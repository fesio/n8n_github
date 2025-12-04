#!/usr/bin/env python3
"""
n8n API Client - Integration with n8n workflows
Handles authentication, workflow execution, and monitoring
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class N8nConfig:
    """Configuration for n8n API connection"""
    base_url: str
    api_key: str
    api_version: str = "v1"
    timeout: int = 30
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'N8nConfig':
        """Load configuration from environment variables"""
        base_url = os.getenv('N8N_BASE_URL', 'http://localhost:5678')
        api_key = os.getenv('N8N_API_KEY', '')
        api_version = os.getenv('N8N_API_VERSION', 'v1')
        timeout = int(os.getenv('N8N_TIMEOUT', '30'))
        verify_ssl = os.getenv('N8N_VERIFY_SSL', 'true').lower() == 'true'

        return cls(
            base_url=base_url,
            api_key=api_key,
            api_version=api_version,
            timeout=timeout,
            verify_ssl=verify_ssl
        )


class N8nAPIClient:
    """
    n8n API Client for workflow management and execution
    Supports: listing workflows, executing workflows, monitoring executions
    """

    def __init__(self, config: N8nConfig):
        """
        Initialize n8n API client

        Args:
            config: N8nConfig object with connection details
        """
        self.config = config
        self.base_url = config.base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())
        logger.info(f"n8n API Client initialized: {self.base_url}/api/{config.api_version}")

    def _get_headers(self) -> Dict[str, str]:
        """Build request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'n8n-python-client/1.0'
        }
        if self.config.api_key:
            headers['X-N8N-API-KEY'] = self.config.api_key
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to n8n API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/workflows')
            data: Request body data
            params: Query parameters

        Returns:
            Response JSON as dictionary
        """
        url = f"{self.base_url}/api/{self.config.api_version}{endpoint}"
        
        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test API connection

        Returns:
            True if connection successful
        """
        try:
            response = self._make_request('GET', '/me')
            logger.info(f"✓ Connected to n8n as: {response.get('email', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"✗ Connection failed: {e}")
            return False

    def list_workflows(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List all workflows

        Args:
            limit: Maximum number of workflows to return
            offset: Number of workflows to skip

        Returns:
            List of workflow objects
        """
        response = self._make_request(
            'GET',
            '/workflows',
            params={'limit': limit, 'offset': offset}
        )
        workflows = response.get('data', [])
        logger.info(f"Retrieved {len(workflows)} workflows")
        return workflows

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get workflow details by ID

        Args:
            workflow_id: n8n workflow ID

        Returns:
            Workflow object with full details
        """
        workflow = self._make_request('GET', f'/workflows/{workflow_id}')
        logger.info(f"Retrieved workflow: {workflow.get('name', workflow_id)}")
        return workflow

    def execute_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow

        Args:
            workflow_id: n8n workflow ID
            data: Input data for the workflow

        Returns:
            Execution result
        """
        payload = {
            'data': data or {}
        }
        result = self._make_request('POST', f'/workflows/{workflow_id}/execute', data=payload)
        logger.info(f"Workflow {workflow_id} executed, ID: {result.get('id', 'unknown')}")
        return result

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Get execution details

        Args:
            execution_id: n8n execution ID

        Returns:
            Execution object with status and results
        """
        execution = self._make_request('GET', f'/executions/{execution_id}')
        status = execution.get('status', 'unknown')
        logger.info(f"Execution {execution_id}: {status}")
        return execution

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List workflow executions

        Args:
            workflow_id: Filter by workflow ID (optional)
            limit: Maximum number of executions to return
            offset: Number of executions to skip

        Returns:
            List of execution objects
        """
        params = {'limit': limit, 'offset': offset}
        if workflow_id:
            endpoint = f'/executions?workflow_id={workflow_id}'
        else:
            endpoint = '/executions'
        
        response = self._make_request('GET', endpoint, params=params)
        executions = response.get('data', [])
        logger.info(f"Retrieved {len(executions)} executions")
        return executions

    def trigger_webhook(
        self,
        workflow_id: str,
        node_name: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger a webhook in a workflow

        Args:
            workflow_id: n8n workflow ID
            node_name: Webhook node name
            data: Data to send to webhook

        Returns:
            Webhook response
        """
        url = f"{self.base_url}/webhook/{workflow_id}/{node_name}"
        try:
            response = requests.post(
                url,
                json=data or {},
                timeout=self.config.timeout,
                verify=self.config.verify_ssl
            )
            response.raise_for_status()
            logger.info(f"Webhook triggered: {workflow_id}/{node_name}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Webhook trigger failed: {e}")
            raise

    def wait_for_execution(
        self,
        execution_id: str,
        max_wait_seconds: int = 300,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """
        Wait for execution to complete

        Args:
            execution_id: n8n execution ID
            max_wait_seconds: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            Final execution object
        """
        import time
        start_time = datetime.now()
        
        while True:
            execution = self.get_execution(execution_id)
            status = execution.get('status')
            
            if status in ['success', 'error', 'crashed']:
                logger.info(f"Execution complete: {status}")
                return execution
            
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait_seconds:
                logger.warning(f"Execution timeout after {elapsed}s")
                return execution
            
            logger.debug(f"Execution status: {status}, waiting...")
            time.sleep(poll_interval)


def main():
    """Example usage of n8n API client"""
    # Load configuration from environment
    config = N8nConfig.from_env()
    
    # Create client
    client = N8nAPIClient(config)
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to n8n API")
        return
    
    # List workflows
    try:
        workflows = client.list_workflows()
        if workflows:
            print("\n📋 Available Workflows:")
            for wf in workflows[:5]:  # Show first 5
                print(f"  - {wf.get('name')} (ID: {wf.get('id')})")
        else:
            print("No workflows found")
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")


if __name__ == '__main__':
    main()
