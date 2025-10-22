# Application Documentation

## Product Overview

**Purpose:**  
Automate the detection, investigation, and advisory process for changes in business systems using a multi-agent AI architecture. All tool calls by agents are orchestrated through an MCV (Model-Controller-View) server, which acts as the central point for executing actions and integrating with data and notification services.

**Core Value:**  
- Reduce manual effort in change governance  
- Accelerate resolution cycles  
- Ensure compliance and auditability  
- Provide clear, explainable decision trails


**Key Workflow:**  
1. **Trigger:** A new HR mutation entry triggers the Investigation Agent.
2. **Rights Check:** The Rights Check Agent verifies if the changer had the correct rights (via MCV server tool call). If authorized, the Investigation Agent sets the `change_investigation` column to 'Approved' in `hr_mutations.csv` for that change.  
3. **User Clarification:** If not approved, the Request for Information Agent contacts the changer for clarification and validates the response (via MCV server tool calls, e.g., checking sick leave or vacation data).  
4. **Manager Validation:** The Request for Information Agent contacts the manager to validate the changer’s claim (via MCV server tool call).  
5. **Advisory:** The Advisory Agent generates a report and recommendation for the Change Controller (via MCV server tool call), with three possible outcomes: (1) accept the change, (2) reject and initiate further investigation, or (3) mark as correct but requiring manual intervention.

---


## Detailed System Flow

This section describes the step-by-step flow of the agentic investigation and advisory process:

1. **HR Mutation Entry:**
	- A user submits a new HR mutation via the entry page.
	- The mutation is recorded in `hr_mutations.csv` with an initial status (e.g., `Pending`).

2. **Investigation Agent Triggered:**
	- The Investigation Agent is automatically triggered by the new entry.
	- The status is updated to `Investigation Started`.

3. **Rights Check:**
	- The Rights Check Agent (via MCV server) checks if the changer has the correct rights for the change.
	- If authorized, the Investigation Agent sets the status to `Approved` and the process ends.
	- If not authorized, the status is set to `Clarification Requested`.

4. **User Clarification:**
	- The Request for Information Agent (via MCV server) sends a clarification request to the changer.
	- The status is set to `Awaiting User Response`.
	- When the user responds, the status is set to `User Responded`.
	- The agent validates the claim using available data (e.g., sick leave, vacation).
	- If the claim is invalid, the status is set to `Rejected - Invalid User Claim` and the process ends.
	- If the claim is valid, the status is set to `Manager Verification Requested`.

5. **Manager Verification:**
	- The Request for Information Agent (via MCV server) sends a verification request to the manager.
	- The status is set to `Awaiting Manager Response`.
	- When the manager responds, the status is set to `Manager Responded`.

6. **Advisory Report:**
	- The Advisory Agent (via MCV server) generates a report for the Change Controller, summarizing all findings.
	- The status is set to `Advisory Report Generated`.
	- The report includes a recommendation with one of three outcomes:
	  - `Accepted`: The change is accepted.
	  - `Rejected - Further Investigation`: The change is rejected and further investigation is required.
	  - `Manual Intervention Required`: The change is correct, but a human must take further action.

7. **Final Status:**
	- The Investigation Agent updates the status to the final outcome (`Accepted`, `Rejected - Further Investigation`, or `Manual Intervention Required`).

This flow ensures that every change is auditable, all decisions are explainable, and the process is fully automated except for cases requiring human intervention.

---

## User Stories (Implementation Targets)

- **As a System:**  
	I want to be triggered by a new change, so I can start the Investigation Agent.

- **As an Investigation Agent:**  
	I orchestrate the investigation, updating the audit status based on results from other agents via Agent2Agent protocol, so I can track context and insights.

- **As a Rights Check Agent:**  
	I check user rights for a particular application using an MCV tool call, and report findings to the Investigation Agent.

- **As a Request for Information Agent:**  
	I contact the changer for clarification, validate their response, and report back to the Investigation Agent.

- **As a Request for Information Agent:**  
	I contact the manager to validate the changer’s claim, and report back to the Investigation Agent.

- **As an Advisory Agent:**  
	I generate and send a detailed report to the Change Controller, then notify the Investigation Agent.

- **As a Changer:**  
	I want a clear email asking for my reason, so I can respond efficiently.

- **As a Manager:**  
	I want a simple yes/no validation request, so I can confirm or deny quickly.

- **As a Change Controller:**  
	I want an AI-generated advisory with evidence and a clear recommendation, so I can decide to accept, investigate, or correct the change.

- **As a Compliance Officer:**  
	I want full audit trails and explainability in the form of a logfile, so I can verify ethical and policy-compliant operation.

---



## Status Codes and Logging for Audit / change_investigation Column

Every time the status in the `Audit` (or `change_investigation`) column of `hr_mutations.csv` is updated, this change must be logged in the audit trail. This ensures full traceability and allows for step-by-step reconstruction of the investigation process for each change.

The following status codes are used to track the investigation state for each change:

| Status Code                    | Description                                                      |
|--------------------------------|------------------------------------------------------------------|
| Pending / New                  | New mutation, not yet processed                                  |
| Investigation Started          | Investigation Agent has started processing                       |
| Approved                       | Change is authorized and approved                                |
| Clarification Requested        | Clarification email sent to changer                              |
| Awaiting User Response         | Waiting for user to respond to clarification                     |
| User Responded                 | User has responded; claim is being validated                     |
| Manager Verification Requested | Manager is being asked to verify user’s claim                    |
| Awaiting Manager Response      | Waiting for manager to respond                                   |
| Manager Responded              | Manager has responded; agent is processing                       |
| Advisory Report Generated      | Advisory report has been generated and sent                      |
| Accepted                       | Change is accepted (final state)                                 |
| Rejected - Invalid User Claim  | User’s claim was invalid; change is rejected                     |
| Rejected - Further Investigation | Change is rejected; further investigation required             |
| Manual Intervention Required   | Change is correct, but requires human/manual action              |

---

## Actionable TODOs

---

## Front-End/UI Requirements

To support the agentic workflow and ensure the system is auditable, demo-ready, and testable, the application must provide a user interface with the following pages and features:

### 1. HR Mutation Entry Page
- Allows users to create a new HR mutation (with dropdowns for user, application, and reason fields).
- Submitting a new entry triggers the Investigation Agent and starts the workflow.

### 2. HR Mutations Table
- Displays all HR mutations with their current status (`change_investigation` column).
- Supports filtering and sorting by status, user, date, etc.
- Allows selection of a mutation to view its audit trail.

### 3. Audit Trail Page
- For a selected change, shows the full audit trail: all agent actions, status changes, and timestamps.
- Enables step-by-step tracking of the investigation process for each change.

### 4. Mocked User/Manager Response Page
- When the system is awaiting a response from a user or manager (e.g., status is `Awaiting User Response` or `Awaiting Manager Response`), the UI presents a form or button for a human to provide a mock response.
- This simulates email/notification interactions and allows the workflow to proceed without real email integration.
- All such interactions are logged in the audit trail for traceability.

### 5. Insights/Dashboard Page (Recommended)
- Shows metrics such as the number of changes in each status, average investigation time, and anomalies.
- Useful for compliance officers and for demoing system capabilities.

### 6. (Optional) Manual Trigger/Chat Page
- Allows manual triggering of agents or direct interaction with the system for testing and debugging.

#### Mocking Email/Notification Interactions
- All email or notification actions by agents are mocked: when an agent requests clarification or validation, the UI displays the request and allows a human to provide a response directly in the interface.
- No real email integration is required; all communication is handled via the UI and logged for auditability.

This UI design ensures the system is fully testable, auditable, and suitable for demonstration, while supporting all user stories and workflow requirements described above.

### Data & Foundation
- [ ] Verify and standardize the structure/content of all CSV files (`authorisations.csv`, `hr_mutations.csv`, `role_authorisations.csv`, `roles.csv`, `users.csv`, `sickLeave.csv`, `vacation.csv`).
- [ ] Add or update columns as needed (e.g., `Reason`, `ManagerID` in `hr_mutations.csv` and `users.csv`).
- [ ] Create an abstraction/data access layer for all data files.
- [ ] Review if the available data in all files is sufficient to answer all agent questions (e.g., can we always check sick leave, vacation, etc. for claims?).

### Multi-Agent System
- [ ] Implement the Investigation Agent to orchestrate the flow and update audit status.
	- [ ] When a change is approved, update the `change_investigation` column in `hr_mutations.csv` to 'Approved'.
- [ ] Implement the Rights Check Agent to validate user rights for changes (using MCV server for tool calls).
- [ ] Implement the Request for Information Agent to:
	- [ ] Contact the changer for clarification and validate their response (e.g., with sick leave or vacation data, using MCV server for tool calls).
	- [ ] Contact the manager for validation of the changer’s claim (using MCV server for tool calls).
- [ ] Implement the Advisory Agent to generate and send a detailed report to the Change Controller (using MCV server for tool calls), with three possible outcomes:
	- [ ] Accept the change (authorized)
	- [ ] Reject and initiate further investigation
	- [ ] Mark as correct but requiring manual intervention
- [ ] Implement Agent2Agent protocol for communication and context passing between agents.
- [ ] Create the MCV server to orchestrate and execute all tool calls for agents.

### User Interaction & Mocking
- [ ] Design and implement the HR mutation entry page (with dropdowns for users, applications, and reason field).
- [ ] Design and implement a chat/trigger page for interacting with and triggering the system.
- [ ] Mock all email/notification interactions (simulate as logs or UI notifications).
- [ ] Allow manual/mock responses for user and manager in the UI for testing.

### Audit & Insights
- [ ] Implement audit trail logging for all agent actions and every status change in the investigation process.
- [ ] Design and implement an insights page to display investigation status, metrics, anomalies, and audit trails.

### Testing & Validation
- [ ] Mock all system interactions for end-to-end testing.
- [ ] Validate the system workflow with sample data and edge cases.