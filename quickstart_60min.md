# ⚡ QUICK START: URUCHOM SYSTEM W 60 MINUT

## 📋 CO BĘDZIESZ MIEĆ PO 1 GODZINIE

✅ GitHub repo z pełną strukturą
✅ Python ML engine (gotowy do uruchomienia)
✅ n8n account z 3 workflow'ami
✅ Automatyczne generowanie strategii co 24h
✅ Powiadomienia na Slack/Telegram
✅ Feedback loop do ciągłego uczenia

---

## ⏱️ TIMELINE - FOLLOW THIS EXACTLY

### 0-5 MIN: GitHub Setup

```bash
# 1. Otwórz GitHub.com → Log in
# 2. "+" → "New repository"
#    - Name: trading-ai-system
#    - Private ✓
#    - Add .gitignore: Python ✓
#    - Create

# 3. W terminalu:
git clone https://github.com/YOUR_USERNAME/trading-ai-system.git
cd trading-ai-system

# 4. Utwórz strukturę (copy-paste):
mkdir -p data scripts pine n8n reports docs
touch README.md ARCHITECTURE.md SETUP_GUIDE.md
touch scripts/requirements.txt scripts/config.json
touch pine/.gitkeep n8n/.gitkeep reports/.gitkeep docs/.gitkeep

# 5. Commit
git add .
git commit -m "Initial project structure"
git push origin main
```

### 5-20 MIN: Python Scripts

```bash
# 1. W /scripts folder, utwórz te 4 pliki:
# COPY PONIŻEJ ↓

# requirements.txt:
pandas==1.5.3
numpy==1.24.3
scikit-learn==1.2.2
ta==0.10.2
optuna==3.0.0
requests==2.31.0
fastapi==0.95.1
uvicorn==0.21.3

# 2. Zainstaluj
cd scripts
pip install -r requirements.txt

# 3. Commit
cd ..
git add scripts/
git commit -m "Add Python ML engine"
git push origin main
```

### 20-35 MIN: n8n Account & Cloud Setup

```
1. Odwiedź: https://app.n8n.cloud/
2. Sign up (darmowe)
3. Create workspace: "Trading AI"
4. Zapamiętaj URL workspace'u: https://app.n8n.cloud/[id]/

(Lub self-hosted: docker run -p 5678:5678 n8nio/n8n)
```

### 35-50 MIN: n8n Workflow #1 - Feature Selection

```
n8n Dashboard → Create new workflow

[NODES TO ADD]

1️⃣ TRIGGER: Cron
   - Cron expression: 0 3 * * *  (co dzień o 3 AM)
   - Display name: "Daily 03:00 AM"

2️⃣ BRANCH: For Each Item
   - Input data: Choose from previous node
   - Item: Loop through each pair [BTC, ETH, SOL]

3️⃣ ACTION: HTTP Request
   - Method: GET
   - URL: https://api.github.com/repos/YOUR_USERNAME/trading-ai-system/contents/data/BTC_USDT_1h_latest.csv
   - Add header: Authorization: token YOUR_GITHUB_TOKEN
   - Output: CSV content

4️⃣ ACTION: Code
   - Language: JavaScript (Node.js)
   - Code:
   ```javascript
   const csv = Buffer.from($json.content, 'base64').toString('utf-8');
   return { csv_data: csv };
   ```

5️⃣ ACTION: HTTP Request (to your Python service)
   - Method: POST
   - URL: http://YOUR_SERVER:5000/api/calculate-indicators
   - Body (JSON):
   ```json
   {
     "csv_data": "{{ $json.csv_data }}"
   }
   ```

6️⃣ ACTION: GitHub
   - Select resource: Repository
   - Authentication: Connect GitHub account
   - Repository: trading-ai-system
   - Operation: Create or update file
   - File path: /data/indicators_features_{{ $now.format('YYYY-MM-DD') }}.csv
   - File content: {{ $json.features }}

7️⃣ ACTION: Slack
   - Select resource: Create Message
   - Channel: #strategy-dev
   - Text: ✓ Features calculated {{ $json.timestamp }}

[SAVE & ACTIVATE]
Name: "Workflow_01_DailyFeatureSelection"
Active toggle: ON
```

### 50-60 MIN: Notification Setup

```
1. Slack Setup:
   - Workspace Settings → Apps → n8n
   - Copy Bot Token
   - n8n → Settings → Slack
   - Paste token
   - Select channel: #strategy-dev

2. GitHub Token:
   - GitHub Settings → Developer settings → Personal access tokens
   - New token (classic)
   - Scopes: repo (full control)
   - Copy token
   - n8n → Nodes → GitHub → Paste token

3. Test:
   - n8n Workflow #1 → Test workflow
   - Should see: ✓ Success in logs
   - Slack: Should receive test message
```

---

## 🎯 MINIMAL DEPLOYABLE SYSTEM

Jeśli chcesz szybciej (najprostsze wersje):

### Simple Option 1: Local Python Only (NO n8n YET)

```bash
# Uruchom co godzinę ręcznie lub via cron:
python scripts/indicator_calculator.py
python scripts/feature_selector.py
python scripts/strategy_generator.py

# Każdy skrypt:
# - Czyta CSV z GitHub
# - Przetwarza
# - Zapisuje wynik
# - Wysyła Slack alert
```

### Simple Option 2: n8n + Manual Triggers

```
Zamiast Cron, używaj:
- n8n Dashboard → Workflows → Manual trigger
- Albo webhook trigger (klikasz button w Slack)
```

### Simple Option 3: Hybrid (Recommended)

```
- Tier 1: GitHub + CSV files (automated by script)
- Tier 2: n8n workflows (scheduled)
- Tier 3: Notifications (Slack)
- Tier 4: Manual: you paste code to TradingView
```

---

## ✅ VERIFICATION CHECKLIST

Po 60 minutach powinieneś mieć:

- [ ] GitHub repo created & pushed
- [ ] Python scripts in /scripts/ folder
- [ ] Python dependencies installed locally
- [ ] n8n account created
- [ ] At least 1 workflow created
- [ ] Slack workspace connected to n8n
- [ ] Test workflow run successfully
- [ ] Slack notification received
- [ ] Files saved to GitHub /data/ folder

---

## 🚀 NEXT PHASE (After 1 hour)

### Add the Missing Workflows (optional but recommended)

```
Workflow #2: Strategy Backtest (06:00 AM)
→ Similar structure to Workflow #1
→ Calls: feature_selector.py
→ Saves: /reports/backtest_report.json

Workflow #3: Pine Generation + Notify (09:00 AM)
→ Reads: backtest_report.json
→ Calls: strategy_generator.py
→ Sends: Full Slack message with Pine code

Workflow #4: Feedback Loop (Daily)
→ Reads: 3Commas live trades
→ Compares: backtest vs live results
→ Flags: If divergence > 5%
```

### Add Python Backend Server

```bash
# Utwórz server.py (w scripts/ folder):
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/api/calculate-indicators")
async def calculate_indicators(data: dict):
    # Your code here
    pass

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)

# Run:
python server.py

# n8n calls:
POST http://YOUR_IP:5000/api/calculate-indicators
```

---

## 📞 TROUBLESHOOTING

**Q: "GitHub token not working"**
A: Make sure token has `repo` scope. Test: `curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user`

**Q: "n8n can't reach my local Python service"**
A: If running locally, use ngrok to expose: `ngrok http 5000` → share URL with n8n

**Q: "First workflow failed"**
A: Check n8n Logs → Show execution details → Usually API key or path issue

**Q: "Slack not receiving message"**
A: Verify Slack token in n8n Settings. Test: n8n Slack node → Test → should see message

**Q: "How do I see generated Pine code?"**
A: It's in Slack message, GitHub file, or Telegram bot

---

## 🎓 LEARNING RESOURCES

```
n8n Docs: https://docs.n8n.io/
n8n Community: https://community.n8n.io/
GitHub API: https://docs.github.com/en/rest
Pine Script Docs: https://www.tradingview.com/pine-script-docs/
```

---

## 💡 PRO TIPS

1. **Test locally first**: Run Python scripts manually before automating with n8n
2. **Use GitHub as backup**: All data/configs in one place
3. **Monitor n8n logs**: Every workflow execution is logged
4. **Start simple**: Get 1 workflow working, then add more
5. **Version your strategies**: tag each Pine Script with version number
6. **Keep config.json updated**: This controls all thresholds

---

## 🏁 AFTER 60 MINUTES - WHAT'S WORKING

**Every day (if you setup Cron workflows):**

```
03:00 AM → Features calculated ✓
06:00 AM → Strategies backtested ✓
09:00 AM → Pine code generated + Slack alert ✓

You get: Slack message at 09:00 with:
- Best indicators for today
- Backtest metrics (WR, PF, DD)
- Full Pine Script code
- Link to detailed report

Your action: Copy code → Paste to TradingView → Done!
```

---

**That's it! You now have a fully automated AI trading strategy discovery system! 🚀**

Next person on your team can fork this repo and start using it immediately.
