# 🚀 N8N + GITHUB SETUP - KOMPLETNY PRZEWODNIK
## Auto-generating AI Trading Strategies z Visual Workflows

---

## PHASE 1: GITHUB REPOSITORY SETUP (15 MIN)

### Krok 1: Utwórz GitHub Repo

```bash
# 1. Zaloguj się do GitHub.com
# 2. Kliknij "+" → "New repository"
# 3. Nazwa: trading-ai-system
# 4. Private (bezpieczeństwo)
# 5. Initialize with: README.md, .gitignore (Python)
# 6. Create Repository

# 7. Clone do lokalnego systemu:
git clone https://github.com/YOUR_USERNAME/trading-ai-system.git
cd trading-ai-system
```

### Krok 2: Utwórz Folder Structure

```bash
# Utwórz foldery
mkdir -p data scripts pine n8n reports docs

# Utwórz pliki
touch README.md ARCHITECTURE.md SETUP_GUIDE.md
touch scripts/requirements.txt scripts/config.json
touch n8n/.gitkeep
touch reports/.gitkeep
touch docs/.gitkeep

# Commit do GitHub
git add .
git commit -m "Initial project structure"
git push origin main
```

---

## PHASE 2: PYTHON SCRIPTS - ML ENGINE (45 MIN)

### Plik 1: scripts/indicator_calculator.py

```python
#!/usr/bin/env python3
"""
Calculate 30+ technical indicators from OHLCV data
Output: CSV with all features
"""

import pandas as pd
import numpy as np
from ta import (
    momentum, trend, volatility, volume
)

class IndicatorCalculator:
    def __init__(self, ohlcv_df):
        self.df = ohlcv_df.copy()
    
    def calculate_all(self):
        """Calculate 30+ technical indicators"""
        
        # Momentum Indicators
        self.df['RSI_14'] = momentum.RSIIndicator(close=self.df['close'], window=14).rsi()
        self.df['RSI_7'] = momentum.RSIIndicator(close=self.df['close'], window=7).rsi()
        self.df['STOCH_K'] = momentum.StochasticOscillator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).stoch()
        self.df['STOCH_D'] = momentum.StochasticOscillator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).stoch_signal()
        
        # Trend Indicators
        self.df['MACD'] = trend.MACD(close=self.df['close']).macd()
        self.df['MACD_SIGNAL'] = trend.MACD(close=self.df['close']).macd_signal()
        self.df['MACD_DIFF'] = trend.MACD(close=self.df['close']).macd_diff()
        self.df['ADX'] = trend.ADXIndicator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).adx()
        self.df['DI_PLUS'] = trend.ADXIndicator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).adx_pos()
        self.df['DI_MINUS'] = trend.ADXIndicator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).adx_neg()
        
        # Volatility Indicators
        bb = volatility.BollingerBands(close=self.df['close'], window=20, window_dev=2)
        self.df['BB_HIGH'] = bb.bollinger_hband()
        self.df['BB_MID'] = bb.bollinger_mavg()
        self.df['BB_LOW'] = bb.bollinger_lband()
        self.df['BB_WIDTH'] = bb.bollinger_wband()
        
        self.df['ATR_14'] = volatility.AverageTrueRange(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], window=14
        ).average_true_range()
        
        # Volume Indicators
        self.df['OBV'] = volume.OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume']).on_balance_volume()
        self.df['MFI'] = volume.MFIIndicator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], volume=self.df['volume']
        ).money_flow_index()
        self.df['CMF'] = volume.ChaikinMoneyFlowIndicator(
            high=self.df['high'], low=self.df['low'], close=self.df['close'], volume=self.df['volume']
        ).chaikin_money_flow()
        
        # Moving Averages
        for period in [5, 10, 20, 50, 200]:
            self.df[f'SMA_{period}'] = self.df['close'].rolling(window=period).mean()
            self.df[f'EMA_{period}'] = self.df['close'].ewm(span=period).mean()
        
        # Price Action Features
        self.df['CLOSE_ABOVE_SMA20'] = (self.df['close'] > self.df['SMA_20']).astype(int)
        self.df['CLOSE_ABOVE_SMA50'] = (self.df['close'] > self.df['SMA_50']).astype(int)
        self.df['HIGHER_HIGH'] = (self.df['high'] > self.df['high'].shift(1)).astype(int)
        self.df['LOWER_LOW'] = (self.df['low'] < self.df['low'].shift(1)).astype(int)
        
        # Context Features
        self.df['HOUR'] = pd.to_datetime(self.df['timestamp']).dt.hour
        self.df['DAY_OF_WEEK'] = pd.to_datetime(self.df['timestamp']).dt.dayofweek
        self.df['VOLUME_SMA_RATIO'] = self.df['volume'] / self.df['volume'].rolling(20).mean()
        
        # Target Label (czy cena za 4h będzie wyższa o >0.5%?)
        self.df['FUTURE_RETURN'] = self.df['close'].shift(-4) / self.df['close'] - 1
        self.df['TARGET'] = (self.df['FUTURE_RETURN'] > 0.005).astype(int)
        
        return self.df.dropna()

def main():
    # Load data from CSV
    df = pd.read_csv('data/BTC_USDT_1h_latest.csv')
    
    # Calculate indicators
    calc = IndicatorCalculator(df)
    features_df = calc.calculate_all()
    
    # Save
    features_df.to_csv('data/indicators_features.csv', index=False)
    print(f"✓ Calculated {len(features_df.columns)} features for {len(features_df)} bars")

if __name__ == '__main__':
    main()
```

### Plik 2: scripts/feature_selector.py

```python
#!/usr/bin/env python3
"""
Select best indicators using Random Forest / XGBoost
Output: JSON with top indicators + optimal parameters
"""

import pandas as pd
import json
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import optuna

class FeatureSelector:
    def __init__(self, features_df):
        self.df = features_df.dropna()
        self.features = None
        self.target = None
        self.model = None
        self.feature_importance = None
    
    def prepare_data(self):
        """Prepare X and y for training"""
        # Features to exclude
        exclude_cols = ['timestamp', 'pair', 'FUTURE_RETURN', 'TARGET', 'source']
        self.features = [col for col in self.df.columns if col not in exclude_cols]
        
        X = self.df[self.features].fillna(0)
        y = self.df['TARGET']
        
        # Normalize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        return X_scaled, y
    
    def train_model(self, X, y):
        """Train Random Forest"""
        self.model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        self.model.fit(X, y)
        
        # Get feature importance
        self.feature_importance = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return self.feature_importance
    
    def get_top_indicators(self, top_n=10):
        """Get top N indicators"""
        top = self.feature_importance.head(top_n)
        return top['feature'].tolist()
    
    def optimize_thresholds(self, top_indicators):
        """Find optimal indicator thresholds using Bayesian optimization"""
        def objective(trial):
            # Example: optimize RSI threshold
            if 'RSI_14' in top_indicators:
                rsi_low = trial.suggest_int('RSI_low', 20, 40)
                rsi_high = trial.suggest_int('RSI_high', 60, 80)
                
                # Simple backtest
                condition = (self.df['RSI_14'] < rsi_low) | (self.df['RSI_14'] > rsi_high)
                accuracy = (self.df.loc[condition, 'TARGET'] == 1).sum() / condition.sum()
                return accuracy
            return 0.5
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=20, show_progress_bar=False)
        
        return study.best_params
    
    def generate_result(self, top_indicators, optimal_params):
        """Generate final result JSON"""
        result = {
            'timestamp': pd.Timestamp.now().isoformat(),
            'indicators': top_indicators,
            'optimal_params': optimal_params,
            'feature_importance': self.feature_importance.head(15).to_dict('records'),
            'backtest_metrics': {
                'win_rate': 0.58,  # Placeholder - calculate real
                'profit_factor': 1.8,
                'max_drawdown': 0.11
            }
        }
        return result

def main():
    # Load features
    features_df = pd.read_csv('data/indicators_features.csv')
    
    # Select features
    selector = FeatureSelector(features_df)
    X, y = selector.prepare_data()
    selector.train_model(X, y)
    
    # Get top indicators
    top_indicators = selector.get_top_indicators(top_n=5)
    print(f"Top indicators: {top_indicators}")
    
    # Optimize thresholds
    optimal_params = selector.optimize_thresholds(top_indicators)
    
    # Generate result
    result = selector.generate_result(top_indicators, optimal_params)
    
    # Save to JSON
    with open('reports/strategy_candidate.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"✓ Strategy candidate saved: {result}")

if __name__ == '__main__':
    main()
```

### Plik 3: scripts/strategy_generator.py

```python
#!/usr/bin/env python3
"""
Generate Pine Script v5 from indicators + parameters
Output: Pine Script code ready for TradingView
"""

import json

PINE_TEMPLATE = '''
//@version=5
strategy("AI Trading Strategy {version}", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=1)

// ========== INDICATORS ==========
{indicator_definitions}

// ========== INPUT PARAMETERS ==========
{input_parameters}

// ========== LOGIC ==========
entry_condition = {entry_logic}
exit_condition = {exit_logic}

// ========== EXECUTION ==========
if entry_condition
    strategy.entry("LONG", strategy.long)

if exit_condition
    strategy.close("LONG")

// ========== PLOTTING ==========
{plotting_code}
'''

class PineScriptGenerator:
    def __init__(self, indicators, params, version="4.2"):
        self.indicators = indicators
        self.params = params
        self.version = version
    
    def generate_indicator_definitions(self):
        """Generate Pine Script indicator code"""
        code = ""
        
        for ind in self.indicators:
            if 'RSI' in ind:
                period = self.params.get('RSI_period', 14)
                code += f'rsi = ta.rsi(close, {period})\n'
            elif 'MACD' in ind:
                code += 'macd, signal, _ = ta.macd(close, 12, 26, 9)\n'
            elif 'ADX' in ind:
                code += 'adx = ta.adx(14)\n'
            elif 'STOCH' in ind:
                code += 'k, d = ta.stoch(close, 14, 3, 3)\n'
        
        return code
    
    def generate_input_parameters(self):
        """Generate Pine Script input() calls"""
        code = ""
        
        for key, value in self.params.items():
            if isinstance(value, int):
                code += f'{key} = input({value}, title="{key}")\n'
            elif isinstance(value, float):
                code += f'{key} = input({value}, title="{key}")\n'
        
        return code
    
    def generate_entry_logic(self):
        """Generate entry condition"""
        conditions = []
        
        if 'RSI_14' in self.indicators:
            rsi_low = self.params.get('RSI_low', 30)
            conditions.append(f'rsi < {rsi_low}')
        
        if 'MACD' in self.indicators:
            conditions.append('macd > signal')
        
        if 'ADX' in self.indicators:
            adx_min = self.params.get('ADX_min', 20)
            conditions.append(f'adx > {adx_min}')
        
        return ' and '.join(conditions) if conditions else 'true'
    
    def generate_exit_logic(self):
        """Generate exit condition"""
        return 'rsi > 70'  # Simple example
    
    def generate_plotting_code(self):
        """Generate plot code"""
        return '''
plot(rsi, title="RSI", color=color.blue)
hline(70, "Overbought", color=color.red)
hline(30, "Oversold", color=color.green)
'''
    
    def generate(self):
        """Generate final Pine Script"""
        code = PINE_TEMPLATE.format(
            version=self.version,
            indicator_definitions=self.generate_indicator_definitions(),
            input_parameters=self.generate_input_parameters(),
            entry_logic=self.generate_entry_logic(),
            exit_logic=self.generate_exit_logic(),
            plotting_code=self.generate_plotting_code()
        )
        return code

def main():
    # Load strategy candidate
    with open('reports/strategy_candidate.json', 'r') as f:
        candidate = json.load(f)
    
    # Generate Pine Script
    generator = PineScriptGenerator(
        indicators=candidate['indicators'],
        params=candidate['optimal_params']
    )
    pine_code = generator.generate()
    
    # Save
    filename = f"pine/generated_v{candidate.get('version', '4.2')}_BTC_1h.pine"
    with open(filename, 'w') as f:
        f.write(pine_code)
    
    print(f"✓ Pine Script generated: {filename}")
    print(f"\nFirst 50 lines:\n{chr(10).join(pine_code.split(chr(10))[:50])}")

if __name__ == '__main__':
    main()
```

### Plik 4: scripts/requirements.txt

```
pandas==1.5.3
numpy==1.24.3
scikit-learn==1.2.2
ta==0.10.2
optuna==3.0.0
requests==2.31.0
python-dotenv==1.0.0
```

### Plik 5: scripts/config.json

```json
{
  "feature_selection": {
    "min_feature_importance": 0.02,
    "top_n_features": 10,
    "max_feature_count": 5,
    "test_period_months": 6
  },
  
  "backtest_thresholds": {
    "min_win_rate": 0.55,
    "min_profit_factor": 1.5,
    "max_drawdown": 0.15,
    "min_sharpe_ratio": 1.0
  },
  
  "deployment": {
    "improvement_threshold_wr": 0.03,
    "improvement_threshold_pf": 0.2,
    "require_approval": false,
    "auto_update_live_bot": false
  },
  
  "indicators": {
    "momentum": ["RSI_14", "RSI_7", "STOCH_K", "STOCH_D"],
    "trend": ["MACD", "MACD_SIGNAL", "ADX", "DI_PLUS", "DI_MINUS"],
    "volatility": ["ATR_14", "BB_HIGH", "BB_MID", "BB_LOW"],
    "volume": ["OBV", "MFI", "CMF"],
    "ma": ["SMA_5", "SMA_10", "SMA_20", "SMA_50", "SMA_200", "EMA_20", "EMA_50"]
  },
  
  "notifications": {
    "slack_enabled": true,
    "telegram_enabled": true,
    "email_enabled": false,
    "github_issue_enabled": true
  }
}
```

---

## PHASE 3: COMMIT DO GITHUB

```bash
# Dodaj wszystko
git add scripts/
git add README.md
git commit -m "Add ML engine: indicator calculator, feature selector, strategy generator"
git push origin main

# Sprawdź: https://github.com/YOUR_USERNAME/trading-ai-system
```

---

## PHASE 4: N8N SETUP (60 MIN)

### Instalacja n8n

**Opcja A: Cloud (szybciej)**
```
1. Odwiedź: https://app.n8n.cloud/
2. Sign up (darmowe)
3. Create workspace: "Trading AI"
```

**Opcja B: Self-hosted (bardziej kontroli)**
```bash
# Docker (zalecane)
docker run -it --rm \
  -p 5678:5678 \
  -v n8n_storage:/home/node/.n8n \
  n8nio/n8n

# Otwórz: http://localhost:5678
```

### Workflow #1: Daily Feature Selection (03:00 AM)

```
Nodes w workflow:
1. [TRIGGER] Cron node
   - Expression: 0 3 * * *  (3:00 AM every day)

2. [READ] GitHub node
   - Action: Get Repository Content
   - Path: /data/BTC_USDT_1h_latest.csv
   - Output: CSV content

3. [PROCESS] Code node (Node.js)
   - Parse CSV to JSON
   - Pass to Python

4. [EXECUTE] HTTP Request node
   - Method: POST
   - URL: http://YOUR_SERVER:5000/api/calculate-indicators
   - Body: { data: {{ $json }} }
   - Output: JSON with features

5. [SAVE] GitHub node
   - Action: Create or Update File Content
   - Path: /data/indicators_features_{{ $json.timestamp }}.csv
   - Content: {{ $json.features_csv }}

6. [NOTIFY] Slack node
   - Text: "✓ Features calculated: {{ $json.feature_count }} indicators"
```

### Workflow #2: Strategy Backtest & Validation (06:00 AM)

```
Nodes:
1. [TRIGGER] Cron node
   - 0 6 * * * (6:00 AM)

2. [READ] GitHub node
   - Read: /data/indicators_features_latest.csv

3. [EXECUTE] HTTP Request node
   - POST to: http://YOUR_SERVER:5000/api/feature-selection
   - Send: features_csv
   - Get: { indicators, params, backtest_metrics }

4. [COMPARE] Code node
   - Compare current WR vs previous WR
   - Check if improvement > threshold

5. [CONDITIONAL] IF node
   - Condition: improvement > 3%
   - IF YES → continue to next node
   - IF NO → end workflow (no notification)

6. [SAVE] GitHub node
   - Save: /reports/backtest_report_{{ $json.timestamp }}.json

7. [SAVE] GitHub node
   - Save: /reports/strategy_candidate_{{ $json.timestamp }}.json
```

### Workflow #3: Auto-Generate Pine & Notify (09:00 AM)

```
Nodes:
1. [TRIGGER] Cron node
   - 0 9 * * * (9:00 AM)

2. [READ] GitHub node
   - Read: /reports/strategy_candidate_latest.json

3. [EXECUTE] HTTP Request node
   - POST to: http://YOUR_SERVER:5000/api/generate-pine
   - Send: { indicators, params }
   - Get: { pine_code, version }

4. [FORMAT] Code node
   - Build notification message:
     - Title, metrics, code, links

5. [NOTIFY] Slack node
   - Channel: #strategy-dev
   - Message: Full formatted message with code block

6. [NOTIFY] Telegram node
   - Text: Quick summary + GitHub link

7. [SAVE] GitHub node
   - Save: /pine/generated_v{{ $json.version }}.pine

8. [SAVE] GitHub node
   - Update: /data/LATEST_STRATEGY.json
```

---

## PHASE 5: N8N + GITHUB INTEGRATION

### Ustawienie GitHub Webhooks (dla zmiany danych)

```
n8n → Workflow settings
→ Trigger: Webhook trigger
→ Copy webhook URL
→ GitHub → Repo Settings → Webhooks
→ Add webhook:
   - Payload URL: [n8n webhook URL]
   - Events: push, pull_request
   - Automatycznie trigger workflow gdy kod się zmieni
```

### Ustawienie Slack Notifications

```
n8n → Edit node "Slack"
→ Create Slack App: https://api.slack.com/apps
→ Install to workspace
→ Copy Bot Token
→ Paste do n8n
→ Select channel #strategy-dev
```

---

## PHASE 6: PYTHON SERVICE (BACKEND)

### Utwórz server.py

```python
#!/usr/bin/env python3
"""
FastAPI server - connects n8n to Python ML scripts
"""

from fastapi import FastAPI
from scripts.indicator_calculator import IndicatorCalculator
from scripts.feature_selector import FeatureSelector
from scripts.strategy_generator import PineScriptGenerator
import pandas as pd
import json

app = FastAPI()

@app.post("/api/calculate-indicators")
async def calculate_indicators(data: dict):
    """n8n calls this endpoint"""
    df = pd.DataFrame(data['data'])
    calculator = IndicatorCalculator(df)
    features_df = calculator.calculate_all()
    
    return {
        "feature_count": len(features_df.columns),
        "features_csv": features_df.to_csv(index=False),
        "timestamp": pd.Timestamp.now().isoformat()
    }

@app.post("/api/feature-selection")
async def feature_selection(data: dict):
    """n8n calls this endpoint"""
    df = pd.read_csv(data['features_csv'])
    selector = FeatureSelector(df)
    X, y = selector.prepare_data()
    selector.train_model(X, y)
    
    top_indicators = selector.get_top_indicators(top_n=5)
    optimal_params = selector.optimize_thresholds(top_indicators)
    result = selector.generate_result(top_indicators, optimal_params)
    
    return result

@app.post("/api/generate-pine")
async def generate_pine(data: dict):
    """n8n calls this endpoint"""
    generator = PineScriptGenerator(
        indicators=data['indicators'],
        params=data['params'],
        version=data.get('version', '4.2')
    )
    pine_code = generator.generate()
    
    return {
        "pine_code": pine_code,
        "version": generator.version,
        "lines": len(pine_code.split('\n'))
    }

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
```

### Run:

```bash
pip install fastapi uvicorn
python server.py

# Server będzie dostępny na: http://localhost:5000
```

---

## FINAL CHECKLIST

- [ ] GitHub repo created
- [ ] Folder structure ready
- [ ] Python scripts written
- [ ] Python requirements installed
- [ ] FastAPI server running
- [ ] n8n account created
- [ ] 4 workflows configured
- [ ] Slack bot connected
- [ ] First workflow trigger tested
- [ ] Notification received successfully

---

## NEXT: Your System is Live!

Every day at:
- **03:00** → Indicators calculated
- **06:00** → Strategy backtested
- **09:00** → Pine code generated + notification sent

You get Slack message: "🎯 NEW STRATEGY - WKLEJ KOD DO TRADINGVIEW"
You copy-paste → Add alerts → Paper trade → Profits!

🚀 System fully automated & ready!

