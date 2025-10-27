# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [flow.md](flow.md): Canonical workflow diagram
- [toolcalls.md](toolcalls.md): MCP tool call protocol and agent tool call details
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

# DEMO UI INTERACTIVITY & REAL-TIME AGENT LOGGING: DETAILED APPROACH


Make the demo UI (`src/ui.py`) more interactive by:
- Allowing user/manager responses to the `RequestForInformationAgent` to be handled interactively in the UI (not just as a single output at the end).
- Surfacing all agent output, thoughts, and tool call results in real time, so they appear on screen step-by-step as the workflow progresses.
- **Filter all agent log entries and pending actions in the UI by the current investigation's `mutation_id` or `correlation_id`.**
- When a user selects a mutation (e.g., from the HR Mutations Table), store the `mutation_id` in session state and use it to filter all polled log entries and pending actions, so only those relevant to the current investigation are shown in the timeline/chat and response forms.

### 1. Real-Time Agent Output Logging
- Refactor agent orchestration (in `agent_main.py` and agent classes) so that every agent step, tool call, and intermediate result is logged to a shared state (e.g., `audit_trail.csv` and/or a new `agent_log.csv`).
- In `ui.py`, implement a polling or streaming mechanism (e.g., using Streamlit's `st.experimental_rerun()` or session state) to update the UI every few seconds, showing new agent outputs as they are logged.
- Display agent thoughts, tool call results, and status changes in a timeline/chat-like format, with each entry appearing as soon as it is available.
- Optionally, add a "Live Agent Log" panel to the UI, showing all agent actions and reasoning in real time for the current mutation/investigation.
- **Always filter agent log entries and pending actions by the selected `mutation_id` or `correlation_id` in the UI, so only the current/latest investigation run is shown.**
- [ ] Add `/docs/agentsetup.md` (referenced in multiple docs, but missing)
- [ ] Add `/docs/CHANGELOG.md` (referenced for changelog/dev diary, but missing)
- [ ] When the `RequestForInformationAgent` issues a clarification or validation request, write a pending action to `pending_actions.csv` (or similar shared state).
- [ ] The UI should poll for pending actions relevant to the current user/manager and display a form for response (see wireframe in `docs/wireframe.md`).
- [ ] On response submission, update the pending action status and log the response to the audit trail.
- [ ] The agent workflow should resume automatically when a response is received, continuing to log outputs in real time.
- [ ] For demo purposes, allow switching between different user/manager roles in the UI to simulate responses from multiple parties.
- [ ] Add `/docs/README.md` (or `/docs/index.md`) summarizing and linking all docs for onboarding
- [ ] Audit all references to missing docs and update them to point to the correct file (or add the missing file)
- [ ] For each mutation/investigation, visualize the workflow as a sequence of agent actions, tool calls, and responses, updating in real time as the process unfolds.
- [ ] Use Streamlit components (e.g., `st.timeline`, `st.chat_message`, or custom HTML) to show each step as a separate entry, with timestamps and agent names.
- [ ] Allow users to expand/collapse details for each step, including full context, tool call arguments/results, and agent reasoning.
- [ ] Surface errors, retries, and escalation events in the UI as they occur, with clear status indicators and audit log entries.
- [ ] Allow manual intervention/escalation via the UI if an agent step fails repeatedly or requires human input.
- [ ] Document the new UI/agent interaction pattern in `docs/todo.md`, `docs/wireframe.md`, and `src/ui.py`.
- [ ] Ensure all agent outputs, pending actions, and user/manager responses are fully auditable and reconstructable from the logs.
- [ ] Update onboarding and demo instructions to highlight interactive, real-time features.
- [ ] Test agent initialization and message flow with sample queries and data (see CLI modes in agent .py files).
- [ ] Validate tool call execution and agent reasoning (mocked and real Azure SDK flows).
- [ ] Refactor agent orchestration to log every step/output in real time.
- [ ] Implement polling/streaming in the UI to surface new agent outputs as they are logged.
- [ ] Add interactive forms for user/manager responses, tied to pending actions.
- [ ] Visualize the workflow and agent log as a timeline/chat in the UI.
- [ ] Handle errors, retries, and escalation interactively.
- [ ] Update documentation and wireframes to reflect the new pattern.
- [ ] Validate system workflow with edge cases and sample data.
- [ ] Add unit tests for each agent and the MCP server.
- [ ] Add integration tests for the end-to-end workflow.
- [ ] Add test cases for error/retry/escalation flows.
- [ ] Add test data and scripts for demo scenarios.
- [ ] Document environment variables and setup steps in `/docs/application.md` and `/docs/agentsetup.md`.
- [ ] Add usage instructions and troubleshooting tips to documentation.
- [ ] Keep all documentation, code, and UI in sync as the system evolves.
- [ ] Reference `/docs/CONTRIBUTING.md` for onboarding and `/docs/prompts.md` for prompt templates.
- [ ] Always use the Agent2Agent protocol for all agent communication and logging (see `src/agent_protocol.py`).
- [ ] Use correlation IDs and timestamps for every message and log entry.
- [ ] Ensure all tool calls are registered as async functions and are auditable.
- [ ] Use environment variables for Azure SDK configuration (see `.env` and agent .py files).
- [ ] Support both CLI and UI-driven workflows for testing and debugging.
- [ ] All CSV read/write operations must be thread-safe and robust to concurrent access (see `src/pending_actions.py`).
- [ ] For extensibility, document new tool calls, agent actions, and UI patterns as they are added.
- [ ] Ensure compliance with audit, security, and accessibility requirements.
- [ ] User/manager responses to agent requests are handled interactively in the UI, not just as a single output at the end.
- [ ] All agent outputs, tool call results, and reasoning are surfaced in real time, step-by-step, as the workflow progresses.
- [ ] The UI supports live logging, workflow visualization, and interactive response forms.
- [ ] All actions and responses are logged for auditability and compliance.
- [ ] Documentation and wireframes are updated to match the new pattern.

## Additions for Real-Time Agent Logging & Interactive UI

- [ ] Refactor agent orchestration so each agent step (including intermediate thoughts, reasoning, and tool call arguments/results) is appended to a shared log (e.g., `agent_log.csv` or in-memory state), not just final outputs.
- [ ] In `ui.py`, implement a real-time timeline/chat component that displays each agent step, tool call, and user/manager response as soon as it is logged, with timestamps and agent names.
- [ ] Ensure the UI can display agent “thoughts” and reasoning, not just tool call results—surface these as separate entries in the timeline/chat.
- [ ] Add a mechanism for agents to log intermediate reasoning steps (e.g., “Agent is waiting for user response”, “Agent is validating claim”, “Agent is retrying tool call”) to the shared log.
- [ ] Ensure the UI can show the current workflow state (e.g., “Waiting for manager response”, “Rights check in progress”) in real time.
- [ ] **Filter all agent log entries and pending actions by the selected `mutation_id` or `correlation_id` in the UI, so only the current/latest investigation run is shown.**
- [ ] Document the agent log format/schema and how it maps to UI components (timeline/chat, status indicators).
- [ ] Add a test scenario for real-time agent logging and interactive user/manager responses, including edge cases (e.g., delayed response, error/retry/escalation).
- [ ] Ensure all agent logs and user/manager responses are reconstructable for audit/compliance, including correlation IDs and timestamps.
- [ ] Update wireframes to show real-time log/timeline and interactive response forms side-by-side (if not already present).
