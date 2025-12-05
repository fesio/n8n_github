#!/usr/bin/env python3
"""
Test n8n MCP Connection
Validates that the MCP gateway is reachable and accessible
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


def main():
    """Run MCP connection tests"""
    # Load environment
    load_dotenv()
    
    print("\n🧪 n8n MCP Connection Tests")
    print("=" * 60)
    
    try:
        # Test 1: Load configuration
        print("1️⃣  Loading configuration...")
        config = N8nConfig.from_env()
        print(f"   ✅ Base URL: {config.base_url}")
        print(f"   ✅ Access Token: {'*' * 20}...")
        print(f"   ✅ Timeout: {config.timeout}s")
        
        # Test 2: Create client
        print("\n2️⃣  Creating MCP client...")
        client = N8nAPIClient(config)
        print("   ✅ Client created successfully")
        
        # Test 3: Test MCP connection
        print("\n3️⃣  Testing MCP connection...")
        if client.test_connection():
            print("   ✅ MCP gateway is accessible")
        else:
            print("   ❌ MCP connection failed")
            return False
        
        # Test 4: List workflows
        print("\n4️⃣  Listing workflows...")
        workflows = client.list_workflows(limit=10)
        print(f"   ✅ Found {len(workflows)} workflow(s)")
        if workflows:
            for wf in workflows[:3]:
                name = wf.get('name', 'Unknown')
                wf_id = wf.get('id', 'N/A')[:12]
                active = "✓" if wf.get('active') else " "
                print(f"      [{active}] {name} (ID: {wf_id}...)")
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\n✨ Your n8n MCP connection is working!")
        print("\n📝 Next steps:")
        print("  1. Run: python scripts/strategy_agent.py")
        print("  2. Monitor n8n for workflow executions")
        
        return True
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Verify N8N_MCP_URL is set in .env")
        print("  2. Verify N8N_ACCESS_TOKEN is set in .env")
        print("  3. Check token format (should be JWT)")
        return False
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n" + "=" * 60)
        print("❌ CONNECTION FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Verify N8N_MCP_URL is correct")
        print("  2. Verify N8N_ACCESS_TOKEN is valid")
        print("  3. Check your n8n Cloud instance is accessible")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
