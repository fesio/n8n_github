# n8n + GitHub Trading Strategy Automation

AI-powered trading strategy generation using n8n workflows and Python ML engine.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- n8n instance (self-hosted or n8n.cloud)
- n8n API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/n8n_github.git
   cd n8n_github
   ```

2. **Create Python virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r scripts/requirements.txt
   ```

4. **Configure n8n API credentials**
   ```bash
   cp .env.example .env
   # Edit .env and add your n8n credentials
   ```

## 📖 Configuration

### Getting n8n API Credentials

1. **Log in to your n8n instance**
   - If using n8n.cloud: https://app.n8n.cloud
   - If self-hosted: http://localhost:5678 (default)

2. **Generate API Key**
   - Click your avatar (top-right)
   - Select "Account Settings"
   - Navigate to "API Tokens"
   - Click "Create New Token"
   - Copy the token

3. **Update .env file**
   ```env
   N8N_BASE_URL=https://yourname.n8n.cloud
   N8N_API_KEY=your_api_key_here
   N8N_API_VERSION=v1
   N8N_TIMEOUT=30
   N8N_VERIFY_SSL=true
   ```

## 🧪 Testing Connection

Test your n8n API configuration:

```bash
python scripts/test_n8n_connection.py
```

Expected output:
```
1️⃣  Testing .env file... ✅
2️⃣  Testing configuration... ✅
3️⃣  Testing API client creation... ✅
4️⃣  Testing API connection... ✅
5️⃣  Testing workflow listing... ✅

✅ All tests passed! n8n API is ready to use.
```

## 📚 Usage Examples

### Example 1: List Available Workflows

```python
from scripts.n8n_integration import N8nIntegration
from dotenv import load_dotenv

load_dotenv()

integration = N8nIntegration()
if integration.connect():
    integration.print_workflows_table()
```

### Example 2: Execute a Workflow

```python
from scripts.n8n_integration import N8nIntegration
from dotenv import load_dotenv

load_dotenv()

integration = N8nIntegration()
integration.connect()

# Execute workflow and wait for completion
result = integration.execute(
    workflow_id='your_workflow_id',
    input_data={'symbol': 'BTC', 'timeframe': '1h'},
    wait=True,
    max_wait=300
)

print(f"Status: {result.get('status')}")
print(f"Data: {result.get('data')}")
```

### Example 3: Execute Trading Workflow with CSV

```python
from scripts.execute_trading_workflow import TradingWorkflowExecutor
from dotenv import load_dotenv

load_dotenv()

executor = TradingWorkflowExecutor()
executor.connect()

# Find input CSV
input_csv = executor.find_input_csv('BTC_USDT')

# Execute workflow
execution = executor.execute_workflow(
    'DailyFeatureSelection',
    input_csv=input_csv,
    wait=True
)

# Save results
executor.save_execution_result(execution, 'trading_result.json')
```

## 🤖 Strategy Agent (Periodic)

The repository includes a small agent that periodically triggers a configured n8n workflow (e.g. a strategy generator), waits for it to complete, and saves results.

Configuration (add to `.env`):

- `WORKFLOW_NAME` or `WORKFLOW_ID` — workflow to trigger (default: `StrategyGenerator`)
- `AGENT_INTERVAL` — seconds between runs (default: `3600`)
- `DRY_RUN` — set to `true` to run the agent locally without contacting n8n (useful for testing)
- `UPLOAD_TO_GCS`, `GCS_BUCKET` — optional: upload saved results to GCS
- `BQ_TABLE` — optional BigQuery table `project.dataset.table` to load tabular results

Run the agent (foreground):

```bash
source .venv/bin/activate
python scripts/strategy_agent.py
```

Run in dry mode (no external credentials required):

```bash
export DRY_RUN=true
python scripts/strategy_agent.py
```

Where results are saved:

- Saved result files go to the `reports/` directory by default.
- A sample result is included at `reports/sample_strategy.json`.

If you set `DRY_RUN=true` the agent will generate a fake execution result and store it locally so you can test the full pipeline without network or credential configuration.


## 📁 Project Structure

```
n8n_github/
├── scripts/
│   ├── n8n_api_client.py          # Low-level API client
│   ├── n8n_integration.py         # High-level integration
│   ├── execute_trading_workflow.py # Trading workflow executor
│   ├── example_n8n_usage.py       # Full usage examples
│   ├── test_n8n_connection.py     # Connection tests
│   └── requirements.txt           # Python dependencies
├── data/                          # Input CSV data
├── reports/                       # Output results & analysis
├── .env                           # Configuration (ignored by git)
├── .env.example                   # Configuration template
└── README.md                      # This file
```

## 🔑 API Client Methods

### N8nAPIClient
- `test_connection()` - Verify API connectivity
- `list_workflows()` - Get all workflows
- `get_workflow(workflow_id)` - Get workflow details
- `execute_workflow(workflow_id, data)` - Execute workflow
- `get_execution(execution_id)` - Get execution status
- `list_executions(workflow_id)` - List executions
- `wait_for_execution(execution_id)` - Wait for completion

### N8nIntegration
- `connect()` - Test connection
- `get_workflows()` - Get workflows with caching
- `find_workflow(name_or_id)` - Search workflows
- `execute()` - Execute with defaults
- `get_execution_status()` - Get status
- `list_recent_executions()` - List recent runs

### TradingWorkflowExecutor
- `connect()` - Connect to n8n
- `list_available_workflows()` - Display workflows
- `find_input_csv()` - Locate CSV files
- `read_csv_data()` - Read CSV data
- `execute_workflow()` - Execute with CSV
- `save_execution_result()` - Save results
- `process_workflow_results()` - Format results

## 🐛 Troubleshooting

### "Connection failed" error

1. Check N8N_BASE_URL is correct
   ```bash
   curl https://yourname.n8n.cloud/api/v1/me -H "X-N8N-API-KEY: your_key"
   ```

2. Verify API key is valid
   - Regenerate in n8n → Account Settings → API Tokens

3. Check firewall/network access
   - Ensure n8n instance is accessible

### "Workflow not found" error

1. List available workflows
   ```bash
   python scripts/n8n_integration.py
   ```

2. Use exact workflow ID from list
   - Format: "123456" or "abcdef123456"

### Timeout errors

Increase timeout in .env:
```env
N8N_TIMEOUT=60
N8N_MAX_WAIT_SECONDS=600
```

## 📝 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `N8N_BASE_URL` | `http://localhost:5678` | n8n instance URL |
| `N8N_API_KEY` | `` | API authentication token |
| `N8N_API_VERSION` | `v1` | API version |
| `N8N_TIMEOUT` | `30` | Request timeout (seconds) |
| `N8N_VERIFY_SSL` | `true` | Verify SSL certificates |
| `N8N_MAX_WAIT_SECONDS` | `300` | Max execution wait time |
| `N8N_POLL_INTERVAL` | `2` | Status check interval (seconds) |

## 📚 Documentation

- [n8n Documentation](https://docs.n8n.io/)
- [n8n API Reference](https://docs.n8n.io/api/api-reference/)
- [Trading Strategy Guide](./n8n_github_guide.md)
- [Quick Start (60 min)](./quickstart_60min.md)

## 📄 License

MIT

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Test with `python scripts/test_n8n_connection.py`
4. Submit a pull request

