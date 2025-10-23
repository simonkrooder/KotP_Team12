---

## Agent Class Interfaces

Each agent is implemented as a Python class with a standard interface. The main method is `handle_request(context: dict) -> dict`, which processes the incoming request and returns a result dict.

### Context Object
- The `context` parameter is a Python dict containing all relevant data for the agent's task (e.g., mutation details, user info, prior findings).
- The result dict should include status, findings, errors, and any updates for the audit trail.

### Minimal Code Templates

#### InvestigationAgent
```python
class InvestigationAgent:
    def __init__(self, config):
        self.config = config  # environment/configuration

    def handle_request(self, context: dict) -> dict:
        # Orchestrate investigation workflow
        # Call other agents via Agent2Agent protocol
        # Update audit trail
        return {"status": "success", "action": "investigation_complete", "details": {}}
```

#### RightsCheckAgent
```python
class RightsCheckAgent:
    def __init__(self, mcv_client):
        self.mcv_client = mcv_client

    def handle_request(self, context: dict) -> dict:
        # Call MCV server to check authorizations
        # Return result and evidence
        return {"status": "success", "authorized": True, "evidence": {}}
```

#### RequestForInformationAgent
```python
class RequestForInformationAgent:
    def __init__(self, mcv_client):
        self.mcv_client = mcv_client

    def handle_request(self, context: dict) -> dict:
        # Send notification, validate claims, handle responses
        return {"status": "success", "response": "clarification received", "details": {}}
```

#### AdvisoryAgent
```python
class AdvisoryAgent:
    def __init__(self, mcv_client):
        self.mcv_client = mcv_client

    def handle_request(self, context: dict) -> dict:
        # Generate advisory report and recommendation
        return {"status": "success", "report": {}, "recommendation": "accept"}
```

### Usage
- Each agent is instantiated with required configuration or MCV client.
- The orchestrator (main workflow) calls `handle_request(context)` for each agent as needed.
- All agent actions and results are logged for auditability.
# Multi-Agent Access Control Architecture

## Introduction & Scope
This document describes the architecture for the Access Control Management System, which uses a multi-agent AI approach to automate, investigate, and advise on changes in business systems. The architecture covers agent roles, agent communication (Agent2Agent protocol), tool call usage, and the mapping between system workflow and implementation targets.

The scope includes:
- Multi-agent orchestration for change investigation and governance
- Agent2Agent protocol for agent communication and context passing
- Tool call integration for agent actions (e.g., data lookups, notifications)
- Data and UI foundation for traceability and user interaction

---


## Multi-Agent System Overview

The system is composed of specialized agents, each responsible for a distinct part of the change investigation and advisory process. The Investigation Agent orchestrates the flow, calling other agents as needed and updating the audit trail. All tool calls (e.g., data lookups, notifications, validations) are performed via a central MCV (Model-Controller-View) server, which acts as the execution and integration layer for agent actions.

---

## Agent Implementation Details

This section provides explicit details for implementing each agent, their responsibilities, message flows, and integration requirements. Use this as a blueprint for development and testing.

### Agent Classes and Responsibilities

- **Investigation Agent**
    - **Role:** Orchestrates the investigation workflow for each HR mutation.
    - **Responsibilities:**
        - Receives new mutation events (from UI or system trigger).
        - Maintains investigation context and status.
        - Delegates tasks to other agents (Rights Check, Request for Information, Advisory) via Agent2Agent protocol.
        - Updates the audit trail and mutation status after each step.
        - Handles error and exception flows (e.g., missing data, unresponsive agents).
    - **Inputs:** New HR mutation data, current investigation context.
    - **Outputs:** Updated investigation status, audit log entries, agent-to-agent messages.

- **Rights Check Agent**
    - **Role:** Validates whether the changer had the correct rights for the mutation.
    - **Responsibilities:**
        - Receives context from Investigation Agent.
        - Calls the MCV server to check authorizations (using user, role, and application data).
        - Returns result (authorized/unauthorized) and supporting evidence.
        - Logs all actions and results.
    - **Inputs:** User ID, mutation details, context.
    - **Outputs:** Authorization result, audit log entry.

- **Request for Information Agent**
    - **Role:** Gathers additional information from the changer and/or their manager.
    - **Responsibilities:**
        - Receives context and clarification requests from Investigation Agent.
        - Calls the MCV server to send (mocked) notifications or requests for clarification.
        - Validates claims (e.g., sick leave, vacation) via MCV server data lookups.
        - Handles and logs user/manager responses (via UI or mock interface).
        - Returns findings to Investigation Agent.
    - **Inputs:** Mutation context, clarification questions.
    - **Outputs:** User/manager responses, validation results, audit log entries.

- **Advisory Agent**
    - **Role:** Synthesizes all findings and generates a final advisory report.
    - **Responsibilities:**
        - Receives full investigation context and findings from Investigation Agent.
        - Calls the MCV server to generate/send a report (mocked or real).
        - Recommends an outcome (accept, reject, escalate/manual intervention).
        - Logs the advisory action and outcome.
    - **Inputs:** Investigation context, findings from other agents.
    - **Outputs:** Advisory report, recommendation, audit log entry.

### Agent2Agent Protocol Implementation

- All agent communication uses structured messages with:
    - Context (current investigation state, mutation data, prior findings)
    - Action/request type
    - Correlation ID (for traceability)
    - Timestamp
- Agents must log every received message, action taken, and response sent.
- All agent-to-agent messages are auditable and stored for traceability.

### MCV Server Integration

- Agents never access data or external systems directly; all tool calls go through the MCV server.
- The MCV server must expose endpoints for:
    - Authorization checks
    - Data lookups (users, roles, sick leave, vacation, etc.)
    - Sending/receiving (mocked) notifications
    - Report generation
- Every tool call and result must be logged by the MCV server for audit.

### Agent Lifecycle and Message Flow

1. **Trigger:** New HR mutation is created (via UI or system event).
2. **Investigation Agent:** Starts investigation, logs event, and requests rights check.
3. **Rights Check Agent:** Validates authorization, returns result.
4. **Investigation Agent:** Updates status. If unauthorized or unclear, requests clarification.
5. **Request for Information Agent:** Contacts changer/manager, validates claims, returns responses.
6. **Investigation Agent:** Updates context and status, then requests advisory.
7. **Advisory Agent:** Generates report and recommendation.
8. **Investigation Agent:** Finalizes status, logs all actions, and updates audit trail.

### Implementation Notes

- Each agent should be implemented as a class/module with a standard interface (e.g., `handle_request(context)`).
- Use environment variables for all Azure and deployment configuration (see `.env`).
- All status changes and agent actions must be logged in `audit_trail.csv` and/or the relevant mutation record.
- The system must be testable end-to-end with sample data and mock responses.

---

The following section continues with the original overview and high-level architecture.
### Agents and Responsibilities

- **Investigation Agent**: Orchestrates the investigation, maintains context, updates audit status, and coordinates other agents via Agent2Agent protocol.
- **Rights Check Agent**: Checks if the user who made a change had the correct rights, using tool calls to query authorizations.
- **Request for Information Agent**: Contacts the changer for clarification and validates their response (e.g., with sick leave data); also contacts the manager for validation of the changer’s claim.
- **Advisory Agent**: Generates a detailed advisory report and recommendation for the Change Controller, based on all gathered context.

All agent-to-agent communication is handled via the Agent2Agent protocol, ensuring modularity, traceability, and clear context passing.

---



## Agent2Agent Protocol

The Agent2Agent protocol is a structured messaging and context-passing mechanism that allows agents to:
- Send requests and receive responses asynchronously
- Pass investigation context, status, and findings
- Log all interactions for auditability

This protocol ensures modularity, traceability, and robust agent orchestration. All agent-to-agent messages are Python dicts (or JSON objects) with a formal schema (see below).

## Agent2Agent Protocol Message Schema (Quick Reference)

All agent-to-agent communication uses the following structured message schema for traceability, modularity, and auditability.

| Field          | Type      | Required | Description                                      |
|--------------- |---------- |----------|--------------------------------------------------|
| sender         | str       | Yes      | Name of sending agent                            |
| receiver       | str       | Yes      | Name of receiving agent                          |
| action         | str       | Yes      | Action/request type (e.g., 'check_rights')       |
| context        | dict      | Yes      | Investigation context, mutation data, findings    |
| correlation_id | str       | Yes      | Unique ID for tracing message flow               |
| timestamp      | str       | Yes      | ISO 8601 timestamp of message                    |
| status         | str       | Yes      | Message status (e.g., 'pending', 'success', 'error') |
| error          | dict      | No       | Error details if status is 'error'               |

#### Example Message (Rights Check Request)
```json
{
    "sender": "InvestigationAgent",
    "receiver": "RightsCheckAgent",
    "action": "check_rights",
    "context": {
        "mutation_id": "1001",
        "user_id": "u001",
        "system": "FinanceApp",
        "access_level": "Admin"
    },
    "correlation_id": "corr-abc123",
    "timestamp": "2025-10-23T09:00:00Z",
    "status": "pending"
}
```

#### Example Message (Rights Check Response)
```json
{
    "sender": "RightsCheckAgent",
    "receiver": "InvestigationAgent",
    "action": "check_rights_result",
    "context": {
        "authorized": true,
        "evidence": {"authorisation_id": "A001", "role_id": "R001"},
        "message": "User u001 is authorized as Admin for FinanceApp."
    },
    "correlation_id": "corr-abc123",
    "timestamp": "2025-10-23T09:00:01Z",
    "status": "success"
}
```

#### Example Message (Error)
```json
{
    "sender": "RightsCheckAgent",
    "receiver": "InvestigationAgent",
    "action": "check_rights_result",
    "context": {},
    "correlation_id": "corr-abc123",
    "timestamp": "2025-10-23T09:00:01Z",
    "status": "error",
    "error": {
        "code": 404,
        "message": "User not found"
    }
}
```

...existing code...

### Error Handling & Retry Flows

- If an agent fails to respond or returns an error, the orchestrator retries the request up to N times (default: 3).
- After N failures, the orchestrator logs the error, updates the audit trail, and escalates to manual intervention or the Advisory Agent.
- All errors, retries, and escalations are logged for auditability.

### Example Messages for Each Agent Interaction

**InvestigationAgent → RightsCheckAgent**
- Action: 'check_rights'
- Context: mutation details

**RightsCheckAgent → InvestigationAgent**
- Action: 'check_rights_result'
- Context: authorization result

**InvestigationAgent → RequestForInformationAgent**
- Action: 'request_clarification' or 'request_manager_validation'
- Context: mutation details, user/manager info

**RequestForInformationAgent → InvestigationAgent**
- Action: 'clarification_response' or 'manager_validation_response'
- Context: user/manager response, validation result

**InvestigationAgent → AdvisoryAgent**
- Action: 'generate_advisory_report'
- Context: full investigation findings

**AdvisoryAgent → InvestigationAgent**
- Action: 'advisory_report_result'
- Context: report summary, recommendation

All messages must include correlation_id and timestamp for traceability. All interactions are logged in the audit trail.

---


## Tool Calls, MCV Server, and Agent Actions

Agents do not execute tool calls directly. Instead, all tool calls are routed through the MCV server, which provides a unified interface for:
- Querying authorization data (for Rights Check Agent)
- Sending (mocked) notifications or emails (for Request for Information Agent)
- Validating claims with external data (e.g., sick leave)
- Generating and sending reports (for Advisory Agent)

The MCV server abstracts and centralizes all integrations, so agents remain modular and the system can be extended or modified without changing agent logic.

---



## MCV Server: Architectural Role & Responsibilities

The MCV (Model-Controller-View) server is a core component that must be implemented as part of this application. It is responsible for:
- Exposing endpoints or interfaces for all tool calls required by agents
- Handling data access, notifications, and report generation
- Logging all tool call requests and results for auditability
- Ensuring agents interact only with the MCV server, not with external systems or data sources directly

The MCV server enables clear separation of concerns, robust integration, and easy testing/mocking of all agent actions. It is the central integration and execution layer for all agent tool calls.

## MCV Server Contract (Quick Reference)

> **Note:** For full details and example requests/responses, see the "MCV Server API Specification" section below.

The MCV (Model-Controller-View) server is the central integration and execution layer for all agent tool calls. All agent actions (data lookups, notifications, validations, report generation) are routed through the MCV server.

### API Endpoints Summary Table

| Endpoint                      | Method | Purpose                        | Input Args (required)                | Output Fields                  | Error Codes |
|-------------------------------|--------|-------------------------------|--------------------------------------|-------------------------------|-------------|
| /api/authorization/check      | POST   | Check user authorization       | user_id, system, access_level        | authorized, evidence, message | 400,404,500 |
| /api/data/lookup              | POST   | Query data from CSV files      | file, query (dict of filters)        | results, message              | 400,404,500 |
| /api/notify/send              | POST   | Send (mocked) notification     | recipient_id, subject, body, context | status, message_id, message   | 400,404,500 |
| /api/report/generate          | POST   | Generate advisory report       | mutation_id, context                 | report_id, summary, recommendation, details | 400,404,500 |

Each endpoint returns a JSON object with the specified output fields. All errors are returned with an appropriate HTTP status code and error message.

For detailed input/output examples and error handling, see the "MCV Server API Specification" section below.

...existing code...

---

## Data & UI Foundation

- All data is stored in CSV files (e.g., `authorisations.csv`, `hr_mutations.csv`, `role_authorisations.csv`, `roles.csv`, `users.csv`, `sickLeave.csv`, `vacation.csv`).
- The UI (e.g., Streamlit) provides:
    - An HR mutation entry page (with dropdowns for users, applications, and reason field)
    - A chat/trigger page for interacting with and triggering the system
    - An insights page for investigation status, metrics, anomalies, and audit trails
- Audit trails are maintained for all agent actions and every status change in the investigation process. Every update to the status in the Audit/change_investigation column of hr_mutations.csv must be logged for full traceability.

---

## Workflow Mapping

The following table maps the system workflow and user stories (see `application.md`) to the agent architecture:

| Step | Agent(s) Involved | Description |
|------|-------------------|-------------|
| 1    | System, Investigation Agent | New HR mutation triggers investigation |
| 2    | Rights Check Agent, Investigation Agent | Rights are checked; if authorized, Investigation Agent updates `change_investigation` to 'Approved' |
| 3    | Request for Information Agent, Investigation Agent | Changer is contacted for clarification; claim validated (e.g., sick leave, vacation) |
| 4    | Request for Information Agent, Investigation Agent | Manager is contacted for validation |
| 5    | Advisory Agent, Investigation Agent | Advisory report is generated and sent with outcome: accept, reject/investigate, or manual intervention |

---

## Architecture Flow Diagram

Below is a simplified flow diagram of the multi-agent system:

```
User/Changer
    |
    v
HR Mutation Entry Page (UI)
    |
    v
Investigation Agent (orchestrator)
    |
    +--> Rights Check Agent (tool call: check rights)
    |
    +--> Request for Information Agent (tool call: contact changer, validate (e.g., sick leave, vacation), contact manager)
    |
    +--> Advisory Agent (tool call: generate/send report with outcome: accept, reject/investigate, or manual intervention)
    |
    v
Audit Trail & Insights Page
```

All agent-to-agent communication is via the Agent2Agent protocol, and all actions are logged for auditability.

---

## Front-End/UI Requirements

To support the agentic workflow, auditability, and demo/testability, the system must provide a user interface with the following features:

### 1. HR Mutation Entry Page
- Form for creating new HR mutations (dropdowns for user, application, reason, etc.).
- Triggers the Investigation Agent and starts the workflow.

### 2. HR Mutations Table
- Table view of all HR mutations with their current status (`change_investigation`).
- Supports filtering, sorting, and selection for further inspection.

### 3. Audit Trail Page
- For a selected mutation, displays the full audit trail: agent actions, status changes, timestamps.
- Enables step-by-step tracking of the investigation process.

### 4. Mocked User/Manager Response Page
- When the system is awaiting a user or manager response (e.g., `Awaiting User Response`, `Awaiting Manager Response`), the UI presents a form or button for a human to provide a mock response.
- This simulates email/notification interactions and allows the workflow to proceed without real email integration.
- All such interactions are logged in the audit trail for traceability.

### 5. Insights/Dashboard Page (Recommended)
- Shows metrics, status counts, anomalies, and investigation timelines.
- Useful for compliance, monitoring, and demonstration.

### 6. (Optional) Manual Trigger/Chat Page
- Allows manual triggering of agents or direct interaction for testing and debugging.

#### Mocking Email/Notification Interactions
- All agent requests for clarification or validation are surfaced in the UI, allowing a human to provide a response directly.
- No real email integration is required; all communication is handled via the UI and logged for auditability.

This UI design ensures the system is fully testable, auditable, and suitable for demonstration, while supporting all workflow and compliance requirements.

This architecture enables modular, auditable, and extensible change governance using a multi-agent system. Each agent is responsible for a clear part of the workflow, and the Agent2Agent protocol ensures robust communication and traceability. The design supports rapid development, easy testing/mocking, and future expansion.

---

## Architectural Decisions & Rationale

- **Python as the main language:** Chosen for rapid prototyping, strong AI/ML ecosystem, and compatibility with Azure AI SDKs.
- **Streamlit for UI:** Enables fast, interactive web UI development in Python, ideal for demos and internal tools.
- **Azure AI Agents/Projects SDK:** Used for agent orchestration, leveraging cloud-based AI and secure integration with Azure resources.
- **MCV (Model-Controller-View) Server:** Centralizes all tool calls, data access, and notifications, ensuring modularity, auditability, and easy mocking/testing.
- **CSV files for data:** Chosen for simplicity, transparency, and ease of manipulation in a demo/prototype context.
- **Agent2Agent protocol:** Ensures modular, auditable, and extensible agent communication.
- **Mocked notifications:** All email/notification flows are simulated in the UI for demo/testability.

## Assumptions & Extensibility Guidelines


---

## Security & Compliance Considerations

- **Sensitive Data Handling:**
    - All access control and HR data is stored in CSV files with strict access permissions.
    - Agents and the MCV server never access data directly; all access is mediated and logged.
    - Audit logs (`audit_trail.csv`) are protected and only accessible to authorized users.
- **Audit Log Protection:**
    - Every agent action and tool call is logged with timestamp, correlation ID, and status.
    - Audit logs are immutable and regularly backed up.
    - Access to audit logs is monitored and restricted.
- **Compliance Requirements:**
    - The system is designed for full traceability and explainability (auditability).
    - Data retention and deletion policies must comply with GDPR and other relevant regulations.
    - All user/manager responses and notifications are mocked for demo/testing; no real personal data is transmitted externally.
    - For production, replace CSVs with a secure database and implement real authentication/authorization.
- The UI is designed for demo/testability: all notifications and user/manager responses are mocked in the UI, not sent via real email or messaging systems.
- Every agent action and status change is logged in `audit_trail.csv` for full auditability and compliance.
- The Agent2Agent protocol and MCV server enforce modularity and separation of concerns; agents never access data or other agents directly.
- The project is structured for easy onboarding and handover, with all setup, environment, and workflow steps documented in `/docs/`.
- The UI supports filtering, sorting, and step-by-step audit trail navigation for transparency and usability.
- The UI must support all workflow states and status codes as described in the documentation.
- The data access layer uses pandas for CSV manipulation.
- The environment is managed with `python-dotenv` and a `.env` file in `/src/`.
- The main entry point for orchestration is `/src/agent_main.py`.
- All required packages are listed in `agentsetup.md` and must be installed for the system to function.

---


## MCV Server API Specification

The MCV (Model-Controller-View) server is the central integration and execution layer for all agent tool calls. All agent actions (data lookups, notifications, validations, report generation) are routed through the MCV server.

### API Endpoints Summary

| Endpoint                      | Method | Purpose                        | Input Args (required)                | Output Fields                  | Error Codes |
|-------------------------------|--------|-------------------------------|--------------------------------------|-------------------------------|-------------|
| /api/authorization/check      | POST   | Check user authorization       | user_id, system, access_level        | authorized, evidence, message | 400,404,500 |
| /api/data/lookup              | POST   | Query data from CSV files      | file, query (dict of filters)        | results, message              | 400,404,500 |
| /api/notify/send              | POST   | Send (mocked) notification     | recipient_id, subject, body, context | status, message_id, message   | 400,404,500 |
| /api/report/generate          | POST   | Generate advisory report       | mutation_id, context                 | report_id, summary, recommendation, details | 400,404,500 |

#### Endpoint Details

**/api/authorization/check**
- Input: user_id (str), system (str), access_level (str)
- Output: authorized (bool), evidence (object), message (str)
- Errors: 400 (bad input), 404 (not found), 500 (internal)

**/api/data/lookup**
- Input: file (str), query (dict)
- Output: results (list of dicts), message (str)
- Errors: 400, 404, 500

**/api/notify/send**
- Input: recipient_id (str), subject (str), body (str), context (dict, optional)
- Output: status (str), message_id (str), message (str)
- Errors: 400, 404, 500

**/api/report/generate**
- Input: mutation_id (str), context (dict)
- Output: report_id (str), summary (str), recommendation (str), details (dict)
- Errors: 400, 404, 500

#### Example Requests/Responses

See below for example JSON requests and responses for each endpoint:

```json
// /api/authorization/check
{
    "user_id": "u001",
    "system": "FinanceApp",
    "access_level": "Admin"
}
// Response
{
    "authorized": true,
    "evidence": {"authorisation_id": "A001", "role_id": "R001"},
    "message": "User u001 is authorized as Admin for FinanceApp."
}
```

```json
// /api/data/lookup
{
    "file": "sickLeave.csv",
    "query": {"UserID": "u001"}
}
// Response
{
    "results": [{"UserID": "u001", "StartDate": "2025-10-20", "EndDate": "2025-10-22", "Status": "approved"}],
    "message": "1 record found."
}
```

```json
// /api/notify/send
{
    "recipient_id": "u002",
    "subject": "Clarification Needed",
    "body": "Please clarify the reason for your recent HR change.",
    "context": {"mutation_id": "1001"}
}
// Response
{
    "status": "mocked",
    "message_id": "msg-12345",
    "message": "Notification displayed in UI for user u002."
}
```

```json
// /api/report/generate
{
    "mutation_id": "1001",
    "context": {"status": "Manager Responded", "findings": {"rights_check": true, "user_claim_valid": true}}
}
// Response
{
    "report_id": "rep-1001",
    "summary": "All checks passed. Change is valid.",
    "recommendation": "accept",
    "details": {"manager_response": "confirmed"}
}
```

### Audit Logging Policy

Every API call and result is logged to `audit_trail.csv` with:
- Timestamp
- Endpoint/method
- Input arguments
- Output/result
- Status (success/error)
- Correlation ID (if provided)

This ensures full traceability and compliance for all agent actions. All tool calls must be auditable and reconstructable from the audit trail.

---

## Tool Call Definitions

Agents interact with the MCV server exclusively for all tool calls. Below are the tool calls, their arguments, expected results, error handling, and mapping to agent responsibilities and workflow steps.

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

This mapping ensures every agent action is routed through the MCV server, fully auditable, and aligned with the workflow.
