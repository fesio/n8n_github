#!/usr/bin/env python3
"""
Example usage of n8n API Client
Demonstrates: connecting, listing workflows, executing, monitoring
"""

import os
from dotenv import load_dotenv
import logging

# Import the n8n API client
from n8n_api_client import N8nAPIClient, N8nConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_test_connection():
    """Example 1: Test connection to n8n API"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Test n8n API Connection")
    print("="*60)
    
    config = N8nConfig.from_env()
    client = N8nAPIClient(config)
    
    success = client.test_connection()
    if success:
        print("✅ Successfully connected to n8n API!")
    else:
        print("❌ Failed to connect. Check N8N_BASE_URL and N8N_API_KEY in .env")
    
    return client if success else None


def example_2_list_workflows(client):
    """Example 2: List all available workflows"""
    print("\n" + "="*60)
    print("EXAMPLE 2: List All Workflows")
    print("="*60)
    
    try:
        workflows = client.list_workflows(limit=10)
        
        if not workflows:
            print("No workflows found in this n8n instance.")
            return None
        
        print(f"\n📋 Found {len(workflows)} workflow(s):\n")
        for i, wf in enumerate(workflows, 1):
            print(f"  {i}. {wf.get('name')}")
            print(f"     ID: {wf.get('id')}")
            print(f"     Active: {wf.get('active', False)}")
            print()
        
        return workflows[0] if workflows else None
    
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        return None


def example_3_get_workflow_details(client, workflow_id):
    """Example 3: Get detailed information about a specific workflow"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Get Workflow Details")
    print("="*60)
    
    try:
        workflow = client.get_workflow(workflow_id)
        
        print(f"\n📌 Workflow Details:")
        print(f"  Name: {workflow.get('name')}")
        print(f"  ID: {workflow.get('id')}")
        print(f"  Active: {workflow.get('active', False)}")
        print(f"  Created: {workflow.get('createdAt', 'N/A')}")
        print(f"  Updated: {workflow.get('updatedAt', 'N/A')}")
        
        nodes = workflow.get('nodes', [])
        if nodes:
            print(f"\n  📍 Nodes ({len(nodes)}):")
            for node in nodes[:5]:  # Show first 5 nodes
                print(f"    - {node.get('name')} ({node.get('type')})")
        
        return workflow
    
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        return None


def example_4_execute_workflow(client, workflow_id):
    """Example 4: Execute a workflow with input data"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Execute Workflow")
    print("="*60)
    
    try:
        # Sample input data for the workflow
        input_data = {
            'symbol': 'BTC',
            'timeframe': '1h',
            'limit': 100
        }
        
        print(f"\n▶️  Executing workflow: {workflow_id}")
        print(f"   Input data: {input_data}\n")
        
        result = client.execute_workflow(workflow_id, input_data)
        
        execution_id = result.get('id')
        print(f"✅ Workflow execution started!")
        print(f"   Execution ID: {execution_id}")
        
        return execution_id
    
    except Exception as e:
        logger.error(f"Error executing workflow: {e}")
        return None


def example_5_monitor_execution(client, execution_id):
    """Example 5: Monitor workflow execution status"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Monitor Execution")
    print("="*60)
    
    try:
        print(f"\n⏳ Waiting for execution {execution_id} to complete...")
        
        execution = client.wait_for_execution(
            execution_id,
            max_wait_seconds=60,
            poll_interval=2
        )
        
        status = execution.get('status')
        print(f"\n✅ Execution finished with status: {status}")
        print(f"   Started: {execution.get('startedAt', 'N/A')}")
        print(f"   Finished: {execution.get('stoppedAt', 'N/A')}")
        
        # Show execution data if available
        execution_data = execution.get('data', {})
        if execution_data:
            print(f"\n📊 Execution Data:")
            print(f"   {execution_data}")
        
        return execution
    
    except Exception as e:
        logger.error(f"Error monitoring execution: {e}")
        return None


def example_6_list_executions(client, workflow_id=None):
    """Example 6: List recent workflow executions"""
    print("\n" + "="*60)
    print("EXAMPLE 6: List Executions")
    print("="*60)
    
    try:
        filter_text = f" for workflow {workflow_id}" if workflow_id else ""
        print(f"\n📋 Listing recent executions{filter_text}...\n")
        
        executions = client.list_executions(
            workflow_id=workflow_id,
            limit=10
        )
        
        if not executions:
            print("No executions found.")
            return
        
        print(f"Found {len(executions)} execution(s):\n")
        for i, exec in enumerate(executions[:5], 1):
            print(f"  {i}. ID: {exec.get('id')}")
            print(f"     Status: {exec.get('status')}")
            print(f"     Started: {exec.get('startedAt', 'N/A')}")
            print()
    
    except Exception as e:
        logger.error(f"Error listing executions: {e}")


def main():
    """Run all examples"""
    # Load environment variables from .env
    load_dotenv()
    
    print("\n🚀 n8n API Client Examples")
    print("=" * 60)
    print("This script demonstrates the n8n Python API client")
    print("=" * 60)
    
    # Example 1: Test connection
    client = example_1_test_connection()
    if not client:
        print("\n❌ Cannot proceed without a valid connection.")
        print("Please check your .env file and n8n instance.")
        return
    
    # Example 2: List workflows
    workflows = example_2_list_workflows(client)
    if not workflows:
        print("\n⚠️  No workflows available to demonstrate.")
        print("Create a workflow in n8n first.")
        return
    
    # Use first workflow for remaining examples
    workflow = workflows[0]
    workflow_id = workflow.get('id')
    workflow_name = workflow.get('name')
    
    print(f"\n🎯 Using workflow: {workflow_name}")
    
    # Example 3: Get workflow details
    example_3_get_workflow_details(client, workflow_id)
    
    # Example 4: Execute workflow
    execution_id = example_4_execute_workflow(client, workflow_id)
    if execution_id:
        # Example 5: Monitor execution
        example_5_monitor_execution(client, execution_id)
    
    # Example 6: List executions
    example_6_list_executions(client, workflow_id)
    
    print("\n" + "="*60)
    print("✅ Examples completed!")
    print("="*60)


if __name__ == '__main__':
    main()
