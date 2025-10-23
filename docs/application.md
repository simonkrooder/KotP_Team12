
# Quickstart & Onboarding

To get started with the Multi-Agent Access Control Demo:

1. **Clone the repository** and review the `/docs/` directory for architecture, approach, and setup.
2. **Install Python 3.10+** and all dependencies listed in `requirements.txt`.
3. **Copy `/src/.env.example` to `/src/.env`** and fill in all required environment variables (see below).
4. **Never commit real `.env` files or secrets to version control.** Always use `.env.example` for onboarding and update it whenever a new variable is added.
5. **Use `python-dotenv` to load environment variables** in all entrypoints, and reference them in code using `os.getenv()`.
6. **Ensure all CSV data files are present** in `/data/` and match the documented schema.
7. **Run the main orchestrator** as described below. (No separate MCP server is required; all orchestration is local using the Azure SDK. The "MCP server" is now a local Python orchestration pattern, not a REST API. All notifications and agent-to-user/manager communication are mocked and surfaced as UI pages.)

For more details on agent implementation, see the "Agent Implementation Pattern" section below and `/docs/architecture.md`.

---

## Environment Variables

The following environment variables must be set in `/src/.env` for the system to function:

| Variable                        | Description                                                      |
|----------------------------------|------------------------------------------------------------------|
| AGENT_MODEL_DEPLOYMENT_NAME      | Name of the Azure OpenAI deployment for agents                   |
| PROJECT_ENDPOINT                 | Base URL for the Azure AI Project or MCP server                  |
| AZURE_SUBSCRIPTION_ID            | Azure subscription ID for resource access                        |
| AZURE_RESOURCE_GROUP_NAME        | Azure resource group name                                        |
| MCP_SERVER_URL                   | (Legacy) URL for the local MCP server (not used in Azure SDK-based pattern)    |
| AGENT_TEMPERATURE (optional)     | Temperature for agent model calls (float, default: 0.2)          |

**Setup:**
1. Copy `/src/.env.example` to `/src/.env` and fill in the required values.
2. Never commit real `.env` files or secrets to version control.
3. Update `.env.example` whenever a new variable is added.

**Troubleshooting:**
- If you encounter schema validation errors when reading or writing CSVs, check that your data files match the schemas in `/docs/csv_schemas.md`.
If you encounter errors with Azure model calls, verify your `.env` file and Azure resource access.
If agent tests are not running, ensure your test files and classes are named correctly and use `python -m unittest discover`.
For agent usage patterns, see `/examples/agent_usage_example.py`.
For the canonical agent pattern, see `/docs/architecture.md` and `/docs/application.md`.
# Onboarding: Implementing and Extending Agents

To implement or extend an agent:

1. Create a new Python class (e.g., `InvestigationAgent`) in `/src/`.
2. Implement a `handle_request(context)` method.
3. In `handle_request`, use the Azure AI SDK (see example in `architecture.md`) to call the appropriate Azure-hosted model, using credentials from `.env`.
4. Register all tool calls (data lookup, authorization, notification, report generation) as Python async functions with the agent using the Azure SDK. Do not use REST endpoints for tool calls.
5. Do not register or persist agents in Azure; all orchestration is local.
6. Use the structure and best practices from `src/old/agent_example.py` as a template for model calls and tool integration.
6. Add or update docstrings to clarify the agent's pattern and responsibilities.
7. Add tests and example usage for your agent.

This ensures all agents follow the correct pattern and are easy to maintain and extend.
# Agent Implementation Pattern: Local Class, Azure Model Inference


**Agents in this project are implemented as local Python classes, using the Azure SDK for orchestration and tool call registration.**

**Note:** The "MCP server" is now a local Python orchestration pattern, not a REST API. All agent-to-agent and agent-to-tool communication is handled in-process via Python functions and the Azure SDK. All notifications and agent-to-user/manager communication are mocked and surfaced as UI pages (not real emails).

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
    - Calls the MCP server to check authorizations (using user, role, and application data).
        - Returns result (authorized/unauthorized) and supporting evidence.
        - Logs all actions and results.
    - **Inputs:** User ID, mutation details, context.
    - **Outputs:** Authorization result, audit log entry.

- **Request for Information Agent**
    - **Role:** Gathers additional information from the changer and/or their manager.
    - **Responsibilities:**
        - Receives context and clarification requests from Investigation Agent.
    - Calls the MCP server to send (mocked) notifications or requests for clarification.
    - Validates claims (e.g., sick leave, vacation) via MCP server data lookups.
        - Handles and logs user/manager responses (via UI or mock interface).
        - Returns findings to Investigation Agent.
    - **Inputs:** Mutation context, clarification questions.
    - **Outputs:** User/manager responses, validation results, audit log entries.

- **Advisory Agent**
    - **Role:** Synthesizes all findings and generates a final advisory report.
    - **Responsibilities:**
        - Receives full investigation context and findings from Investigation Agent.
    - Calls the MCP server to generate/send a report (mocked or real).
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

### MCP Server Integration

- Agents never access data or external systems directly; all tool calls go through the MCP server.
- The MCP server must expose endpoints for:
    - Authorization checks
    - Data lookups (users, roles, sick leave, vacation, etc.)
    - Sending/receiving (mocked) notifications
    - Report generation
- Every tool call and result must be logged by the MCP server for audit.

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

- Each agent (e.g., InvestigationAgent, RightsCheckAgent) is a Python class with a `handle_request(context)` method.
- When handling a request, the agent uses the Azure AI SDK (with credentials from `.env`) to call an Azure-hosted model endpoint for reasoning, decision-making, or text generation.
- All tool calls (data lookup, authorization, notification, report generation) are implemented as Python async functions and registered with the agent using the Azure SDK. There is no REST MCP server; all orchestration and tool call execution is local.
- No persistent agent registration or orchestration is performed in Azure. All agent orchestration, message passing, and workflow logic is handled locally in Python.
- The code structure follows the pattern in `src/old/agent_example.py`, with orchestration and message passing handled locally.
- This approach allows for flexible, testable, and auditable agent logic, while leveraging the power of Azure-hosted models for intelligence.
- Use environment variables for all Azure and deployment configuration (see `.env`).
- All status changes and agent actions must be logged in `audit_trail.csv` and/or the relevant mutation record.
- The system must be testable end-to-end with sample data and mock responses.

**Summary:**
> Agents are local Python classes that use Azure-hosted models for inference. All orchestration and workflow logic is local. No persistent agent registration in Azure.

See `flow.md` for the canonical workflow and UI/agent integration pattern.

# Application Documentation

## Project Review & Progress Tracking
## Code Review & Pair Programming Policy
## Continuous Documentation Updates
## Sample Data & Test Scenarios
## End-to-End Demo Flow Prioritization
## Contributor Guidance: Clarifying Questions & Assumptions
## Version Control Branching & Merging Policy
## Acceptance Criteria & User Story Refinement
## Keeping the AI Coding Assistant Up to Date

To maximize the effectiveness of the AI coding assistant:
- Regularly update documentation and checklists with new requirements, architecture changes, and lessons learned
- Summarize major changes and decisions in the changelog or dev diary
- Ensure the AI assistant is provided with the latest context, including updated `/docs/`, `/src/`, and `/data/` files
- Review and refresh the assistant’s context window at the start of each major development phase

This practice ensures the assistant remains a valuable, context-aware contributor throughout the project.

Acceptance criteria and user stories will be:
- Reviewed at the start of each sprint or milestone
- Updated as requirements evolve or new insights are gained
- Used as the basis for UI acceptance and demo validation
- Documented in `/docs/application.md` and referenced in `/docs/TODO.md`

This ensures the project remains aligned with user needs and stakeholder expectations.

To maintain code quality and enable safe collaboration:
- Use feature branches for all major features, bug fixes, or experiments
- Name branches descriptively (e.g., `feature/agent2agent-protocol`)
- Open pull requests for all merges into `master` or main branches
- Require code review and successful tests before merging
- Resolve conflicts and document merge decisions in the changelog

This policy ensures a clean, auditable project history and reduces integration risks.

Contributors are encouraged to:
- Ask clarifying questions early and often, especially when requirements or workflows are unclear
- Document all assumptions in code comments, pull requests, or the changelog
- Use the project chat or issue tracker for open questions
- Review and update assumptions as new information becomes available

This practice reduces misunderstandings and helps maintain project clarity.

The team will prioritize building complete, working end-to-end demo flows before focusing on optimization or refactoring. This approach ensures:
- Early validation of the full system
- Rapid feedback on integration points
- Clear demonstration value for stakeholders

Optimization and refactoring will be scheduled only after the main demo flows are functional and tested.

Sample data is provided in the `/data/` directory:
- `users.csv`, `hr_mutations.csv`, `authorisations.csv`, `role_authorisations.csv`, `roles.csv`, `sickLeave.csv`, `vacation.csv`, `audit_trail.csv`

Test scenarios should be created early and used to validate agent workflows and UI pages. Example scenarios:
- HR mutation with valid/invalid rights
- Sick leave or vacation claim validation
- Manager approval/denial
- End-to-end audit trail reconstruction

Developers should:
- Add new sample data as new features or edge cases are implemented
- Use these scenarios for manual and automated testing
- Document new scenarios in this section as the project evolves

This ensures robust validation and demo readiness from the start.

To prevent documentation from falling behind the codebase:
- Update relevant documentation files with every significant code or workflow change.
- Assign responsibility for documentation updates as part of each pull request or feature branch.
- Review documentation as part of code review and before merging.
- Use clear commit messages to indicate documentation changes.
- Periodically audit documentation for accuracy and completeness.

This ensures that all contributors and the AI coding assistant have access to the latest information.

To ensure code quality and reduce defects in critical modules (such as the Agent2Agent protocol and MCP server):
- All changes to these modules must undergo code review by at least one other contributor (AI or human).
- Pair programming is encouraged for complex or high-impact features.
- Use pull requests for all major changes, and require approval before merging.
- Reviewers should check for correctness, clarity, test coverage, and documentation updates.
- Document review outcomes and decisions in the changelog or dev diary.

This policy helps maintain high standards and shared understanding for the most important parts of the system.

To ensure steady progress and alignment, the team will:
- Conduct weekly standup meetings (in-person or async) to review the canonical build checklist in `/docs/TODO.md`.
- Use the checklist to track completed, in-progress, and blocked items.
- Assign action items and update blockers in a running changelog or dev diary.
- Encourage async check-ins via project chat or issue tracker for distributed contributors.
- Review and update the checklist at the start of each sprint or milestone.

This process ensures transparency, accountability, and continuous momentum throughout the project lifecycle.


## Model Selection Rationale & Update Process

### Rationale for Model and Technology Choices

- **Python 3.12**: Chosen for its strong ecosystem, rapid prototyping capabilities, and compatibility with AI/ML and data tools.
- **Streamlit**: Enables fast, interactive UI development in Python, ideal for demos and internal tools.
- **Azure AI Agents SDK**: Used for agent orchestration, leveraging cloud-based AI and secure integration with Azure resources.

**Azure AI SDK Tool Call Registration**: All agent tool calls (authorization, data lookup, notification, report generation) are implemented as Python async functions and registered with the agent using the Azure SDK. There is no REST MCP server; all orchestration and tool call execution is local and auditable. This ensures every agent action is modular, traceable, and compliant.

For the full MCP tool call protocol specification, see [`toolcalls.md`](toolcalls.md).
- **CSV Data Storage**: Selected for transparency, ease of manipulation, and suitability for prototyping and demos.
- **Pandas**: Used for robust, efficient CSV data access and manipulation.
- **python-dotenv**: Simplifies environment variable management for local and cloud deployments.

These choices prioritize rapid development, transparency, and ease of onboarding for new contributors, while ensuring the system is extensible and cloud-ready.

### Model/Component Update Process

1. **Review Requirements**: Reassess project requirements and stakeholder needs before considering a model or technology update.
2. **Evaluate Alternatives**: Research and compare new models, libraries, or frameworks for suitability, performance, and compatibility.
3. **Prototype & Test**: Implement a proof-of-concept or test integration in a feature branch. Validate with sample data and workflows.
4. **Document Changes**: Update `/docs/application.md` and `/docs/architecture.md` with rationale, migration steps, and any new dependencies.
5. **Code Review & Approval**: Submit changes via pull request. Require review and approval from at least one other contributor.
6. **Update Onboarding**: Revise `/docs/CONTRIBUTING.md` and `/docs/agentsetup.md` as needed to reflect new setup or usage instructions.
7. **Communicate & Train**: Announce changes in project meetings or chat, and provide guidance for contributors as needed.

This process ensures that all model and technology updates are transparent, justified, and well-documented, minimizing disruption and technical debt.

---


**Purpose:**  
Automate the detection, investigation, and advisory process for changes in business systems using a multi-agent AI architecture. All tool calls by agents are orchestrated as Python async functions registered with the agent using the Azure SDK. There is no REST MCP server; all orchestration, context management, and integration with data and notification services is handled locally in Python. This ensures every agent interaction is modular, auditable, and compliant, providing a unified interface for all tool calls and workflow orchestration.

**Core Value:**  
- Reduce manual effort in change governance  
- Accelerate resolution cycles  
- Ensure compliance and auditability  
- Provide clear, explainable decision trails


**Key Workflow:**  
1. **Trigger:** A new HR mutation entry triggers the Investigation Agent.
2. **Rights Check:** The Rights Check Agent verifies if the changer had the correct rights (via registered tool call). If authorized, the Investigation Agent sets the `change_investigation` column to 'Approved' in `hr_mutations.csv` for that change.  
3. **User Clarification:** If not approved, the Request for Information Agent contacts the changer for clarification and validates the response (via registered tool calls, e.g., checking sick leave or vacation data).  
4. **Manager Validation:** The Request for Information Agent contacts the manager to validate the changer’s claim (via registered tool call).  
5. **Advisory:** The Advisory Agent generates a report and recommendation for the Change Controller (via registered tool call), with three possible outcomes: (1) accept the change, (2) reject and initiate further investigation, or (3) mark as correct but requiring manual intervention.

---


## Detailed System Flow


This section describes the step-by-step flow of the agentic investigation and advisory process:

---

## Practical Multi-Agent Workflow Example

This example demonstrates how the multi-agent system processes a new HR mutation from start to finish, using sample data and showing each agent's actions and message flows.

### Example Scenario

- **User:** Alice (UserID: U123)
- **Application:** Payroll
- **Mutation:** Change salary for Bob (UserID: U456)
- **Reason:** "Correction after sick leave"

#### Step 1: HR Mutation Entry
- Alice submits a mutation via the UI.
- Entry is added to `hr_mutations.csv`:
	- `changer=U123`, `target=U456`, `application=Payroll`, `reason=Correction after sick leave`, `status=Pending`
- Audit trail logs: "Mutation submitted by Alice (U123) for Bob (U456) in Payroll."

#### Step 2: Investigation Agent Triggered
- Investigation Agent detects the new entry.
- Updates status to `Investigation Started`.
- Logs: "Investigation started for mutation X."

#### Step 3: Rights Check Agent
- Investigation Agent sends a message (via Agent2Agent protocol) to Rights Check Agent:
	- Context: mutation details, changer ID, application
	- Correlation ID: auto-generated
-- Rights Check Agent calls MCP server to check if Alice (U123) is authorized for this change.
-- MCP server queries `authorisations.csv` and `role_authorisations.csv`.
- Rights Check Agent returns result:
	- If authorized: Investigation Agent sets status to `Approved`, logs action, and process ends.
	- If not authorized: Investigation Agent sets status to `Clarification Requested`, logs action.

#### Step 4: Request for Information Agent (User Clarification)
- Investigation Agent sends a clarification request to Request for Information Agent.
-- Request for Information Agent calls MCP server to send a (mocked) notification to Alice.
-- Status set to `Awaiting User Response`.
-- Alice responds via UI (mocked response captured by MCP server).
-- Request for Information Agent validates claim (e.g., checks `sickLeave.csv` for Bob).
- If claim invalid: status set to `Rejected - Invalid User Claim`, logs action, process ends.
- If claim valid: status set to `Manager Verification Requested`, logs action.

#### Step 5: Request for Information Agent (Manager Verification)
- Request for Information Agent sends a verification request to Bob's manager (e.g., ManagerID: M789).
- MCP server sends (mocked) notification to manager.
- Status set to `Awaiting Manager Response`.
- Manager responds via UI (mocked response captured).
- Status set to `Manager Responded`, logs action.

#### Step 6: Advisory Agent
- Investigation Agent sends full context and findings to Advisory Agent.
- Advisory Agent calls MCP server to generate a report and recommendation.
- Report includes summary, findings, and recommended outcome (e.g., `Accepted`).
- Status set to `Advisory Report Generated`, logs action.

#### Step 7: Finalization
- Investigation Agent updates `hr_mutations.csv` and `audit_trail.csv` with final status and all actions.
- UI displays the full audit trail and advisory report for review.

---

**This example can be used as a test case for development and demo purposes.**

1. **HR Mutation Entry:**
	- A user submits a new HR mutation via the entry page.
	- The mutation is recorded in `hr_mutations.csv` with an initial status (e.g., `Pending`).

2. **Investigation Agent Triggered:**
	- The Investigation Agent is automatically triggered by the new entry.
	- The status is updated to `Investigation Started`.

3. **Rights Check:**
    -- The Rights Check Agent (via MCP server) checks if the changer has the correct rights for the change.
	- If authorized, the Investigation Agent sets the status to `Approved` and the process ends.
	- If not authorized, the status is set to `Clarification Requested`.

4. **User Clarification:**
    -- The Request for Information Agent (via MCP server) sends a clarification request to the changer.
	- The status is set to `Awaiting User Response`.
	- When the user responds, the status is set to `User Responded`.
	- The agent validates the claim using available data (e.g., sick leave, vacation).
	- If the claim is invalid, the status is set to `Rejected - Invalid User Claim` and the process ends.
	- If the claim is valid, the status is set to `Manager Verification Requested`.

5. **Manager Verification:**
    -- The Request for Information Agent (via MCP server) sends a verification request to the manager.
	- The status is set to `Awaiting Manager Response`.
	- When the manager responds, the status is set to `Manager Responded`.

6. **Advisory Report:**
    -- The Advisory Agent (via MCP server) generates a report for the Change Controller, summarizing all findings.
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

-- **As a Rights Check Agent:**  
    I check user rights for a particular application using an MCP tool call, and report findings to the Investigation Agent.

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




## Audit Trail & Logging Format

Every agent action and status change must be logged in `audit_trail.csv` for full traceability and compliance. This enables step-by-step reconstruction of the investigation process for each change.

### Required Fields for Each Audit Log Entry

| Field      | Type     | Required | Description                                         |
|------------|----------|----------|-----------------------------------------------------|
| AuditID    | string   | Yes      | Unique identifier for each audit log entry          |
| MutationID | string   | Yes      | Reference to the HR mutation being audited          |
| Timestamp  | datetime | Yes      | ISO 8601 timestamp of the action                    |
| OldStatus  | string   | No       | Previous status before the change                   |
| NewStatus  | string   | Yes      | New status after the change                         |
| Agent      | string   | Yes      | Name of the agent or process making the change      |
| Comment    | string   | No       | Additional context or reason for the status change  |

**Example row:**
1,123,2025-10-22T10:00:00,Pending,Investigation Started,InvestigationAgent,"Triggered by new entry"

### Logging Policy
- Log every agent action and every status change in the investigation process.
- Log all tool call requests and results (including errors) with correlation IDs for traceability.
- Ensure audit logs are immutable and only accessible to authorized users.
- All audit log entries must be written to `audit_trail.csv` immediately after the action occurs.

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


## Technology Stack & Integration Details

- **Programming Language:** Python 3.10+
- **UI Framework:** Streamlit
- **AI/Agent Framework:** Azure AI Agents SDK (`azure-ai-agents`, `azure-ai-projects`)
- **Authentication:** Azure Identity (`azure-identity`)
- **Data Storage:** CSV files in `/data/`
- **Environment Management:** python-dotenv, `.env` file in `/src/`
- **Other Libraries:** pandas (data access), logging

### Integration Points
- All agent actions and tool calls are routed through the MCP server.
- The UI interacts with the agent system via API/tool calls (mocked for demo).
- All notifications and emails are simulated in the UI for traceability.



## Deployment Instructions

### Local Deployment (Quick Reference)
1. **Install Python 3.10+** and all required packages:
    - `pip install -r requirements.txt`
2. **Set up environment variables:**
    - Copy `/src/.env.example` to `/src/.env` and fill in required values.
3. **Ensure all CSV data files are present** in `/data/`.
4. **Start the MCP server:**
    - `python src/mcp_server.py`
5. **Start the main orchestrator:**
    - `python src/agent_main.py`
6. **Start the Streamlit UI:**
    - `streamlit run src/ui.py`
    - Access the UI at `http://localhost:8501`

### Detailed Local Setup Steps

#### 1. Environment Setup
- Install Python 3.10+ and required packages (see `agentsetup.md`).
- Create and populate `/src/.env` with Azure credentials and deployment info.
- Ensure all CSV data files are present in `/data/`.
- Add `.env` to `.gitignore`.

#### 2. Start the MCP Server
- Run the MCP server (e.g., `python src/mcp_server.py`).
- Confirm endpoints are available (see API spec in `architecture.md`).

#### 3. Launch Agents
- Start the main orchestrator: `python src/agent_main.py`.
- Agents will be initialized and registered automatically.

#### 4. Start the Streamlit UI
- Run: `streamlit run src/ui.py` (or the relevant UI entrypoint).
- Access the UI in your browser (default: `localhost:8501`).


### Troubleshooting Tips
- If endpoints are not available, check server logs and port configuration.
- If agents fail to initialize, verify `.env` and data files.
- For UI issues, ensure Streamlit is installed and all dependencies are met.
- For data errors, check CSV file formats and required columns.

---

## Testing & Validation Strategy

### Test Plan
- **Unit Tests:** Test each agent class and MCP server endpoint in isolation.
- **Integration Tests:** Test agent workflows with sample data and mock tool calls.
- **End-to-End Tests:** Simulate a full HR mutation workflow from entry to advisory report.

### Sample Test Data & Expected Outcomes
- Use provided sample rows in documentation for each CSV file.
- Validate status transitions and audit trail logging for each workflow step.

### Mocking User/Manager Responses & Tool Calls
- All notifications and responses are mocked in the UI (no real email integration).
- Use UI forms/buttons to simulate user/manager responses.
- Tool calls to the MCP server can be mocked for testing error handling and edge cases.

---

## Data Model & CSV Schemas

### authorisations.csv
- **Purpose:** Tracks user-system authorizations for access control.
- **Columns:**
    - AuthorisationID (str, required, unique)
    - UserID (str, required, FK to users.csv)
    - RoleID (str, required, FK to roles.csv)
    - System (str, required)
    - AccessLevel (str, required: Admin/User/Viewer)
    - GrantedBy (str, required, FK to users.csv)
    - GrantedOn (date, required, YYYY-MM-DD)
    - ExpiresOn (date, optional, YYYY-MM-DD or empty)
    - Status (str, required: Active/Revoked)
- **Sample row:**
    - A001,u001,R001,FinanceApp,Admin,grace,2020-01-15,,Active

### hr_mutations.csv
- **Purpose:** Audit log of all HR data changes and mutations.
- **Columns:**
    - MutationID (str/int, required, unique)
    - Timestamp (datetime, required, ISO 8601)
    - ChangedBy (str, required, FK to users.csv)
    - ChangedFor (str, required, FK to users.csv)
    - ChangeType (str, required: Create/Update/Terminate)
    - FieldChanged (str, required)
    - OldValue (str, optional)
    - NewValue (str, required)
    - Environment (str, required)
    - Metadata (str/JSON, optional)
    - change_investigation (str, required, status code)
    - Reason (str, required)
    - ManagerID (str, required, FK to users.csv)
- **Sample row:**
    - 1001,2025-10-23T09:00:00Z,u001,u002,Update,Salary,50000,52000,HRProd,"{}",Pending,Annual raise,heidi

### role_authorisations.csv
- **Purpose:** Maps roles to system access levels.
- **Columns:**
    - RoleID (str, required, FK to roles.csv)
    - System (str, required)
    - AccessLevel (str, required)
- **Sample row:**
    - R001,FinanceApp,Admin

### roles.csv
- **Purpose:** Master data for job roles and their default system access.
- **Columns:**
    - RoleID (str, required, unique)
    - RoleName (str, required)
    - Department (str, required)
    - Description (str, required)
    - DefaultAuthorisations (str, required, e.g. System:AccessLevel)
- **Sample row:**
    - R001,Finance Admin,Finance,Full admin rights to FinanceApp,"FinanceApp:Admin"

### users.csv
- **Purpose:** Master employee data for all users.
- **Columns:**
    - UserID (str, required, unique)
    - Name (str, required)
    - Department (str, required)
    - JobTitle (str, required)
    - Status (str, required: Active/Terminated/Removed)
    - Email (str, required)
    - Manager (str, required, FK to users.csv)
    - HireDate (date, required, YYYY-MM-DD)
    - TerminationDate (date, optional, YYYY-MM-DD or empty)
    - Environment (str, required)
- **Sample row:**
    - u001,Alice Johnson,Finance,Finance Admin,Active,alice@company.com,grace,2020-01-15,,HRProd

### sickLeave.csv
- **Purpose:** Tracks user sick leave periods.
- **Columns:**
    - UserID (str, required, FK to users.csv)
    - StartDate (date, required, YYYY-MM-DD)
    - EndDate (date, required, YYYY-MM-DD)
    - Status (str, required: approved/pending/etc.)
- **Sample row:**
    - u001,2025-10-20,2025-10-22,approved

### vacation.csv
- **Purpose:** Tracks user vacation periods.
- **Columns:**
    - UserID (str, required, FK to users.csv)
    - StartDate (date, required, YYYY-MM-DD)
    - EndDate (date, required, YYYY-MM-DD)
    - Status (str, required: approved/pending/etc.)
- **Sample row:**
    - u001,2025-11-01,2025-11-10,pending

### Constraints & Relationships
- All IDs must be unique within their file.
- All FK (foreign key) columns must reference valid entries in the related file.
- Status codes and values must match those defined in the documentation.
- Dates must be in the specified format; empty means not applicable.

---


## Audit Logging and Compliance

--- Every agent action, UI mutation, and registered tool call is logged to `audit_trail.csv`.
- The audit trail includes: AuditID, MutationID, Timestamp, OldStatus, NewStatus, Agent, and Comment.
- Agents do not directly mutate state files; all state changes are orchestrated via the UI or registered tool calls, which are responsible for logging.
- Log rotation/archiving is implemented for large audit files.
- The function `get_audit_trail_for_mutation(mutation_id)` allows full traceability for any mutation.

This ensures compliance, traceability, and a clear, explainable decision trail for all system actions.