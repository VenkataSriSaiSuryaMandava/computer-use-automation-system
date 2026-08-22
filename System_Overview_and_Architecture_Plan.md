# System Overview & Architecture Plan

The system implements the **"Record-Once with LLM, Replay-Deterministically without LLM"** paradigm for legacy enterprise and banking environments.

## Architecture Diagram

```text
    ┌───────────────────────────────────────────────────┐
    │                  DISCOVERY PHASE                  │
    │  Goal + Target App ──> LLM (Vision/Acc. Tree)     │
    └───────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────────┐
    │                CAPABILITY ARTIFACT                │
    │                - Typed Inputs/Outs                │
    │                - Multi-Strategy Loc               │
    │                - Checkpoints/Guards               │
    └───────────────────────────────────────────────────┘
                            │
                            ▼
    ┌───────────────────────────────────────────────────┐
    │                  REPLAY ENGINE                    │
    │    Zero-Inference • Deterministic Execution       │
    │  Triage: Business Outcome | Recoverable | Panic   │
    └───────────────────────────────────────────────────┘
               │                              │
               ▼                              ▼
    [Success / Business Data]          [HITL Escalation]
                                 (Pause • Human acts • Resume)
```

## Components

### 1. Discovery Phase
The initial phase where the goal and the target application are processed through a Large Language Model (utilizing Vision and Accessibility Trees) to map out the execution path.

### 2. Capability Artifact
The output of the discovery phase. It defines the structured execution blueprint containing:
* **Typed Inputs/Outs:** Defined data structures for expected inputs and outputs.
* **Multi-Strategy Loc:** Robust element localization strategies.
* **Checkpoints/Guards:** Verification steps to ensure the system is in the expected state.

### 3. Replay Engine
The execution environment that runs the capability artifact.
* **Zero-Inference:** Runs deterministically without relying on the LLM, reducing latency and cost.
* **Triage System:** Evaluates execution state into three categories: Business Outcome, Recoverable errors, or Panic (unrecoverable).

### Execution Outcomes
* **Success / Business Data:** The happy path yielding the desired business results.
* **HITL (Human-in-the-Loop) Escalation:** When a panic or unrecoverable state is reached, the system pauses, allows a human to intervene, and then resumes execution.
