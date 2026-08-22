# Computer-Use Automation System

An end-to-end integration layer that records legacy enterprise web applications with...

## Requirements
- Python 3.10+
- Playwright Chromium browser binaries

## Setup & Installation

1. Clone repository and install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Start the local mock core-banking service:
```bash
python -m mock_bank_app.app
```
*(Server listens on http://127.0.0.1:8000)*

## Execution Commands

### 1. Discovery Run (LLM Agent Loop)
Discovers the UI workflow, captures accessibility/DOM state, parameterizes variables, and compiles the artifact:

```bash
python -m src.agent
```
Artifact written to `evidence/capability_artifact.json`.

### 2. Deterministic Replay (Production Path)
Replays the capability artifact deterministically without an LLM:

```bash
python -m src.replay
```

### 3. Automated Test Suite
Runs comprehensive test validations across all error pathways and guardrails:

```bash
python -m pytest tests/test_automation.py -v
```