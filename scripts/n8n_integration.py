#!/usr/bin/env python3
"""
n8n Integration Module
Main module for integrating with n8n workflows and managing executions
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from n8n_api_client import N8nAPIClient, N8nConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class N8nIntegration:
    """
    High-level n8n integration for trading strategy automation
    """

    def __init__(self, config: Optional[N8nConfig] = None):
        """Initialize n8n integration"""
        if config is None:
            config = N8nConfig.from_env()
        
        self.config = config
        self.client = N8nAPIClient(config)
        self.workflows_cache: Optional[List[Dict[str, Any]]] = None
        logger.info("N8nIntegration initialized")

    def connect(self) -> bool:
        """
        Test and establish connection to n8n

        Returns:
            True if connection successful
        """
        logger.info("Connecting to n8n API...")
        success = self.client.test_connection()
        
        if success:
            logger.info("✅ Successfully connected to n8n")
        else:
            logger.error("❌ Failed to connect to n8n")
            logger.error("Check N8N_BASE_URL and N8N_API_KEY in .env file")
        
        return success

    def get_workflows(self, refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Get list of available workflows

        Args:
            refresh: Force refresh from API (ignore cache)

        Returns:
            List of workflow objects
        """
        if self.workflows_cache and not refresh:
            logger.debug(f"Using cached workflows ({len(self.workflows_cache)} items)")
            return self.workflows_cache
        
        logger.info("Fetching workflows from n8n...")
        try:
            workflows = self.client.list_workflows(limit=100)
            self.workflows_cache = workflows
            logger.info(f"✅ Retrieved {len(workflows)} workflows")
            return workflows
        except Exception as e:
            logger.error(f"Failed to fetch workflows: {e}")
            return []

    def find_workflow(self, name_or_id: str) -> Optional[Dict[str, Any]]:
        """
        Find workflow by name or ID

        Args:
            name_or_id: Workflow name or ID

        Returns:
            Workflow object or None
        """
        workflows = self.get_workflows()
        
        # Try exact ID match first
        for wf in workflows:
            if wf.get('id') == name_or_id:
                return wf
        
        # Try name match
        for wf in workflows:
            if wf.get('name', '').lower() == name_or_id.lower():
                return wf
        
        # Try partial name match
        for wf in workflows:
            if name_or_id.lower() in wf.get('name', '').lower():
                return wf
        
        logger.warning(f"Workflow '{name_or_id}' not found")
        return None

    def execute(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
        wait: bool = True,
        max_wait: int = 300
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a workflow

        Args:
            workflow_id: Workflow ID
            input_data: Input data for workflow
            wait: Wait for execution to complete
            max_wait: Maximum seconds to wait

        Returns:
            Execution result or None if failed
        """
        logger.info(f"Executing workflow: {workflow_id}")
        
        try:
            # Execute workflow
            result = self.client.execute_workflow(workflow_id, input_data or {})
            execution_id = result.get('id')
            
            if not execution_id:
                logger.error("No execution ID returned")
                return None
            
            logger.info(f"✅ Execution started: {execution_id}")
            
            # Wait for completion if requested
            if wait:
                logger.info(f"Waiting for execution (max {max_wait}s)...")
                execution = self.client.wait_for_execution(
                    execution_id,
                    max_wait_seconds=max_wait,
                    poll_interval=2
                )
                
                status = execution.get('status')
                logger.info(f"Execution {execution_id} completed with status: {status}")
                
                return execution
            else:
                return result
        
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return None

    def get_execution_status(self, execution_id: str) -> Optional[str]:
        """
        Get execution status

        Args:
            execution_id: Execution ID

        Returns:
            Status string (success, error, running, etc.)
        """
        try:
            execution = self.client.get_execution(execution_id)
            return execution.get('status')
        except Exception as e:
            logger.error(f"Failed to get execution status: {e}")
            return None

    def list_recent_executions(self, workflow_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent executions

        Args:
            workflow_id: Filter by workflow (optional)
            limit: Number of executions to return

        Returns:
            List of execution objects
        """
        try:
            executions = self.client.list_executions(workflow_id=workflow_id, limit=limit)
            logger.info(f"Retrieved {len(executions)} recent executions")
            return executions
        except Exception as e:
            logger.error(f"Failed to list executions: {e}")
            return []

    def print_workflows_table(self):
        """Print workflows in a nice table format"""
        workflows = self.get_workflows()
        
        if not workflows:
            print("No workflows found")
            return
        
        print("\n" + "="*80)
        print("AVAILABLE WORKFLOWS")
        print("="*80)
        print(f"{'Name':<30} {'ID':<20} {'Active':<10} {'Created':<15}")
        print("-"*80)
        
        for wf in workflows[:20]:  # Show first 20
            name = wf.get('name', 'N/A')[:29]
            wf_id = wf.get('id', 'N/A')[:19]
            active = "✓" if wf.get('active') else " "
            created = wf.get('createdAt', 'N/A')[:14]
            
            print(f"{name:<30} {wf_id:<20} {active:<10} {created:<15}")
        
        if len(workflows) > 20:
            print(f"... and {len(workflows) - 20} more")
        print("="*80 + "\n")


def main():
    """Demo usage of n8n integration"""
    # Load environment variables
    load_dotenv()
    
    print("\n🚀 n8n Integration Demo")
    print("="*60)
    
    # Initialize integration
    integration = N8nIntegration()
    
    # Test connection
    if not integration.connect():
        print("Cannot proceed without connection")
        return
    
    # List workflows
    integration.print_workflows_table()
    
    # Example: Get specific workflow
    workflows = integration.get_workflows()
    if workflows:
        first_wf = workflows[0]
        print(f"📌 First workflow: {first_wf.get('name')}")
        print(f"   ID: {first_wf.get('id')}")
        print(f"   Active: {first_wf.get('active')}")
    
    print("\n✅ Integration ready!")
    print("Use the N8nIntegration class to execute workflows:")
    print("  integration.execute(workflow_id, input_data)")


if __name__ == '__main__':
    main()
