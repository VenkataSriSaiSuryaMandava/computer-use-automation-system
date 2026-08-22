├── mock_bank_app/
│   ├── __init__.py
│   └── app.py                  # Standalone legacy-styled mock core banking portal
├── src/
│   ├── __init__.py
│   ├── schemas.py              # Pydantic schemas: Artifact, Steps, Locators, Results
│   ├── guardrails.py           # Domain allowlists, risky-action gates, PII scrubbers
│   ├── hitl.py                 # Live-session escalation and human-in-the-loop coordinator
│   ├── agent.py                # LLM-driven Observe-Decide-Act discovery engine
│   └── replay.py               # Deterministic execution engine with 3-tier error taxonomy
├── evidence/
│   ├── capability_artifact.json
│   ├── discovery_run.log
│   ├── replay_success.log
│   └── replay_business_error.log
├── tests/
│   ├── __init__.py
│   └── test_automation.py      # End-to-end pytest suite
├── README.md                   # Setup guide and reproduction commands
├── REPORT.md                   # Full 7-section design report
└── requirements.txt