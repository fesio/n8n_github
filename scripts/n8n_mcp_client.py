#!/usr/bin/env python3
"""
n8n MCP Client - Integration via Model Context Protocol gateway
Uses supergateway to access n8n MCP server endpoint
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class N8nMCPConfig:
    """Configuration for n8n MCP integration"""
    mcp_url: str
    access_token: str
    timeout: int = 30
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'N8nMCPConfig':
        """Load configuration from environment variables"""
        mcp_url = os.getenv('N8N_MCP_URL', 'https://fesu.app.n8n.cloud/mcp-server/http')
        access_token = os.getenv('N8N_ACCESS_TOKEN', '')
        timeout = int(os.getenv('N8N_TIMEOUT', '30'))
        verify_ssl = os.getenv('N8N_VERIFY_SSL', 'true').lower() == 'true'

        if not access_token:
            raise ValueError("N8N_ACCESS_TOKEN environment variable not set")

        return cls(
            mcp_url=mcp_url,
            access_token=access_token,
            timeout=timeout,
            verify_ssl=verify_ssl
        )


class N8nMCPClient:
    """n8n MCP API client - REST API access via MCP gateway"""

    def __init__(self, config: N8nMCPConfig):
        """Initialize MCP client
        
        Args:
            config: N8nMCPConfig instance
        """
        self.config = config
        self.mcp_url = config.mcp_url.rstrip('/')
        self.session = requests.Session()
        self._setup_headers()
        logger.info(f"n8n MCP Client initialized: {self.mcp_url}")

    def _setup_headers(self):
        """Setup authorization headers"""
        self.session.headers.update({
            'Authorization': f'Bearer {self.config.access_token}',
            'Content-Type': 'application/json'
        })

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make MCP request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/api/v1/workflows')
            json_data: Request body
            params: Query parameters
            
        Returns:
            Response JSON
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.mcp_url}/api/v1{endpoint}"
        
        try:
            logger.debug(f"{method} {url}")
            response = self.session.request(
                method=method,
                url=url,
                json=json_data,
                params=params,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"MCP request failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test MCP connection
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing n8n MCP connection...")
            response = self._make_request('GET', '/me')
            logger.info(f"✓ MCP connection successful: {response}")
            return True
        except Exception as e:
            logger.error(f"✗ MCP connection failed: {e}")
            return False

    def list_workflows(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List workflows via MCP
        
        Args:
            limit: Max workflows to return
            offset: Offset for pagination
            
        Returns:
            List of workflow objects
        """
        try:
            logger.info("Listing workflows via MCP...")
            response = self._make_request(
                'GET',
                '/workflows',
                params={'limit': limit, 'offset': offset}
            )
            workflows = response.get('data', [])
            logger.info(f"Retrieved {len(workflows)} workflows")
            return workflows
        except Exception as e:
            logger.error(f"Failed to list workflows: {e}")
            return []

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow details
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow object
        """
        try:
            return self._make_request('GET', f'/workflows/{workflow_id}')
        except Exception as e:
            logger.error(f"Failed to get workflow: {e}")
            return {}

    def execute_workflow(
        self,
        workflow_id: str,
        input_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute workflow via MCP
        
        Args:
            workflow_id: Workflow ID
            input_data: Input data for workflow
            
        Returns:
            Execution response
        """
        try:
            logger.info(f"Executing workflow {workflow_id} via MCP...")
            payload = {'data': input_data or {}}
            response = self._make_request(
                'POST',
                f'/workflows/{workflow_id}/execute',
                json_data=payload
            )
            logger.info(f"Workflow execution triggered: {response}")
            return response
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            raise

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        """Get execution details
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution object
        """
        try:
            return self._make_request('GET', f'/executions/{execution_id}')
        except Exception as e:
            logger.error(f"Failed to get execution: {e}")
            return {}

    def wait_for_execution(
        self,
        execution_id: str,
        timeout: int = 300,
        poll_interval: int = 2
    ) -> Dict[str, Any]:
        """Wait for execution to complete
        
        Args:
            execution_id: Execution ID
            timeout: Max seconds to wait
            poll_interval: Seconds between checks
            
        Returns:
            Final execution object
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            execution = self.get_execution(execution_id)
            status = execution.get('status')
            
            if status in ['success', 'error', 'crashed']:
                logger.info(f"Execution {execution_id} completed: {status}")
                return execution
            
            logger.debug(f"Execution status: {status}")
            time.sleep(poll_interval)
        
        logger.warning(f"Execution timeout after {timeout}s")
        return execution
