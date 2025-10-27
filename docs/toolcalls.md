
# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [flow.md](flow.md): Canonical workflow diagram
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

## Real-Time Pending Action Toolcall and UI Pattern

### New Toolcall: Pending Action (CSV-based Shared State)

To support real-time, auditable UI/agent interaction, a new pattern is implemented:

- **Shared State:** All pending agent actions (e.g., notifications, clarifications) are written to a CSV file (`pending_actions.csv`) in the `/data/` directory. Each row includes: `action_id`, `type`, `recipient_id`, `context`, `status`, `created_at`, `response`.
- **UI Polling:** The Streamlit UI polls this CSV every 2 seconds (using `st.experimental_rerun()` and `time.sleep()`) to check for new actions relevant to the current user/manager.
- **Real-Time Forms:** For each pending action, the UI displays a form for the user/manager to submit a response. On submission, the response is written to the CSV and the status is updated to `responded`.
- **Audit Logging:** All actions and responses are logged to `audit_trail.csv` for traceability.
- **Escalation/Reminders:** If an action remains `pending` for more than 10 minutes, the UI displays a warning and can trigger escalation logic.

#### Example Usage

```python
# Add a new pending action (agent/toolcall):
add_pending_action({
    'action_id': str(uuid.uuid4()),
    'type': 'send_notification',
    'recipient_id': 'manager1',
    'context': 'Clarification needed for mutation X',
    'status': 'pending',
    'created_at': datetime.utcnow().isoformat(),
    'response': ''
})

# UI polling and response (see ui.py):
actions = get_pending_actions(recipient_id=current_user_id, status='pending')
for action in actions:
    # Display form, on submit:
    update_action_response(action['action_id'], response)
    log_ui_audit(...)
```

#### Extensibility
- To add new real-time interactions, define new action types and update the UI to handle them.
- Document each new toolcall and UI pattern in this file and in `ui.py`.

# Agent Tool Call Protocol Specification (Azure SDK Pattern)

## Overview
All agent tool calls (data lookup, authorization, notification, report generation) are implemented as Python async functions and registered with the agent using the Azure SDK. Agents never access data or external systems directly; they interact with the registered tool functions. Every tool call and result is logged for auditability.

**Note:** The "MCP server" is now a local Python orchestration pattern, not a REST API. All orchestration and tool call execution is handled in-process via Python functions and the Azure SDK. All notifications and agent-to-user/manager communication are mocked and surfaced as UI pages (not real emails).


---

## MCP Server Contract (Quick Reference)

The MCP (Model Context Protocol) server is a core component that must be implemented as part of this application. It is responsible for:
- Exposing endpoints or interfaces for all tool calls required by agents
- Handling data access, notifications, and report generation
- Logging all tool call requests and results for auditability
- Ensuring agents interact only with the MCP server, not with external systems or data sources directly

The MCP server enables clear separation of concerns, robust integration, and easy testing/mocking of all agent actions. It is the central integration and execution layer for all agent tool calls.

### Tool Function Signatures Summary Table

| Function Name           | Purpose                        | Input Args (required)                | Output Fields                  | Error Handling |
|------------------------|-------------------------------|--------------------------------------|-------------------------------|----------------|
| check_authorization    | Check user authorization       | user_id, system, access_level        | authorized, evidence, message | Exception/log   |
| lookup_data            | Query data from CSV files      | file, query (dict of filters)        | results, message              | Exception/log   |
| send_notification      | Send (mocked) notification     | recipient_id, subject, body, context | status, message_id, message   | Exception/log   |
| generate_report        | Generate advisory report       | mutation_id, context                 | report_id, summary, recommendation, details | Exception/log   |

Each function returns a Python dict with the specified output fields. All errors are handled via exceptions and logging.

For detailed input/output examples and error handling, see the "MCP Orchestration Function Specification" section below.

---

## Tool Call List, Arguments, Results, Error Handling, and Agent Mapping

Agents interact with the MCP server exclusively for all tool calls. Below are the tool calls, their arguments, expected results, error handling, and mapping to agent responsibilities and workflow steps.

### Tool Call List

| Tool Call                | Endpoint                  | Agent(s)                | Purpose/Workflow Step                                 |
|--------------------------|---------------------------|-------------------------|------------------------------------------------------|
| Authorization Check      | /api/authorization/check  | RightsCheckAgent        | Validate user rights for a mutation                   |
| Data Lookup              | /api/data/lookup          | All agents              | Query CSV data (users, sick leave, vacation, etc.)    |
| Notification/Clarification | /api/notify/send        | RequestForInformationAgent | Send (mocked) notification to user/manager           |
| Report Generation        | /api/report/generate      | AdvisoryAgent           | Generate advisory report for controller               |

### Arguments, Results, Error Handling

#### Authorization Check
- **Arguments:** user_id (str), system (str), access_level (str)
- **Result:** authorized (bool), evidence (object), message (str)
- **Errors:** 400 (bad input), 404 (not found), 500 (internal)
- **Agent:** RightsCheckAgent
- **Workflow:** Step 2 (rights validation)

#### Data Lookup
- **Arguments:** file (str), query (dict)
- **Result:** results (list of dicts), message (str)
- **Errors:** 400, 404, 500
- **Agent:** All agents
- **Workflow:** Used for context, validation, and evidence gathering

#### Notification/Clarification Request
- **Arguments:** recipient_id (str), subject (str), body (str), context (dict, optional)
- **Result:** status (str: "sent" or "mocked"), message_id (str), message (str)
- **Errors:** 400, 404, 500
- **Agent:** RequestForInformationAgent
- **Workflow:** Step 3/4 (clarification, manager validation)

#### Report Generation
- **Arguments:** mutation_id (str), context (dict)
- **Result:** report_id (str), summary (str), recommendation (str), details (dict)
- **Errors:** 400, 404, 500
- **Agent:** AdvisoryAgent
- **Workflow:** Step 5 (advisory report)

### Error Handling
- All errors are returned in the result dict with status 'error' and error details.
- Agents must log all tool call errors and escalate if needed (e.g., manual intervention).
- The orchestrator retries failed tool calls up to N times (default: 3), then logs and escalates.

### Mapping to Agent Responsibilities & Workflow Steps

| Step | Agent(s)                | Tool Call(s)                |
|------|-------------------------|-----------------------------|
| 1    | InvestigationAgent      | Data Lookup                 |
| 2    | RightsCheckAgent        | Authorization Check, Data Lookup |
| 3    | RequestForInformationAgent | Notification, Data Lookup |
| 4    | RequestForInformationAgent | Notification, Data Lookup |
| 5    | AdvisoryAgent           | Report Generation, Data Lookup |

This mapping ensures every agent action is routed through the MCP server, fully auditable, and aligned with the workflow.

## Registered Tool Functions
| Function Name         | Purpose                        | Input Args (required)                | Output Fields                  |
|----------------------|-------------------------------|--------------------------------------|-------------------------------|
| check_authorization  | Check user authorization       | user_id, system, access_level        | authorized, evidence, message |
| lookup_data          | Query data from CSV files      | file, query (dict of filters)        | results, message              |
| send_notification    | Send (mocked) notification     | recipient_id, subject, body, context | status, message_id, message   |
| generate_report      | Generate advisory report       | mutation_id, context                 | report_id, summary, recommendation, details |


### Example Tool Function and Usage
```python
async def check_authorization(user_id: str, system: str, access_level: str) -> dict:
    # Implement logic to check authorization from CSVs
    # Return dict: {"authorized": True/False, "evidence": {...}, "message": str}
    ...

# Register with agent (see agent_example.py):
from azure.ai.agents.models import AsyncFunctionTool
toolset = AsyncFunctionTool(functions={check_authorization, ...})
```


## Canonical Agent Tool Call Pattern
```python
# Example: RightsCheckAgent using registered tool function
class RightsCheckAgent:
    def __init__(self, toolset):
        self.toolset = toolset

    async def handle_request(self, context):
        # Call the registered async tool function
        result = await self.toolset.check_authorization(
            user_id=context["user_id"],
            system=context["system"],
            access_level=context["access_level"]
        )
        # Log result to audit trail
        return {"status": "success", **result}
```


## Audit Logging Schema
Every tool call and result must be logged with:
- timestamp
- agent name
- function name
- input arguments
- output/result
- status (success/error)
- correlation_id (if provided)


## Error Handling & Retry
- Orchestrator retries failed tool calls up to 3 times, then escalates.
- All errors and retries are logged.


## Extensibility Guidelines
- To add a new tool call: define async function, input/output schema, register with agent, document in this file.
- To add a new agent: implement agent class, use canonical tool call pattern, update documentation.


## Testing & Mocking
- Tool calls can be mocked by replacing registered tool functions with test doubles.
- Use sample data and error cases to validate agent logic.



## Real-Time UI Interaction with Agents via Toolcalls

### Overview
To achieve real-time, interactive workflows between the UI and agents, the Streamlit UI must act as both the initiator and the responder for agent toolcalls. This enables users and managers to interact with agent requests, provide clarifications, and see results or notifications immediately in the UI.

### Implementation Details

#### 1. Toolcall-Driven UI Updates
- Each agent toolcall (e.g., `send_notification`, `request_clarification`, `request_manager_validation`) triggers a UI state change.
- When an agent needs user/manager input, it issues a toolcall (e.g., `send_notification`). Instead of sending an email, the backend logs the request and updates a shared state (e.g., a CSV, database, or in-memory store).
- The Streamlit UI polls or listens for new pending actions (e.g., notifications, clarifications) relevant to the current user/manager.
- When a pending action is detected, the UI displays a form or notification, allowing the user/manager to respond in real time.
- Upon submission, the UI writes the response back to the shared state, which the agent then consumes to continue its workflow.

#### 2. Streamlit UI Integration Pattern
- Use Streamlit session state or a lightweight backend (e.g., CSV, SQLite, or in-memory dict) to track pending agent actions and responses.
- For each workflow step:
    - The agent logs a toolcall (e.g., `send_notification`) with a unique correlation ID and context.
    - The UI displays a notification or form for the relevant user/manager, keyed by correlation ID.
    - The user/manager submits a response, which is logged and made available to the agent.
    - The agent polls for or is notified of the response and continues processing.
- All actions and responses are logged to the audit trail for traceability.

#### 3. Real-Time Feedback and State Synchronization
- Use Streamlit's `st.experimental_rerun()` or websocket-based callbacks (if using a backend) to refresh the UI when new agent actions or responses are available.
- Optionally, implement a lightweight polling mechanism (e.g., every few seconds) to check for new pending actions or updates.
- For multi-user scenarios, use user authentication or session IDs to filter and display only relevant actions/notifications.

#### 4. Example: Mocked Notification Workflow
1. Agent issues a `send_notification` toolcall with context (e.g., clarification needed for mutation X).
2. Backend logs the notification as pending in a shared store (e.g., `pending_notifications.csv`).
3. Streamlit UI detects the pending notification for the current user and displays a form.
4. User submits a response; UI writes it to `pending_notifications.csv` or a response store.
5. Agent reads the response, logs the result, and continues the workflow.
6. All steps are logged in `audit_trail.csv`.

#### 5. Error Handling and Retries
- If a user/manager does not respond within a timeout, the agent can escalate or retry, and the UI can display reminders.
- All errors, retries, and escalations are surfaced in the UI and logged.

#### 6. Extensibility
- To add new real-time interactions, define new toolcalls and corresponding UI forms/pages.
- Document each new interaction in this file and update the UI accordingly.

#### 7. References
- See `flow.md` for the canonical workflow.
- See `ui.py` for Streamlit implementation patterns.
- See `audit_trail.csv` for logging schema.

---
**Summary:**
Real-time UI/agent interaction is achieved by treating toolcalls as triggers for UI state changes, using a shared store for pending actions and responses, and ensuring all steps are logged and surfaced in the UI. This enables demo-friendly, auditable, and interactive workflows without external messaging systems.

---
**References:**
- See `architecture.md` for system diagrams and workflow.
- See `application.md` for user stories and acceptance criteria.

---
# DETAILED TODO/ACTION MAPPING (from application.md)

This list maps each major TODO/action point from `application.md` to its current implementation status and file locations. Use this as a living checklist for project status and onboarding.


## To Check: Architecture & Protocol Compliance (from architecture.md)

- [ ] Ensure all agent-to-agent communication uses the formal Agent2Agent protocol and message schema (`src/agent_protocol.py`).
- [ ] Guarantee all tool calls are routed through the MCP server and are fully logged for auditability (`src/mcv_server.py`).
- [ ] Maintain and update canonical workflow diagrams in `docs/visualFlowchart.mmd` as the workflow changes.
- [ ] Keep UI wireframes in `docs/wireframe.md` up to date with the actual UI implementation.
- [ ] Ensure all error/retry/escalation flows are implemented as described in `architecture.md` and are logged.
- [ ] Maintain audit logging policy and log rotation/archiving for `audit_trail.csv`.

## Multi-Agent System
- [ ] **Agent2Agent Protocol**
	- Agents are orchestrated in sequence in `src/agent_main.py` (function calls/context passing).
	- No explicit protocol abstraction; could be formalized if needed.

## Outstanding/Nice-to-Have

	- Current: Sequential orchestration in `agent_main.py`.
	- Next step: Implement a message-passing or protocol abstraction if needed for extensibility.
