#!/usr/bin/env python3
"""
Execute Trading Workflows via n8n Webhook
Handles: CSV input, workflow execution, result processing and saving
"""

import os
import sys
import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from n8n_api_client import N8nConfig, N8nAPIClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingWorkflowExecutor:
    """Execute trading workflows via webhook and manage results"""

    def __init__(self, data_dir: str = "data", reports_dir: str = "reports"):
        """
        Initialize executor

        Args:
            data_dir: Directory for input CSV files
            reports_dir: Directory for output results
        """
        self.data_dir = Path(data_dir)
        self.reports_dir = Path(reports_dir)
        
        # Initialize webhook client
        try:
            config = N8nConfig.from_env()
            self.client = N8nAPIClient(config)
        except ValueError as e:
            logger.error(f"Failed to initialize n8n client: {e}")
            self.client = None
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        logger.info(f"TradingWorkflowExecutor initialized")
        logger.info(f"  Data dir: {self.data_dir}")
        logger.info(f"  Reports dir: {self.reports_dir}")

    def connect(self) -> bool:
        """Connect to n8n webhook"""
        if not self.client:
            return False
        return self.client.test_connection()

    def find_input_csv(self, pattern: Optional[str] = None) -> Optional[Path]:
        """
        Find input CSV file

        Args:
            pattern: Optional file name pattern (e.g., 'BTC_USDT')

        Returns:
            Path to CSV file or None
        """
        # List all CSV files
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if not csv_files:
            logger.warning(f"No CSV files found in {self.data_dir}")
            return None
        
        if pattern:
            # Find file matching pattern
            for f in csv_files:
                if pattern.lower() in f.name.lower():
                    return f
            logger.warning(f"No CSV file matching '{pattern}' found")
            return None
        
        # Return latest file if no pattern
        latest = max(csv_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"Found input file: {latest.name}")
        return latest

    def read_csv_data(self, csv_path: Path) -> Optional[List[Dict[str, Any]]]:
        """
        Read CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            List of rows as dictionaries
        """
        try:
            data = []
            with open(csv_path, 'r') as f:
                reader = csv.DictReader(f)
                data = list(reader)
            
            logger.info(f"Read {len(data)} rows from {csv_path.name}")
            return data
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return None

    def execute_workflow(
        self,
        workflow_name_or_id: str,
        input_csv: Optional[Path] = None,
        wait: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Execute trading workflow via n8n MCP API

        Args:
            workflow_name_or_id: Name or ID of workflow to execute
            input_csv: Optional path to input CSV
            wait: Wait for execution to complete

        Returns:
            Execution result
        """
        if not self.client:
            logger.error("Client not initialized")
            return None
        
        # Find workflow by name or ID
        workflows = self.client.list_workflows()
        workflow = None
        
        for wf in workflows:
            if wf.get('id') == workflow_name_or_id or wf.get('name') == workflow_name_or_id:
                workflow = wf
                break
        
        if not workflow:
            logger.error(f"Workflow '{workflow_name_or_id}' not found")
            return None
        
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name')
        logger.info(f"Found workflow: {workflow_name}")
        
        # Prepare input data
        input_data = {}
        
        if input_csv:
            csv_data = self.read_csv_data(input_csv)
            if csv_data:
                input_data['csv_data'] = csv_data
                input_data['filename'] = input_csv.name
                logger.info(f"Attached CSV data: {len(csv_data)} rows")
        
        # Execute workflow
        logger.info(f"Executing workflow...")
        try:
            response = self.client.execute_workflow(workflow_id, input_data)
            execution_id = response.get('id')
            logger.info(f"✅ Execution triggered: {execution_id}")
            
            # Wait for completion if requested
            if wait:
                logger.info(f"Waiting for execution...")
                execution = self.client.wait_for_execution(execution_id, timeout=300)
                status = execution.get('status')
                logger.info(f"Execution completed: {status}")
                return execution
            
            return response
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return None

    def save_execution_result(
        self,
        execution: Dict[str, Any],
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Save execution result to file

        Args:
            execution: Execution object from n8n
            output_name: Optional custom output file name

        Returns:
            Path to saved file
        """
        if not execution:
            return None
        
        # Generate filename
        if not output_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"execution_{timestamp}.json"
        
        output_path = self.reports_dir / output_name
        
        try:
            with open(output_path, 'w') as f:
                json.dump(execution, f, indent=2, default=str)
            
            logger.info(f"Execution result saved: {output_path}")
            # Optional: upload to GCS if configured
            try:
                upload_to_gcs = os.getenv('UPLOAD_TO_GCS', 'false').lower() == 'true'
                gcs_bucket = os.getenv('GCS_BUCKET')
                if upload_to_gcs and gcs_bucket:
                    from gcs_helper import upload_file_to_gcs
                    gs_path = upload_file_to_gcs(gcs_bucket, str(output_path), output_path.name)
                    logger.info(f"Execution result uploaded to {gs_path}")
            except Exception:
                logger.exception("Failed to optionally upload result to GCS")
            return output_path
        except Exception as e:
            logger.error(f"Failed to save result: {e}")
            return None

    def get_execution_data(self, execution: Dict[str, Any]) -> Optional[Any]:
        """
        Extract execution data/results

        Args:
            execution: Execution object

        Returns:
            Execution output data or None
        """
        # Try different paths where data might be stored
        data = execution.get('data')
        if data:
            return data
        
        # Try result
        result = execution.get('result')
        if result:
            return result
        
        # Try returnData
        return_data = execution.get('returnData')
        if return_data:
            return return_data
        
        return None

    def process_workflow_results(
        self,
        execution: Dict[str, Any],
        workflow_name: str
    ) -> Dict[str, Any]:
        """
        Process and format workflow results

        Args:
            execution: Execution object
            workflow_name: Name of workflow

        Returns:
            Processed results dictionary
        """
        results = {
            'workflow': workflow_name,
            'execution_id': execution.get('id'),
            'status': execution.get('status'),
            'started_at': execution.get('startedAt'),
            'finished_at': execution.get('stoppedAt'),
            'duration_ms': execution.get('duration'),
            'data': self.get_execution_data(execution)
        }
        
        return results


def main():
    """Example usage"""
    load_dotenv()
    
    print("\n🚀 Trading Workflow Executor")
    print("="*60)
    
    executor = TradingWorkflowExecutor()
    
    # Connect
    if not executor.connect():
        return
    
    # List workflows
    print("\n📋 Available Workflows:")
    executor.list_available_workflows()
    
    # Find input CSV
    print("\n📂 Looking for input data...")
    input_csv = executor.find_input_csv()
    
    if input_csv:
        print(f"Found: {input_csv.name}")
        # Optional: Show first few rows
        data = executor.read_csv_data(input_csv)
        if data:
            print(f"  Rows: {len(data)}")
            if len(data) > 0:
                print(f"  Sample row: {data[0]}")
    else:
        print("No input CSV found - workflows can still be executed without data")
    
    print("\n✅ Executor ready!")
    print("Usage: executor.execute_workflow('workflow_name', input_csv)")


if __name__ == '__main__':
    main()
