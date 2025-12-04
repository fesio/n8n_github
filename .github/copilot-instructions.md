<!--
Guidelines for AI coding agents working in the n8n_github repository.
Keep this short and actionable (~20–50 lines). Reference concrete files and commands.
-->

# Copilot / AI agent guide — n8n_github

Short, focused notes to help an AI agent be productive right away.

- Project purpose: AI-assisted generation of trading strategies via a small Python ML engine + n8n visual workflows. Key directories: `scripts/` (python engine), `n8n/` (workflows), `data/`, `reports/`, `pine/`.

- Quick runtime: `scripts/indicator_calculator.py` → `scripts/feature_selector.py` → `scripts/strategy_generator.py` produce CSV, JSON and Pine Script.
  - Example inputs: `data/BTC_USDT_1h_latest.csv`
  - Example outputs: `data/indicators_features.csv`, `reports/strategy_candidate.json`, `pine/generated_v{version}_BTC_1h.pine`

- Typical dev commands:
  - Install deps: `pip install -r scripts/requirements.txt` (run inside a Python virtualenv)
  - Run the pipeline locally: `python scripts/indicator_calculator.py && python scripts/feature_selector.py && python scripts/strategy_generator.py`
  - n8n dev: externally hosted on https://app.n8n.cloud or locally via `docker run -p 5678:5678 n8nio/n8n`

- Integration points & secrets:
  - n8n workflows call the Python service (HTTP POST) and use the GitHub and Slack nodes. When adding automation code, confirm the environment expects `GITHUB_TOKEN` and Slack credentials in n8n.

- Code patterns & constraints:
  - Scripts are small, single-purpose Python files with a clear `main()` and `if __name__ == '__main__'` entrypoint. Follow the same structure when adding new utilities.
  - Use the existing data->process->report flow — new features should emit artifacts in `data/`, `reports/` or `pine/` so n8n can pick them up.
  - Avoid changing the workflow contract (files/paths/JSON shapes) without updating `n8n/` or docs.

- Documentation & examples:
  - Keep README.md and `n8n_github_guide.md` in sync with any changes to script outputs, file names or scheduling.
  - When modifying scripts, include example commands and expected output file paths in the top-level docs.
  - This repo also includes an importable n8n workflow (JSON) and a short setup checklist:
    - `n8n/workflows/workflow_01_json_ready.md` — full JSON you can import into n8n (Workflow_01_DailyFeatureSelection).
    - `docs/setup_checklist.md` — step-by-step pre-setup and quick test checklist (GitHub token, Slack, ngrok, server).

 - Tests & validation:
  - Not all runtime files are present in the repo — many example Python scripts are included inline in `n8n_github_guide.md` and `quickstart_60min.md` as canonical examples. Always check those docs before adding or modifying `scripts/`.
  - No unit tests present — prefer small, easily runnable validation (e.g., a `scripts/check_outputs.py` that confirms CSV/JSON exist and have expected keys) — add alongside the script you change.

- Pull request guidance for AI edits:
  - Make minimal, focused commits. Prefer branch names like `feat/<short-desc>` or `fix/<short-desc>`.
  - Update docs (README or guide) with any behavioral changes and include one-line run examples.

If anything here is unclear or you want a different level of detail, ask and I’ll adjust this file. ✅
