# Walkthrough: Testing All Flows and Components

This section provides a step-by-step guide to test the full workflow and all major components. Follow these steps to validate the system end-to-end:

## 1. Preparation
- Ensure all dependencies are installed:
  - `pip install -r requirements.txt`
- Ensure all CSV files in `/data/` are present and contain sample/mock data.
- Ensure your `.env` file is set up in `/src/` with the required environment variables (see `/src/.env.example`).

## 2. Start the MCV Server
- Open a terminal in the project root.
- Start the MCV server:
  - `python src/mcv_server.py`
- Confirm the FastAPI server is running (default: http://localhost:8000/docs for API docs).

## 3. Start the Streamlit UI
- Open a new terminal in the project root.
- Start the UI:
  - `streamlit run src/ui.py`
- The UI should open in your browser (default: http://localhost:8501).

## 4. Run the Agent Orchestrator
- Open another terminal in the project root.
- Start the agent orchestrator:
  - `python src/agent_main.py`
- This process will handle agent registration, message routing, and workflow orchestration.

## 5. Walk Through a Full Flow
1. **HR Mutation Entry:**
	- In the UI, go to the "HR Mutation Entry" page.
	- Submit a new mutation (fill in required fields).
2. **Mutations Table:**
	- Go to the "Mutations Table" page.
	- Find your mutation; verify its status and details.
	- Use the "View Audit Trail" button to see the audit log for this mutation.
3. **Agent Processing:**
	- The agent orchestrator (`agent_main.py`) will process the mutation through the workflow:
	  - InvestigationAgent → RightsCheckAgent → RequestForInformationAgent → AdvisoryAgent
	- Watch the status updates in the UI and audit trail.
4. **Mocked User/Manager Response:**
	- Use the "Mocked User/Manager Response" page to simulate responses if required by the workflow.
5. **Audit Trail:**
	- Use the "Audit Trail" page to view and export logs for any mutation.
6. **Insights/Dashboard:**
	- Review the "Insights/Dashboard" page for summary statistics and workflow health.

## 6. Test Edge Cases and Error Handling
- Try submitting incomplete or invalid mutations to test validation.
- Simulate errors or retries by interrupting agent processes and observing recovery.
- Check that all actions are logged in `audit_trail.csv`.

## 7. Review Logs and Data
- Inspect `/data/audit_trail.csv` for a complete log of all actions.
- Inspect `/data/hr_mutations.csv` for status changes.

## 8. Stopping the System
- Stop all running Python processes (UI, MCV server, agent orchestrator) when done.

---
# TODO.md: Canonical Build Checklist

> **Note:** This checklist is now supplemented by, `/docs/csv_schemas.md`, `/docs/CONTRIBUTING.md`, and `/docs/prompts.md`. Always reference these files for the latest detailed steps, schemas, onboarding, and prompt templates.


# ACTIONABLE POINTS (from /docs/ review)
- [x] Standardize and update all CSV schemas and files for consistency (see csv_schemas.md).
- [x] Implement the MCV server in `/src/mcv_server.py` with all required endpoints and logging.
- [x] Implement a shared Agent2Agent protocol module for message schema, validation, and logging.
- [x] Create `/src/.env.example` and document all required environment variables.
- [x] Validate and add sample/mock data for all CSVs in `/data/`.
- [x] Implement the Streamlit UI entrypoint in `/src/ui.py` as per `wireframe.md`.


## 1a. Documentation & Architecture Overview
- [x] Document and diagram the overall architecture in (what is missing?) `/docs/architecture.md`.
- [x] Document the Agent2Agent protocol (message schema, error handling, retries, escalation) in `/docs/architecture.md` (see also `/docs/prompts.md`).
- [x] Document the MCV server API/interface in `/docs/architecture.md` or `/docs/application.md`.
- [x] Add a quickstart guide and contributor onboarding section to `/docs/CONTRIBUTING.md`.
- [x] Add a section on model selection rationale and update process to `/docs/application.md`.
- [x] Add user stories as acceptance criteria for each UI page (in `/docs/application.md`).
- [x] Add architecture diagrams and message flow charts.

## 1b. DevOps & Deployment
- [x] Add `requirements.txt` and/or `environment.yml` for reproducibility.
- [x] Add local and cloud deployment instructions (e.g., Streamlit sharing, Azure).

## 2. Project Setup & Environment
- [x] Install all required Python dependencies (`azure-ai-agents`, `azure-ai-projects`, `azure-identity`, `python-dotenv`, `pandas`, `streamlit`, etc.) (already done).
- [x] Create and populate `/src/.env` with required Azure credentials and deployment info  (already done).
- [x] Add `.env` to `.gitignore` if not already present (already done).

- [x] Verify and standardize the structure of all CSVs (see `/docs/csv_schemas.md`):
	- [x] `users.csv`
	- [x] `hr_mutations.csv`
	- [x] `authorisations.csv`
	- [x] `role_authorisations.csv`
	- [x] `roles.csv`
	- [x] `sickLeave.csv`
	- [x] `vacation.csv`
	- [x] `audit_trail.csv`
- [x] Add missing columns (e.g., `Reason`, `ManagerID`) to relevant CSVs.
- [x] Ensure all data needed for agent decisions is present in the CSVs.
- [x] Implement a robust data access layer for reading/writing all CSV files.
- [x] Validate CSV data against expected schemas (types, required fields) in `/docs/csv_schemas.md`.
- [x] Add sample/mock data for demo and testing.
- [x] Document CSV schema and sample data in `/docs/csv_schemas.md`.

## 3. Agent & Protocol Implementation
- [x] For each agent, create a dedicated `<AgentName>Agent.py` in `/src/`:
	- [x] InvestigationAgent
	- [x] RightsCheckAgent
	- [x] RequestForInformationAgent
	- [x] AdvisoryAgent
- [x] Implement each agent class with the standard `handle_request(context)` interface.
- [x] Encapsulate agent logic in its own module.
- [x] Implement the Agent2Agent protocol (message schema, logging, correlation IDs).
- [x] Register and orchestrate agents in `agent_main.py`.
- [x] Implement error handling, retries, and escalation logic for agent-to-agent messages.
- [x] Ensure all agent-to-agent messages are logged and auditable.

## 4. MCV Server Implementation
- [x] Implement the MCV server as the only integration point for tool calls:
	- [x] Authorization checks
	- [x] Data lookups
	- [x] Notifications (mocked)
	- [x] Report generation
- [x] Ensure all tool calls and results are logged for audit.
- [x] Add stubs for future integrations (e.g., email, external APIs).
- [x] Document the API/interface for the MCV server.

## 5. Workflow Orchestration
- [x] Create `/src/agent_main.py` as the main entrypoint:
	- [x] Load environment/config
	- [x] Initialize agents and MCV server
	- [x] Register agents and their toolsets
	- [x] Route messages and handle agent lifecycles
	- [x] Submit all tool calls to the MCV server and poll for responses
	- [x] Log all actions and status changes
	- [x] Orchestrate the end-to-end workflow: mutation entry → investigation → rights check → clarification → manager validation → advisory report → audit logging

## 6. UI Implementation (Streamlit)
- [x] Build Streamlit pages as per `wireframe.md`:
	- [x] HR Mutation Entry
	- [x] Mutations Table
	- [x] Audit Trail
	- [x] Mocked User/Manager Response
	- [x] Insights/Dashboard
	- [x] Manual Trigger/Chat (optional, for testing)
- [x] Add navigation (sidebar/top menu) to Streamlit UI for all pages.
- [x] Implement UI for error states, loading, and edge cases.
- [x] Add accessibility and usability checks.
- [x] Add user stories as acceptance criteria for each UI page.

## 7. Audit & Logging
- [x] Log every agent action and status change in `audit_trail.csv`.
- [x] Ensure all status changes in `hr_mutations.csv` are logged.
- [x] Implement a function to reconstruct the full audit trail for any mutation.
- [x] Add log rotation/archiving if audit files grow large.

## 8. UI Enhancement: Mutation-Centric Audit Trail View
- [x] Add a "View Audit Trail" button or link for each mutation in the Mutations Table.
- [x] When clicked, show a modal or new page with the full audit trail for that mutation (using the `get_audit_trail_for_mutation(mutation_id)` function).
- [x] Allow export of the audit trail for a mutation as CSV (optional).
- [x] Ensure this feature is accessible and user-friendly for auditors, managers, and end users.

## 9. Testing & Validation
- [ ] Test agent initialization and message flow with sample queries and data.
- [ ] Validate tool call execution and agent reasoning (mocked where needed).
- [ ] Validate system workflow with edge cases and sample data.
- [ ] Add unit tests for each agent and the MCV server.
- [ ] Add integration tests for the end-to-end workflow.
- [ ] Add test cases for error/retry/escalation flows.
- [ ] Add test data and scripts for demo scenarios.

- [ ] Document environment variables and setup steps in `/docs/application.md` and `/docs/agentsetup.md`.
- [ ] Add usage instructions and troubleshooting tips to documentation.
- [ ] Keep all documentation, code, and UI in sync as the system evolves.
- [ ] Reference `/docs/CONTRIBUTING.md` for onboarding and `/docs/prompts.md` for prompt templates.