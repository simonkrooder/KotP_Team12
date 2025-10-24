

# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [flow.md](flow.md): Canonical workflow diagram
- [toolcalls.md](toolcalls.md): MCP tool call protocol and agent tool call details
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

# Tool Call Implementation Action List

## Context Summary

This document outlines the required actions to implement tool calls in all agents of the Multi-Agent Access Control System. The system uses a modular, agent-based architecture where each agent is responsible for its own reasoning (via Azure model) and tool calls (via the MCP server). All tool calls (e.g., data lookup, authorization check, notification, report generation) are routed through the MCP server, which exposes REST endpoints. The UI and audit trail are tightly integrated with the agent workflow, and all actions must be logged for traceability.

**Current State:**
- Agents (`InvestigationAgent`, `RightsCheckAgent`, `RequestForInformationAgent`, `AdvisoryAgent`) are implemented as Python classes with `handle_request(context)` methods.
- Agents currently perform reasoning via Azure model calls, but do not yet make their own tool calls (these are TODOs in the code).
- The MCP server exposes endpoints for `/api/authorization/check`, `/api/data/lookup`, `/api/notify/send`, and `/api/report/generate`.
- Documentation (`architecture.md`, `application.md`, `wireframe.md`) now fully describes the intended tool call flow, conditions, and UI integration.

**Goal:**
Implement all required tool calls in the agents, ensure robust error handling and audit logging, and update supporting infrastructure as needed.

---

## Action List: Implementing Tool Calls in Agents

### 1. InvestigationAgent
- [ ] Refactor `handle_request` to:
    - [ ] Call `/api/data/lookup` via the MCP server at investigation start if additional context/evidence is needed.
    - [ ] Pass the full investigation context, mutation details, and prior findings to the Azure model for reasoning.
    - [ ] Log all tool calls and results using the audit trail mechanism.
    - [ ] Handle errors and escalate as per the documented retry/escalation flow.
    - [ ] Add/Update tests for tool call logic and error handling.

### 2. RightsCheckAgent
- [ ] Refactor `handle_request` to:
    - [ ] Call `/api/authorization/check` via the MCP server to validate user rights.
    - [ ] Optionally call `/api/data/lookup` for supporting evidence if required by the context.
    - [ ] Pass user ID, mutation details, system, access level, and context to the Azure model for reasoning.
    - [ ] Log all tool calls and results using the audit trail mechanism.
    - [ ] Handle errors and escalate as per the documented retry/escalation flow.
    - [ ] Add/Update tests for tool call logic and error handling.

### 3. RequestForInformationAgent
- [ ] Refactor `handle_request` to:
    - [ ] Call `/api/notify/send` via the MCP server to contact user/manager for clarification/validation.
    - [ ] Call `/api/data/lookup` to validate claims (e.g., sick leave, vacation) as needed.
    - [ ] Pass mutation context, clarification questions, user/manager info, and claim details to the Azure model for reasoning.
    - [ ] Integrate with the UI/backend flow for receiving user/manager responses (see `architecture.md`).
    - [ ] Log all tool calls, responses, and results using the audit trail mechanism.
    - [ ] Handle errors and escalate as per the documented retry/escalation flow.
    - [ ] Add/Update tests for tool call logic, UI integration, and error handling.

### 4. AdvisoryAgent
- [ ] Refactor `handle_request` to:
    - [ ] Call `/api/report/generate` via the MCP server to generate the advisory report.
    - [ ] Optionally call `/api/data/lookup` for additional evidence if required by the context.
    - [ ] Pass the full investigation context and findings from other agents to the Azure model for reasoning.
    - [ ] Log all tool calls and results using the audit trail mechanism.
    - [ ] Handle errors and escalate as per the documented retry/escalation flow.
    - [ ] Add/Update tests for tool call logic and error handling.

---

## Action List: Supporting Infrastructure & Tools

### 5. MCP Server & Tool Endpoints
- [ ] Review and, if needed, implement or update the following endpoints in the MCP server:
    - [ ] `/api/authorization/check` (authorization validation)
    - [ ] `/api/data/lookup` (CSV data queries)
    - [ ] `/api/notify/send` (mocked notifications/clarifications)
    - [ ] `/api/report/generate` (advisory report generation)
- [ ] Ensure all endpoints:
    - [ ] Validate input and output schemas.
    - [ ] Log all requests and results to the audit trail.
    - [ ] Return clear error messages and status codes.
    - [ ] Are covered by tests (unit/integration).

### 6. Agent2Agent Protocol & Audit Trail
- [ ] Ensure all agent-to-agent and agent-to-MCP messages are logged using the canonical protocol and audit trail.
- [ ] Update or refactor `log_agent_message` and related helpers as needed.
- [ ] Add/Update tests for audit logging and traceability.

### 7. UI & User/Manager Response Integration
- [ ] Ensure the UI (see `wireframe.md` and `ui.py`) correctly surfaces agent requests for user/manager responses.
- [ ] Ensure the backend routes responses to the correct agent/context and logs them.
- [ ] Add/Update tests for UI/backend integration and audit trail updates.

### 8. Error Handling, Retries, and Escalation
- [ ] Implement robust error handling in all agent tool call logic.
- [ ] Ensure retry logic and escalation to manual intervention (AdvisoryAgent) as per documentation.
- [ ] Log all errors, retries, and escalations in the audit trail.
- [ ] Add/Update tests for error/retry/escalation flows.

### 9. Extensibility & Documentation
- [ ] Document the tool call implementation pattern in `architecture.md` and `application.md` as changes are made.
- [ ] Ensure all new/updated code is covered by docstrings and usage examples.
- [ ] Update onboarding and developer docs as needed.

---

## Cross-Cutting Actions
- [ ] Ensure all tool call logic is modular, testable, and auditable.
- [ ] Maintain a running changelog of tool call implementation progress.
- [ ] Review and update this action list as work progresses.

---

**This file is the canonical checklist for implementing agent tool calls and supporting infrastructure. Update it as the project evolves.**

For the full MCP tool call protocol specification, see [`toolcalls.md`](toolcalls.md).