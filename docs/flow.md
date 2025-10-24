
# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [toolcalls.md](toolcalls.md): MCP tool call protocol and agent tool call details
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

# End-to-End Agentic Access Control Demo: Implementation Flow

## 1. Overview
This document describes the canonical workflow and implementation plan for the Multi-Agent Access Control Demo, aligning the UI, agent orchestration, and auditability. It incorporates the latest architectural choices: local Python orchestration (no REST MCP server), UI-driven workflow, and full audit/logging.

## 2. High-Level Flow
1. **User adds a change (mutation) via the UI** (Streamlit), which writes a new row to `hr_mutations.csv`.
2. **Backend (orchestrator) detects the new mutation** and triggers the agent workflow:
    - InvestigationAgent starts the investigation.
    - RightsCheckAgent checks authorizations.
    - RequestForInformationAgent sends (mocked) notifications and awaits user/manager response.
    - AdvisoryAgent generates a final report.
3. **All agent tool calls and results are logged** to `audit_trail.csv`.
4. **Mocked notifications/emails** are surfaced as UI pages (e.g., "Pending Actions" or "Inbox" for users/managers).
5. **User/manager responses** are entered via the UI, which updates the CSVs and triggers the next agent step.
6. **All actions and status changes** are visible in the UI (audit trail, status dashboards).

## 3. Detailed Implementation Steps

### 3.1. UI (Streamlit)
- HR Mutation Entry: Form to add a new mutation (writes to `hr_mutations.csv`).
- HR Mutations Table: View/filter all mutations.
- Audit Trail: View all audit log entries.
- Mocked User/Manager Response: Page for users/managers to see and respond to pending notifications (simulates email/inbox).
- Insights/Dashboard: Metrics and charts on workflow status.
- Manual Trigger/Chat: (Optional) For dev/test.

### 3.2. Agent Orchestration
- Orchestrator runs as a background process or is triggered by UI actions (e.g., after mutation submission or response).
- Agents are instantiated as Python classes, not separate processes.
- Each agent step is triggered in sequence, passing context/results to the next agent.
- When a user/manager response is required, the workflow pauses and the UI surfaces the pending action.
- When the response is entered in the UI, the orchestrator resumes the workflow.

### 3.3. Tool Calls and Audit Logging
- All tool calls (data lookup, authorization, notification, report generation) are Python async functions registered with each agent.
- Every tool call and result (success or error) is logged to `audit_trail.csv` using the canonical protocol.
- The audit trail is visible in the UI.

### 3.4. Mocked Notifications/Emails
- When an agent needs to notify a user/manager, a record is written to a "pending actions" table or status in the CSV.
- The UI displays these as "inbox" items for the relevant user/manager.
- When the user/manager responds in the UI, the response is written to the CSV and the workflow continues.

### 3.5. Error Handling and Retries
- All tool calls are retried up to 3 times on error, with each attempt logged.
- If all retries fail, the workflow escalates (e.g., triggers AdvisoryAgent for manual intervention).

### 3.6. Extensibility
- To add a new agent or tool call, define the async function, register it, and update the documentation.
- The UI and orchestrator are designed to be modular and extensible.

## 4. Example Workflow
1. HR staff submits a mutation via the UI.
2. Orchestrator triggers InvestigationAgent, which logs its actions and may call RightsCheckAgent.
3. RightsCheckAgent checks authorization and logs results.
4. If clarification is needed, RequestForInformationAgent sends a notification (mocked as a UI action).
5. User/manager sees the pending action in the UI and responds.
6. Orchestrator resumes, AdvisoryAgent generates a report, and the workflow completes.
7. All steps are logged and visible in the UI.

## 5. Summary Table: Component Responsibilities
| Component         | Responsibility                                    |
|-------------------|---------------------------------------------------|
| UI (Streamlit)    | Mutation entry, audit trail, notifications, dashboard |
| Orchestrator      | Triggers agent workflow, manages state, logging   |
| Agents            | Investigation, rights check, RFI, advisory        |
| Data Layer        | CSV read/write, schema validation                 |
| Audit Trail       | Logs all actions, tool calls, and status changes  |

## 6. Notes
- The "MCP server" is now a local Python orchestration pattern, not a REST API.
- All communication and workflow logic is handled in-process via Python functions and the Azure SDK.
- The UI is the primary interface for demo, audit, and user/manager interaction.
- This pattern is demo/test focused, not production-hardened.

---

**This document is the canonical flow for the demo. All contributors and AI coding agents should follow it for consistent, auditable, and extensible development.**
