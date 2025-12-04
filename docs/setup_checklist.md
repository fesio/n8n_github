# ✅ SETUP CHECKLIST - WYKONAJ TERAZ

Musisz zrobić **6 rzeczy** zanim workflow zacznie działać. Każda zajmie 2-5 minut.

---

## ✓ KROK 1: UTWÓRZ GITHUB TOKEN (3 MIN)

```
1. Otwórz: https://github.com/settings/personal-access-tokens/new
   (Jeśli nie zalogowany → zaloguj się)

2. Wypełnij:
   - Token name: n8n-trading
   - Expiration: 90 days (albo więcej)
   
3. Scopes (zaznacz):
   ✓ repo (full control)
   
4. Click "Generate token"

5. SKOPIUJ TOKEN (pojawi się raz!)
   Wygląda: ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
6. Zapisz gdzieś (będzie potrzebny za chwilę)
```

---

## ✓ KROK 2: POŁĄCZ GITHUB TOKEN W N8N (2 MIN)

```
W n8n (gdzie masz otwarte):

1. Left sidebar → Credentials (ikonka klucza)

2. "+ Add credentials"

3. Select: GitHub Token API

4. Paste token z Kroku 1

5. Test connection → powinno być zielone ✓

6. Save
```

---

## ✓ KROK 3: UTWÓRZ SLACK BOT (5 MIN)

```
1. Otwórz: https://api.slack.com/apps

2. Click "Create New App"

3. "From scratch"
   - App name: n8n-trading
   - Select workspace: twoja nazwa

4. Left menu → "OAuth & Permissions"

5. Scopes → User Token Scopes:
   + Add OAuth Scope
   ✓ chat:write
   ✓ channels:read

6. "Install to Workspace"
   → Authorize (powinno być zielone)

7. Copy: Bot User OAuth Token
   Wygląda: xoxb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
8. Zapisz token
```

---

## ✓ KROK 4: POŁĄCZ SLACK W N8N (2 MIN)

```
W n8n:

1. Left sidebar → Credentials

2. "+ Add credentials"

3. Select: Slack

4. Paste Bot token z Kroku 3

5. Test connection → zielone ✓

6. Save
```

---

## ✓ KROK 5: URUCHOM PYTHON SERVER (5 MIN)

```bash
# Otwórz terminal/command prompt

# Przejdź do folderu:
cd /path/to/trading-ai-system/scripts

# Zainstaluj requirements (jeśli nie zrobione):
pip install -r requirements.txt

# Uruchom server:
python server.py

# Powinno wyświetlić:
# INFO:     Uvicorn running on http://0.0.0.0:5000
# [Press ENTER to quit]

# ⚠️ POZOSTAW TERMINAL OTWARTY!
```

---

## ✓ KROK 6: ZNAJ SWÓJ IP/URL (3 MIN)

**Jeśli Python działa LOKALNIE:**

```bash
# Otwórz DRUGI terminal i wykonaj:
ngrok http 5000

# Wyświetli coś takiego:
# Forwarding: https://xxxxx-xx-xxx.ngrok-free.app -> http://localhost:5000

# Skopiuj URL: https://xxxxx-xx-xxx.ngrok-free.app
```

**Jeśli Python na SERWERZE:**

```
IP: xxx.xxx.xxx.xxx
Port: 5000
URL: http://xxx.xxx.xxx.xxx:5000
```

---

## 🔧 TERAZ WGRAJ WORKFLOW

W n8n (gdzie pokazana jest pusta plansza):

```
1. Right side, top → Click "..." (trzy kropki)

2. "Import from URL" lub "Import from file"
   (lub po prostu "Add" → "Start from blank" → potem "+" nodes)

3. Jeśli masz plik JSON:
   - Drag & drop plik
   - Lub copy-paste JSON z pliku: workflow_01_json_ready.md

4. Kliknij "Import"

5. Workflow pojawi się na ekranie

6. ZMIEŃ:
   - ❗ YOUR_USERNAME → twoja GitHub username
   - ❗ YOUR_SERVER → URL z Kroku 6 (ngrok URL lub IP)
   
   Gdzie znaleźć do zmiany:
   - Kliknij każdy HTTP node (obie)
   - Sprawdź URL → replace YOUR_SERVER
   - GitHub node → replace YOUR_USERNAME
```

---

## 📊 SPRAWDŹ POŁĄCZENIA

W workflow powinno być:

```
CRON → For Each Pair → HTTP GET → Code → HTTP POST → GitHub → Slack
```

Jeśli brakuje strzałek:
- Hover na node
- Kliknij "+" output arrow
- Connect do następnego node'a

---

## ▶️ TEST WORKFLOW

```
1. Kliknij Play (▶️ Execute workflow)

2. Wait ~5-10 sekund

3. Check "Executions" tab:
   - Powinno być zielone ✓
   - Jeśli czerwone ❌ → kliknij aby zobaczyć error

4. Check "Logs" na dole:
   - Powinno być: "Workflow executed successfully"
   - Jeśli są błędy → przeczytaj message

5. Sprawdź:
   - ✓ Slack #strategy-dev → powinna być wiadomość
   - ✓ GitHub repo → powinien być nowy plik CSV
```

---

## 🎯 JEŚLI COŚ NIE DZIAŁA:

| Error | Przyczyna | Fix |
|-------|-----------|-----|
| "401 Unauthorized GitHub" | Zły token lub scopes | Sprawdź token, musi mieć `repo` scope |
| "Cannot read property 'body'" | Python nie zwrócił danych | Sprawdź czy Python server działa |
| "Connection refused" | Python nie uruchomiony | `python server.py` w terminalu |
| "Slack message not sent" | Zły Bot token | Sprawdź token w Slack App settings |
| "404 File not found" | Zły YOUR_USERNAME | Sprawdź GitHub login |
| "405 Method not allowed" | Python endpoint nie istnieje | Sprawdź server.py - musi mieć `/api/calculate-indicators` |

---

## 💾 OSTATNIE KROKI:

```
1. Po udanym teście → Click "Save" (top right)

2. Workflow settings → Toggle "Active" = ON

3. Workflow będzie działać codziennie o 03:00 AM

4. Możesz go teraz zamknąć
```

---

## 📋 CHECKLIST - GOTOWY DO DROGI?

- [ ] GitHub token created
- [ ] GitHub connected to n8n
- [ ] Slack bot created
- [ ] Slack connected to n8n
- [ ] Python server running (terminal otwarty)
- [ ] ngrok/IP URL known
- [ ] Workflow imported
- [ ] YOUR_USERNAME replaced (2 miejsca)
- [ ] YOUR_SERVER replaced (2 miejsca)
- [ ] Workflow tested successfully
- [ ] Slack notification received
- [ ] GitHub file created
- [ ] Workflow activated (toggle ON)

---

## 🎉 GOTOWE!

Workflow #1 jest teraz aktywny i będzie:

```
✓ Każdego dnia o 03:00 AM:
  - Przeczyta CSV z GitHub
  - Obliczy 30+ wskaźników
  - Wyśle do Python ML
  - Zapisze wynik na GitHub
  - Wyśle notyfikację na Slack
```

**Następny: Powtórz dla Workflow #2 i #3** 

---

Powodzenia! 🚀

Jeśli masz pytania - pisz!
