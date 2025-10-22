
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

**Protocol Features:**
- Each agent exposes a standard interface for receiving requests and returning results
- Messages include context, action, and correlation IDs for traceability
- All agent actions and status changes are logged

---


## Tool Calls, MCV Server, and Agent Actions

Agents do not execute tool calls directly. Instead, all tool calls are routed through the MCV server, which provides a unified interface for:
- Querying authorization data (for Rights Check Agent)
- Sending (mocked) notifications or emails (for Request for Information Agent)
- Validating claims with external data (e.g., sick leave)
- Generating and sending reports (for Advisory Agent)

The MCV server abstracts and centralizes all integrations, so agents remain modular and the system can be extended or modified without changing agent logic.

---

## MCV Server Implementation

The MCV (Model-Controller-View) server is a core component that must be implemented as part of this application. It is responsible for:
- Exposing endpoints or interfaces for all tool calls required by agents
- Handling data access, notifications, and report generation
- Logging all tool call requests and results for auditability
- Ensuring agents interact only with the MCV server, not with external systems or data sources directly

The MCV server enables clear separation of concerns, robust integration, and easy testing/mocking of all agent actions.

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

## Conclusion

This architecture enables modular, auditable, and extensible change governance using a multi-agent system. Each agent is responsible for a clear part of the workflow, and the Agent2Agent protocol ensures robust communication and traceability. The design supports rapid development, easy testing/mocking, and future expansion.
