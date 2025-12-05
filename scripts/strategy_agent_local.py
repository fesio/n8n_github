#!/usr/bin/env python3
"""
Trading Strategy Agent - Local Implementation
Generates trading strategies without requiring n8n API access
"""

import time
import os
import signal
import logging
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import sys

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

STOP = False

def handle_signal(sig, frame):
    global STOP
    logger.info(f"Received signal {sig}; stopping agent gracefully...")
    STOP = True


signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


def generate_strategy_result() -> dict:
    """Generate a sample trading strategy result"""
    return {
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "strategies": [
            {
                "name": "Mean Reversion",
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "score": 0.82,
                "signal": "BUY",
                "confidence": 0.78
            },
            {
                "name": "Momentum",
                "symbol": "ETH/USDT",
                "timeframe": "4h",
                "score": 0.71,
                "signal": "HOLD",
                "confidence": 0.65
            },
            {
                "name": "RSI Divergence",
                "symbol": "XRP/USDT",
                "timeframe": "1h",
                "score": 0.68,
                "signal": "SELL",
                "confidence": 0.70
            }
        ]
    }


def save_result(result: dict, reports_dir: str = "reports") -> Path:
    """Save strategy result to file"""
    reports_path = Path(reports_dir)
    reports_path.mkdir(exist_ok=True)
    
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"strategy_execution_{timestamp}.json"
    filepath = reports_path / filename
    
    with open(filepath, 'w') as f:
        json.dump(result, f, indent=2)
    
    logger.info(f"Saved result to {filepath}")
    return filepath


def evaluate_and_notify(result: dict) -> None:
    """Evaluate results and send notifications if thresholds exceeded"""
    threshold = float(os.getenv('NOTIFY_SCORE_THRESHOLD', '0.75'))
    
    for strategy in result.get('strategies', []):
        score = strategy.get('score', 0)
        if score >= threshold:
            signal_type = strategy.get('signal', 'N/A')
            symbol = strategy.get('symbol', 'N/A')
            name = strategy.get('name', 'Unknown')
            logger.warning(f"🚨 ALERT: {name} ({symbol}) score={score} signal={signal_type}")
            
            # Try to send notifications
            try:
                from notify import notify_slack, notify_email
                message = f"Strategy Alert: {name} for {symbol} - Score: {score} - Signal: {signal_type}"
                notify_slack(message)
                notify_email(f"Trading Alert: {name}", message)
                logger.info("Notification sent")
            except Exception as e:
                logger.debug(f"Could not send notification: {e}")


def main():
    load_dotenv()
    
    interval = int(os.getenv('AGENT_INTERVAL', '3600'))
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    logger.info("🤖 Trading Strategy Agent Started")
    logger.info(f"   Interval: {interval}s")
    logger.info(f"   Dry Run: {dry_run}")
    
    run_count = 0
    
    while not STOP:
        run_count += 1
        logger.info(f"\n📊 Agent Run #{run_count}")
        logger.info("=" * 60)
        
        try:
            # Generate strategy
            logger.info("Generating trading strategies...")
            result = generate_strategy_result()
            logger.info(f"Generated {len(result['strategies'])} strategies")
            
            # Save result
            logger.info("Saving results...")
            filepath = save_result(result)
            
            # Evaluate and notify
            logger.info("Evaluating results...")
            evaluate_and_notify(result)
            
            logger.info("✅ Run completed successfully")
            
        except Exception as e:
            logger.exception(f"❌ Run failed: {e}")
        
        # Sleep until next run or exit
        logger.info(f"Waiting {interval}s until next run...")
        slept = 0
        while slept < interval and not STOP:
            time.sleep(1)
            slept += 1
    
    logger.info("\n✅ Agent stopped gracefully")


if __name__ == '__main__':
    main()
