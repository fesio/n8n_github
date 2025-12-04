#!/usr/bin/env python3
"""
Test n8n API Connection
Validates configuration and connectivity
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from n8n_api_client import N8nConfig, N8nAPIClient

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class N8nConnectionTester:
    """Test n8n API connection and configuration"""

    def __init__(self):
        """Initialize tester"""
        self.config: Optional[N8nConfig] = None
        self.client: Optional[N8nAPIClient] = None
        self.results = {}

    def test_env_loaded(self) -> bool:
        """Test if .env file is properly loaded"""
        logger.info("1️⃣  Testing .env file...")
        
        base_url = os.getenv('N8N_BASE_URL')
        api_key = os.getenv('N8N_API_KEY')
        
        if not base_url:
            logger.error("   ❌ N8N_BASE_URL not set")
            self.results['env_loaded'] = False
            return False
        
        if not api_key or api_key == 'replace_with_your_api_key_here':
            logger.error("   ❌ N8N_API_KEY not set or using default")
            self.results['env_loaded'] = False
            return False
        
        logger.info(f"   ✅ N8N_BASE_URL: {base_url}")
        logger.info(f"   ✅ N8N_API_KEY: {'*' * 10}... (hidden)")
        self.results['env_loaded'] = True
        return True

    def test_config_creation(self) -> bool:
        """Test if config can be created"""
        logger.info("2️⃣  Testing configuration...")
        
        try:
            self.config = N8nConfig.from_env()
            logger.info(f"   ✅ Config created")
            logger.info(f"     Base URL: {self.config.base_url}")
            logger.info(f"     API Version: {self.config.api_version}")
            logger.info(f"     Timeout: {self.config.timeout}s")
            logger.info(f"     SSL Verify: {self.config.verify_ssl}")
            self.results['config_created'] = True
            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to create config: {e}")
            self.results['config_created'] = False
            return False

    def test_client_creation(self) -> bool:
        """Test if API client can be created"""
        logger.info("3️⃣  Testing API client creation...")
        
        if not self.config:
            logger.error("   ❌ Config not initialized")
            self.results['client_created'] = False
            return False
        
        try:
            self.client = N8nAPIClient(self.config)
            logger.info("   ✅ API client created")
            self.results['client_created'] = True
            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to create client: {e}")
            self.results['client_created'] = False
            return False

    def test_api_connection(self) -> bool:
        """Test actual API connection"""
        logger.info("4️⃣  Testing API connection...")
        
        if not self.client:
            logger.error("   ❌ Client not initialized")
            self.results['api_connection'] = False
            return False
        
        try:
            success = self.client.test_connection()
            if success:
                logger.info("   ✅ API connection successful")
                self.results['api_connection'] = True
                return True
            else:
                logger.error("   ❌ API connection failed")
                self.results['api_connection'] = False
                return False
        except Exception as e:
            logger.error(f"   ❌ Connection test error: {e}")
            self.results['api_connection'] = False
            return False

    def test_list_workflows(self) -> bool:
        """Test listing workflows"""
        logger.info("5️⃣  Testing workflow listing...")
        
        if not self.client:
            logger.error("   ❌ Client not initialized")
            self.results['list_workflows'] = False
            return False
        
        try:
            workflows = self.client.list_workflows(limit=5)
            count = len(workflows)
            logger.info(f"   ✅ Retrieved {count} workflow(s)")
            
            if count > 0:
                logger.info("   Sample workflows:")
                for wf in workflows[:3]:
                    logger.info(f"     - {wf.get('name')} (ID: {wf.get('id')})")
            
            self.results['list_workflows'] = True
            self.results['workflow_count'] = count
            return True
        except Exception as e:
            logger.error(f"   ❌ Failed to list workflows: {e}")
            self.results['list_workflows'] = False
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        all_passed = all(
            v for k, v in self.results.items()
            if k not in ['workflow_count']
        )
        
        for test, result in self.results.items():
            if test == 'workflow_count':
                continue
            
            status = "✅ PASS" if result else "❌ FAIL"
            test_name = test.replace('_', ' ').title()
            print(f"{test_name:<30} {status}")
        
        if 'workflow_count' in self.results:
            count = self.results['workflow_count']
            print(f"{'Workflows Found':<30} {count}")
        
        print("="*60)
        
        if all_passed:
            print("✅ All tests passed! n8n API is ready to use.")
        else:
            print("❌ Some tests failed. Check your configuration.")
        
        return all_passed

    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("\n🧪 n8n Connection Tests")
        print("="*60)
        
        # Run tests in sequence
        tests = [
            self.test_env_loaded,
            self.test_config_creation,
            self.test_client_creation,
            self.test_api_connection,
            self.test_list_workflows
        ]
        
        results = []
        for test in tests:
            try:
                results.append(test())
            except Exception as e:
                logger.error(f"Test error: {e}")
                results.append(False)
        
        # Print summary
        all_passed = self.print_summary()
        
        return all_passed


def main():
    """Run connection tests"""
    # Load environment
    load_dotenv()
    
    # Run tests
    tester = N8nConnectionTester()
    success = tester.run_all_tests()
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
