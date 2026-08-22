# **Design Report: Computer-Use Automation System**

# System Overview & Architecture Plan

The system implements the **\*\*"Record-Once with LLM, Replay-Deterministically without LLM"\*\*** paradigm for legacy enterprise and banking environments.

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

* **\*\*Typed Inputs/Outs:\*\*** Defined data structures for expected inputs and outputs.

* **\*\*Multi-Strategy Loc:\*\*** Robust element localization strategies.

* **\*\*Checkpoints/Guards:\*\*** Verification steps to ensure the system is in the expected state.

### 3. Replay Engine

The execution environment that runs the capability artifact.

* **\*\*Zero-Inference:\*\*** Runs deterministically without relying on the LLM, reducing latency and cost.

* **\*\*Triage System:\*\*** Evaluates execution state into three categories: Business Outcome, Recoverable errors, or Panic (unrecoverable).

### Execution Outcomes

* **\*\*Success / Business Data:\*\*** The happy path yielding the desired business results.

* **\*\*HITL (Human-in-the-Loop) Escalation:\*\*** When a panic or unrecoverable state is reached, the system pauses, allows a human to intervene, and then resumes execution.

## 1. Architecture

The architecture strictly decouples the exploratory, stochastic discovery phase from the high-throughput production replay phase[cite: 1]:

- **\*\*Discovery Phase (LLM-in-the-loop):\*\*** Operates against a live UI to explore pathways, inspect accessibility nodes, bind input parameters, declare extraction targets, and establish validation checkpoints[cite: 1].

- **\*\*Capability Compiler:\*\*** Translates the discovery session into a versioned, serializable `CapabilityArtifact` JSON schema[cite: 1].

- **\*\*Deterministic Replay Engine (Zero-LLM):\*\*** Executes the compiled flow using a multi-strategy locator pipeline (`Aria > Text > CSS > XPath`), intercepts business error outcomes, and exposes live-session escalation seams for human intervention[cite: 1].

## 2. Artifact Schema

The `CapabilityArtifact` represents a formal capability contract decoupled from conversational transcripts[cite: 1]:

- **\*\*Typed Input/Output Contracts:\*\*** Defines parameters (e.g., `member_id`) and output types (`savings_balance`), enabling agent orchestration layers to invoke capabilities via structured schemas[cite: 1].

- **\*\*Dynamic Variable Interpolation:\*\*** Uses Jinja-style parameter tokens (`{{inputs.member_id}}`) to support arbitrary runtime inputs without re-discovery[cite: 1].

- **\*\*Multi-Strategy Locators:\*\*** Encapsulates accessibility roles, text content, CSS selectors, and XPath fallback trees to prevent breakage during minor styling updates[cite: 1].

- **\*\*Checkpoints:\*\*** Declares post-action assertions (`url_contains`, `element_visible`, `text_present`) to verify state transitions before proceeding[cite: 1].

## 3. Determinism & Error Handling

Replay determinism eliminates model latency, non-deterministic reasoning, and token costs[cite: 1]:

- **\*\*Locator Strategy:\*\*** Prioritizes Accessibility Tree nodes (`get_by_role`, `get_by_name`) over raw CSS, as enterprise UIs frequently alter nested table structures or hashed CSS classes while semantic element roles remain stable[cite: 1].

- **\*\*3-Tier Error Taxonomy:\*\***
  1. *\*Expected Business Outcomes:\** Catches known institution states (e.g., `404 Member Not Found`, `403 Account Frozen`) and returns `BUSINESS_OUTCOME` with structured metadata rather than failing with an unhandled exception[cite: 1].
  2. *\*Recoverable Conditions:\** Employs auto-wait polling and retries for network latency or dismissible dialogs[cite: 1].
  3. *\*Hard Failures:\** When locator resolution is exhausted or assertions fail, the engine captures step diagnostics and initiates human escalation[cite: 1].

## 4. Heterogeneity & Multi-Tenant

- **\*\*Surface Abstraction:\*\*** The execution engine communicates through driver primitives (`click`, `fill`, `extract`, `wait_for`)[cite: 1]. For legacy native Windows desktop apps (e.g., Win32/WPF banking terminals), this abstraction layer maps directly onto OS-level accessibility APIs (Windows UI Automation / PyWinAuto) without modifying the high-level `CapabilityArtifact` schema[cite: 1].

- **\*\*Multi-Tenant Inheritance:\*\*** Multiple credit unions often run identical vendor software (e.g., Fiserv, Symitar) configured with custom branding or routes[cite: 1]. The system uses an **\*\*Overlay Pattern\*\***: a base artifact schema defines core workflow steps, while tenant-specific JSON overlays override locator mappings or entry routes without requiring ground-up discovery runs[cite: 1].

## 5. Escalation & Handoff

When automation is blocked:

1. The engine pauses the active execution thread while maintaining the live Playwright browser context[cite: 1].

2. An intervention payload (failing step ID, diagnostic screenshot, error description) is routed to a human operator[cite: 1].

3. The operator manipulates the active browser window to resolve the issue (e.g., solving an unexpected security challenge)[cite: 1].

4. Upon entering `resume`, the engine re-evaluates the page DOM state, logs the human intervention to the execution trace, and continues deterministic execution[cite: 1].

## 6. Safety

- **\*\*Host Allowlisting:\*\*** Network navigation is restricted to pre-approved institutional domains (`localhost:8000`, internal endpoints)[cite: 1].

- **\*\*Irreversible Operation Gates:\*\*** Workflows flagged as `reversible: false` (such as funds transfers or account terminations) require explicit operator confirmation before firing[cite: 1].

- **\*\*PII / Secret Scrubbing:\*\*** Regex scrubbers sanitize SSNs, credit card numbers, and credentials from all execution traces, JSON outputs, and diagnostic logs[cite: 1].

## 7. Cuts

- **\*\*Deliberately Cut:\*\*** A full WebRTC co-browsing operator portal UI (mocked via active browser window suspension and CLI resume hooks to focus on the control-transfer model)[cite: 1].

- **\*\*Next to Build:\*\*** Automated shadow-run locator self-healing and tenant configuration drift detectors[cite: 1].
