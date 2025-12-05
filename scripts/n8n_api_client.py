#!/usr/bin/env python3
"""
n8n API Client - Integration with n8n workflows via MCP gateway
Direct access to n8n REST API through the MCP server endpoint
"""

import os
import requests
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class N8nConfig:
    """Configuration for n8n MCP integration"""
    base_url: str
    access_token: str
    timeout: int = 30
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> 'N8nConfig':
        """Load configuration from environment variables"""
        # MCP endpoint is the base URL
        base_url = os.getenv('N8N_MCP_URL', 'https://fesu.app.n8n.cloud/mcp-server/http')
        access_token = os.getenv('N8N_ACCESS_TOKEN', '')
        timeout = int(os.getenv('N8N_TIMEOUT', '30'))
        verify_ssl = os.getenv('N8N_VERIFY_SSL', 'true').lower() == 'true'

        if not access_token:
            raise ValueError("N8N_ACCESS_TOKEN environment variable not set")

        return cls(
            base_url=base_url.rstrip('/'),
            access_token=access_token,
            timeout=timeout,
            verify_ssl=verify_ssl
        )


class N8nAPIClient:
    """n8n REST API client via MCP gateway"""

    def __init__(self, config: N8nConfig):
        """Initialize MCP client
        
        Args:
            config: N8nConfig instance
        """
        self.config = config
        self.base_url = config.base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {config.access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'n8n-python-client/1.0'
        })
        logger.info(f"n8n API Client initialized: {self.base_url}/api/v1")

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make MCP API request
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., '/workflows')
            json_data: Request body
            params: Query parameters
            
        Returns:
            Response JSON
            
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.base_url}/api/v1{endpoint}"
        
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
            
            # Log response details for debugging
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response type: {response.headers.get('content-type')}")
            
            response.raise_for_status()
            
            # Try to parse as JSON
            try:
                return response.json()
            except json.JSONDecodeError:
                logger.warning(f"Response is not JSON (type: {response.headers.get('content-type')})")
                logger.warning(f"Response text: {response.text[:200]}")
                raise ValueError(f"API returned non-JSON response: {response.headers.get('content-type')}")
                
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test MCP connection
        
        Returns:
            True if connection successful
        """
        try:
            logger.info("Testing n8n MCP connection...")
            response = self._make_request('GET', '/me')
            logger.info(f"✓ MCP connection successful")
            return True
        except ValueError as e:
            # This is likely the HTML response issue - log for debugging
            logger.warning(f"Connection returned non-JSON: {e}")
            logger.info("⚠️  MCP endpoint may not expose JSON API directly")
            logger.info("Attempting workaround: checking direct access...")
            return self._check_direct_api_access()
        except Exception as e:
            logger.error(f"✗ MCP connection failed: {e}")
            return False
    
    def _check_direct_api_access(self) -> bool:
        """Check if we can access n8n REST API directly (bypass MCP)"""
        try:
            # Try direct access to n8n API
            base_url = self.base_url.replace('/mcp-server/http', '')
            url = f"{base_url}/api/v1/me"
            logger.info(f"Trying direct API access: {url}")
            
            response = self.session.get(url, timeout=self.config.timeout, verify=self.config.verify_ssl)
            response.raise_for_status()
            
            # Update base_url if direct access works
            self.base_url = base_url
            logger.info("✓ Direct API access successful!")
            return True
        except Exception as e:
            logger.error(f"Direct API access also failed: {e}")
            return False

    def list_workflows(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List workflows
        
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
            logger.info(f"Workflow execution triggered")
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
            
            logger.debug(f"Execution status: {status}, waiting...")
            time.sleep(poll_interval)
        
        logger.warning(f"Execution timeout after {timeout}s")
        return execution


def main():
    """Example usage of n8n API client"""
    # Load configuration from environment
    config = N8nConfig.from_env()
    
    # Create client
    client = N8nAPIClient(config)
    
    # Test connection
    if not client.test_connection():
        logger.error("Failed to connect to n8n MCP")
        return
    
    # List workflows
    try:
        workflows = client.list_workflows(limit=5)
        logger.info(f"Found {len(workflows)} workflows")
        for wf in workflows[:3]:
            logger.info(f"  - {wf.get('name')} (ID: {wf.get('id')})")
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")


if __name__ == '__main__':
    main()
