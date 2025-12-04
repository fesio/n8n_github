#!/usr/bin/env python3
"""
Strategy Agent

Periodically triggers a configured n8n workflow (strategy generator), waits for completion,
stores results and optionally uploads them to GCS/BigQuery using helper modules.

Configure via environment variables in `.env`:
- WORKFLOW_NAME or WORKFLOW_ID: which workflow to trigger
- AGENT_INTERVAL: seconds between runs (default 3600 = 1 hour)
- UPLOAD_TO_GCS, GCS_BUCKET: optional upload
- BQ_TABLE: optional BigQuery table id to load results (project.dataset.table)

Run:
    source .venv/bin/activate
    python scripts/strategy_agent.py

Note: requires `N8N_BASE_URL` and `N8N_API_KEY` in `.env`.
"""

import time
import os
import signal
import logging
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

# Ensure scripts package path is available
import sys
sys.path.insert(0, str(Path(__file__).parent))

from execute_trading_workflow import TradingWorkflowExecutor
from notify import notify_slack, notify_email

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STOP = False

def handle_signal(sig, frame):
    global STOP
    logger.info(f"Received signal {sig}; stopping agent gracefully...")
    STOP = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def run_once(executor: TradingWorkflowExecutor, workflow_name_or_id: str):
    """Trigger the workflow, wait for execution and save results"""
    logger.info(f"Agent run: triggering workflow '{workflow_name_or_id}'")

    # Support DRY_RUN mode for testing without external services
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    if dry_run:
        logger.info("DRY_RUN enabled — generating fake execution result")
        # Create a fake execution result similar to n8n's structure
        timestamp = datetime.utcnow().isoformat() + 'Z'
        fake_execution = {
            'id': f"dryrun-{int(time.time())}",
            'status': 'success',
            'startedAt': timestamp,
            'stoppedAt': timestamp,
            'duration': 0,
            'data': [
                {'strategy': 'mean_reversion', 'symbol': 'BTC_USDT', 'score': 0.78},
                {'strategy': 'momentum', 'symbol': 'ETH_USDT', 'score': 0.65}
            ]
        }
        execution = fake_execution
    else:
        # Try to find and execute
        execution = executor.execute_workflow(workflow_name_or_id, wait=True)
        if not execution:
            logger.error("Execution failed or returned no data")
            return False

    # Save execution result locally and (optionally) upload via executor
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    out_name = f"strategy_execution_{timestamp}.json"
    saved = executor.save_execution_result(execution, out_name)
    if saved:
        logger.info(f"Saved execution result to {saved}")
    else:
        logger.error("Failed to save execution result")

    # Optional BigQuery load
    bq_table = os.getenv('BQ_TABLE')
    if bq_table:
        try:
            from bq_helper import load_dataframe_to_bq
            # Try to extract tabular data; if execution contains JSON array of rows, load
            data = executor.get_execution_data(execution)
            import pandas as pd
            if isinstance(data, list) and data:
                df = pd.DataFrame(data)
                rows = load_dataframe_to_bq(df, bq_table)
                logger.info(f"Loaded {rows} rows into BigQuery table {bq_table}")
            else:
                logger.warning("Execution data not a list or empty; skipping BQ load")
        except Exception as e:
            logger.exception(f"BigQuery load failed: {e}")

    # Evaluate results for notification
    try:
        threshold = float(os.getenv('NOTIFY_SCORE_THRESHOLD', '0.75'))
        data = executor.get_execution_data(execution)
        if isinstance(data, list):
            for row in data:
                score = None
                # Support keys 'score' or 'confidence'
                if isinstance(row, dict):
                    score = row.get('score') or row.get('confidence')
                try:
                    if score is not None and float(score) >= threshold:
                        # Build message
                        strategy_name = row.get('strategy') if isinstance(row, dict) else str(row)
                        symbol = row.get('symbol') if isinstance(row, dict) else 'n/a'
                        message = (
                            f"Strategy passed threshold: {strategy_name} for {symbol} — score={score} (threshold={threshold})"
                        )
                        notify_slack(message)
                        notify_email(f"Strategy Alert: {strategy_name}", message)
                        logger.info("Notification sent for strategy %s (score=%s)", strategy_name, score)
                except Exception:
                    logger.exception("Error evaluating row for notification: %s", row)
    except Exception:
        logger.exception("Failed to evaluate execution result for notifications")

    return True


def main():
    load_dotenv()

    interval = int(os.getenv('AGENT_INTERVAL', '3600'))
    workflow = os.getenv('WORKFLOW_NAME') or os.getenv('WORKFLOW_ID') or 'StrategyGenerator'

    executor = TradingWorkflowExecutor()
    # If DRY_RUN is set, skip attempting to connect to n8n
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    if dry_run:
        logger.info('DRY_RUN enabled — skipping n8n connection')
    else:
        # Ensure connection
        if not executor.connect():
            logger.error('Cannot connect to n8n; aborting agent startup')
            return

    logger.info(f"Starting Strategy Agent: workflow={workflow}, interval={interval}s")

    # Initial run immediately
    while not STOP:
        try:
            run_once(executor, workflow)
        except Exception as e:
            logger.exception(f"Agent run error: {e}")

        # Sleep until next run or exit
        slept = 0
        while slept < interval and not STOP:
            time.sleep(1)
            slept += 1

    logger.info("Agent stopped")


if __name__ == '__main__':
    main()
