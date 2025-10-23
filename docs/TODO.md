# DETAILED TODO/ACTION MAPPING (from application.md)

This list maps each major TODO/action point from `application.md` to its current implementation status and file locations. Use this as a living checklist for project status and onboarding.

---

## Architecture & Protocol Compliance (from architecture.md)

- [ ] Ensure all agent-to-agent communication uses the formal Agent2Agent protocol and message schema (`src/agent_protocol.py`).
- [ ] Guarantee all tool calls are routed through the MCP server and are fully logged for auditability (`src/mcv_server.py`).
- [ ] Maintain and update canonical workflow diagrams in `docs/visualFlowchart.mmd` as the workflow changes.
- [ ] Keep UI wireframes in `docs/wireframe.md` up to date with the actual UI implementation.
- [ ] Ensure all error/retry/escalation flows are implemented as described in `architecture.md` and are logged.
- [ ] Maintain audit logging policy and log rotation/archiving for `audit_trail.csv`.

## Multi-Agent System

- [x] **Investigation Agent**
	- Implemented: `src/InvestigationAgent.py`, registered in `src/agent_main.py`.
	- Orchestrates workflow, updates status, logs actions.

- [x] **Rights Check Agent**
	- Implemented: `src/RightsCheckAgent.py`, registered in `src/agent_main.py`.
	- Validates user rights, handles tool calls.

- [x] **Request for Information Agent**
	- Implemented: `src/RequestForInformationAgent.py`, registered in `src/agent_main.py`.
	- Handles clarification and manager validation logic.

- [x] **Advisory Agent**
	- Implemented: `src/AdvisoryAgent.py`, registered in `src/agent_main.py`.
	- Generates reports and recommendations.

- [ ] **Agent2Agent Protocol**
	- Agents are orchestrated in sequence in `src/agent_main.py` (function calls/context passing).
	- No explicit protocol abstraction; could be formalized if needed.

- [x] **MCP Server**
	- Implemented: `src/mcv_server.py` (local orchestration, not REST API).
	- Handles tool calls, data lookups, notifications, audit logging.

---

## User Interaction & Mocking

- [x] **HR Mutation Entry Page**
	- Implemented: `src/ui.py` (Streamlit app, see also `docs/wireframe.md`).

- [x] **Chat/Trigger Page**
	- Implemented: `src/ui.py` (Manual Trigger/Chat page).

- [x] **Mocked Email/Notification Interactions**
	- All notifications and responses are mocked in the UI (`src/ui.py`).
	- See also: `docs/toolcalls.md`, `docs/wireframe.md`.

- [x] **Manual/Mock Responses for User/Manager**
	- Implemented: "Mocked User/Manager Response" page in `src/ui.py`.

---

## Audit & Insights

- [x] **Audit Trail Logging**
	- Implemented: `src/ui.py` (`log_ui_audit`), agent/server code, and `audit_trail.csv`.

- [x] **Insights Page**
	- Implemented: `src/ui.py` (Insights/Dashboard page).

---

## Testing & Validation

- [x] **Mock All System Interactions**
	- Supported in UI and agent code.

- [x] **Validate with Sample Data and Edge Cases**
	- Sample data in `/data/`, test scenarios in docs, implemented in `tests/`.

- [x] **Unit/Integration/End-to-End Tests**
	- Test files: `tests/test_agents.py`, `tests/test_data_access.py`, `tests/test_integration_workflow.py`, etc.

---

## Documentation & Onboarding

- [x] **Environment Variables & Setup**
	- Documented in `/docs/application.md`, `/docs/agentsetup.md`.

- [x] **Usage Instructions & Troubleshooting**
	- In `/docs/application.md`, `/docs/CONTRIBUTING.md`.

- [x] **Documentation, Code, and UI Sync**
	- Ongoing; keep updating as system evolves.

---

## Outstanding/Nice-to-Have

- [ ] **Formal Agent2Agent Protocol Abstraction**
	- Current: Sequential orchestration in `agent_main.py`.
	- Next step: Implement a message-passing or protocol abstraction if needed for extensibility.

---


## Testing & Validation
- [ ] Test agent initialization and message flow with sample queries and data.
- [ ] Validate tool call execution and agent reasoning (mocked where needed).
- [ ] Validate system workflow with edge cases and sample data.
- [ ] Add unit tests for each agent and the MCP server.
- [ ] Add integration tests for the end-to-end workflow.
- [ ] Add test cases for error/retry/escalation flows.
- [ ] Add test data and scripts for demo scenarios.

- [ ] Document environment variables and setup steps in `/docs/application.md` and `/docs/agentsetup.md`.
- [ ] Add usage instructions and troubleshooting tips to documentation.
- [ ] Keep all documentation, code, and UI in sync as the system evolves.
- [ ] Reference `/docs/CONTRIBUTING.md` for onboarding and `/docs/prompts.md` for prompt templates.

**Legend:**
	- [x] = Implemented/complete
	- [~] = Partially implemented or could be improved
	- [ ] = Not yet implemented