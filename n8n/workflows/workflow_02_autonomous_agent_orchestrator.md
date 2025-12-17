# 🤖 N8N WORKFLOW #2 - AUTONOMOUS AGENT ORCHESTRATOR

## Workflow_02_AutonomousAgentOrchestrator — JSON gotowy do importu

_English summary: ready-to-import orchestrator that spawns specialist sub-agents, validates outputs, and posts a Slack summary with hallucination guard._

Poniższy workflow tworzy **menedżera-agenta**, który:
- przyjmuje zadanie (goal) przez webhook,
- układa plan podzadań i tworzy podagentów-specjalistów,
- wymusza format JSON, aby uniknąć fantomowych odpowiedzi,
- na końcu wykonuje sanity-check (hallucination guard) i publikuje wynik na Slacku.

Skopiuj cały JSON i wklej w n8n → "Import from JSON".

```json
{
  "name": "Workflow_02_AutonomousAgentOrchestrator",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "agent-manager",
        "responseMode": "onReceived",
        "responseData": "default"
      },
      "id": "uuid-webhook-1",
      "name": "Webhook - Task Intake",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [
        50,
        200
      ]
    },
    {
      "parameters": {
        "mode": "chat",
        "model": "gpt-4o-mini",
        "systemMessage": "You are an autonomous manager agent. Return STRICT JSON with fields: goal, context, tasks (array of {role, specialization, instructions}). Do NOT write prose. Enforce hallucination guard by requiring sources or clear assumptions.",
        "text": "Goal: {{$json.goal || $json.body.goal || \"Generate trading insight\"}}\nContext: {{$json.context || $json.body.context || \"\"}}\nReturn JSON only."
      },
      "id": "uuid-manager-1",
      "name": "OpenAI - Manager Plan",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "position": [
        260,
        200
      ],
      "credentials": {
        "openAiApi": {
          "id": "openai-credentials-id"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "const raw = $json.data?.choices?.[0]?.message?.content || $json.text || $json.plan || '';\nlet parsed = {};\ntry {\n  parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;\n} catch (e) {\n  parsed = {};\n}\nconst goal = parsed.goal || $json.goal || $json.body?.goal || 'unspecified goal';\nconst tasks = Array.isArray(parsed.tasks) && parsed.tasks.length ? parsed.tasks : [\n  {\n    role: 'Researcher',\n    specialization: 'market-data',\n    instructions: `Collect only verifiable facts for goal: ${goal}. Return bullet list with sources.`\n  },\n  {\n    role: 'Verifier',\n    specialization: 'fact-check',\n    instructions: `Cross-check claims for goal: ${goal}. Flag hallucinations and require evidence.`\n  }\n];\nreturn tasks.map(task => ({ json: { goal, ...task } }));"
      },
      "id": "uuid-code-1",
      "name": "Code - Build Specialist Tasks",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [
        470,
        200
      ]
    },
    {
      "parameters": {
        "mode": "chat",
        "model": "gpt-4o-mini",
        "systemMessage": "You are a specialist sub-agent. Stick to your specialization. Output JSON: {role, specialization, notes, answer, sources}. Never fabricate sources.",
        "text": "Goal: {{$json.goal}}\nSpecialization: {{$json.specialization}}\nRole: {{$json.role}}\nInstructions: {{$json.instructions}}"
      },
      "id": "uuid-specialist-1",
      "name": "OpenAI - Specialist Agent",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "position": [
        680,
        200
      ],
      "credentials": {
        "openAiApi": {
          "id": "openai-credentials-id"
        }
      }
    },
    {
      "parameters": {
        "jsCode": "const combined = items.map(item => ({\n  role: item.json.role,\n  specialization: item.json.specialization,\n  answer: item.json.answer || item.json.text || item.json.data?.text || item.json.data?.choices?.[0]?.message?.content || '',\n  sources: item.json.sources || []\n}));\nreturn [{ json: { combined } }];"
      },
      "id": "uuid-aggregate-1",
      "name": "Code - Combine Agents",
      "type": "n8n-nodes-base.code",
      "typeVersion": 2,
      "position": [
        890,
        200
      ]
    },
    {
      "parameters": {
        "mode": "chat",
        "model": "gpt-4o-mini",
        "systemMessage": "Act as hallucination guard. Validate answers strictly against provided combined data. If evidence is missing, say so. Return concise summary + risks.",
        "text": "Combined responses: {{$json.combined}}"
      },
      "id": "uuid-guard-1",
      "name": "OpenAI - Hallucination Guard",
      "type": "n8n-nodes-base.openai",
      "typeVersion": 1,
      "position": [
        1100,
        200
      ],
      "credentials": {
        "openAiApi": {
          "id": "openai-credentials-id"
        }
      }
    },
    {
      "parameters": {
        "channel": "#your-slack-channel",
        "text": "={{'🤖 Agent summary for ' + ($json.body?.goal || $json.goal || \"task\") + \"\\n\\n\" + ($json.text || $json.data?.choices?.[0]?.message?.content || '') + \"\\n\\nSources pinned above. If something is missing, manager should refine inputs.'}}"
      },
      "id": "uuid-slack-1",
      "name": "Slack - Final Notify",
      "type": "n8n-nodes-base.slack",
      "typeVersion": 2,
      "position": [
        1310,
        200
      ],
      "credentials": {
        "slackApi": {
          "id": "slack-credentials-id"
        }
      }
    }
  ],
  "connections": {
    "Webhook - Task Intake": {
      "main": [
        [
          {
            "node": "OpenAI - Manager Plan",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI - Manager Plan": {
      "main": [
        [
          {
            "node": "Code - Build Specialist Tasks",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Code - Build Specialist Tasks": {
      "main": [
        [
          {
            "node": "OpenAI - Specialist Agent",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI - Specialist Agent": {
      "main": [
        [
          {
            "node": "Code - Combine Agents",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "Code - Combine Agents": {
      "main": [
        [
          {
            "node": "OpenAI - Hallucination Guard",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "OpenAI - Hallucination Guard": {
      "main": [
        [
          {
            "node": "Slack - Final Notify",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  }
}
```

### Czytelna wersja kodu (jsCode)
```javascript
// Code - Build Specialist Tasks
const raw = $json.data?.choices?.[0]?.message?.content || $json.text || $json.plan || '';
let parsed = {};
try {
  parsed = typeof raw === 'string' ? JSON.parse(raw) : raw;
} catch (e) {
  parsed = {};
}
const goal = parsed.goal || $json.goal || $json.body?.goal || 'unspecified goal';
const tasks = Array.isArray(parsed.tasks) && parsed.tasks.length ? parsed.tasks : [
  {
    role: 'Researcher',
    specialization: 'market-data',
    instructions: `Collect only verifiable facts for goal: ${goal}. Return bullet list with sources.`
  },
  {
    role: 'Verifier',
    specialization: 'fact-check',
    instructions: `Cross-check claims for goal: ${goal}. Flag hallucinations and require evidence.`
  }
];
return tasks.map(task => ({ json: { goal, ...task } }));
```

```javascript
// Code - Combine Agents
const combined = items.map(item => ({
  role: item.json.role,
  specialization: item.json.specialization,
  answer: item.json.answer || item.json.text || item.json.data?.text || item.json.data?.choices?.[0]?.message?.content || '',
  sources: item.json.sources || []
}));
return [{ json: { combined } }];
```

---

## Jak zaimportować
1. **Kopiuj JSON** powyżej (od `{` do `}`).
2. W n8n kliknij **Import from JSON** i wklej treść.
3. Podmień credentials:
   - `openai-credentials-id` → Twoje OpenAI (lub Azure OpenAI) w n8n.
   - `slack-credentials-id` → Twoje połączenie Slack.
   - `#your-slack-channel` → Kanał Slack, na który mają trafiać podsumowania.
4. (Opcjonalnie) zmień ścieżkę webhooka `agent-manager` lub dodaj auth header.
5. Aktywuj workflow i wyślij `POST` z payloadem:
   ```json
   {
     "goal": "Znajdź strategię dla BTC/USDT 1h",
     "context": "Użyj danych z ostatnich 30 dni"
   }
   ```

## Co się dzieje po kolei
- **Webhook** przyjmuje zadanie i odpala menedżera.
- **Manager Plan** zwraca czysty JSON z listą podzadań.
- **Build Specialist Tasks** zamienia plan na wiele elementów (po jednym na podagenta).
- **Specialist Agent** działa na każdym elemencie oddzielnie (n8n iteruje automatycznie).
- **Combine Agents** skleja wyniki w jedną paczkę.
- **Hallucination Guard** waliduje odpowiedzi i ogranicza fantomowe treści.
- **Slack** publikuje finalny, zweryfikowany wynik.

## Notatki
- Trzymaj **temperature nisko (0.1–0.3)**, aby zmniejszyć halucynacje.
- Jeśli potrzebujesz kolejnych podagentów, dodaj więcej itemów w `Build Specialist Tasks`.
- Możesz podmienić Slack na email/Telegram — zostaw strukturę JSON bez zmian.
