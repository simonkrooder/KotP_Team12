
# TODO: Canonical Build Checklist (Aligned with approach.md and actionlist.md)

> **Note:** This checklist is now supplemented by `/docs/actionlist.md`, `/docs/csv_schemas.md`, `/docs/CONTRIBUTING.md`, and `/docs/prompts.md`. Always reference these files for the latest detailed steps, schemas, onboarding, and prompt templates.


- [ ] Document and diagram the overall architecture in `/docs/architecture.md`.
- [ ] Document the Agent2Agent protocol (message schema, error handling, retries, escalation) in `/docs/architecture.md` (see also `/docs/prompts.md`).
- [ ] Document the MCV server API/interface in `/docs/architecture.md` or `/docs/application.md`.
- [ ] Add a quickstart guide and contributor onboarding section to `/docs/CONTRIBUTING.md`.
- [ ] Add a section on model selection rationale and update process to `/docs/application.md`.
- [ ] Add user stories as acceptance criteria for each UI page (in `/docs/application.md`).
- [ ] Add architecture diagrams and message flow charts.

## 1b. DevOps & Deployment
- [ ] Add `requirements.txt` and/or `environment.yml` for reproducibility.
- [ ] Add local and cloud deployment instructions (e.g., Streamlit sharing, Azure).
- [ ] (Optional) Add CI/CD setup for linting, testing, and deployment.

## 1. Project Setup & Environment
- [ ] Install all required Python dependencies (`azure-ai-agents`, `azure-ai-projects`, `azure-identity`, `python-dotenv`, `pandas`, `streamlit`, etc.).
- [ ] Create and populate `/src/.env` with required Azure credentials and deployment info.
- [ ] Add `.env` to `.gitignore` if not already present.

- [ ] Verify and standardize the structure of all CSVs (see `/docs/csv_schemas.md`):
	- [ ] `users.csv`
	- [ ] `hr_mutations.csv`
	- [ ] `authorisations.csv`
	- [ ] `role_authorisations.csv`
	- [ ] `roles.csv`
	- [ ] `sickLeave.csv`
	- [ ] `vacation.csv`
	- [ ] `audit_trail.csv`
- [ ] Add missing columns (e.g., `Reason`, `ManagerID`) to relevant CSVs.
- [ ] Ensure all data needed for agent decisions is present in the CSVs.
- [ ] Implement a robust data access layer for reading/writing all CSV files.
- [ ] Validate CSV data against expected schemas (types, required fields) in `/docs/csv_schemas.md`.
- [ ] Add sample/mock data for demo and testing.
- [ ] Document CSV schema and sample data in `/docs/csv_schemas.md`.

## 3. Agent & Protocol Implementation
- [ ] For each agent, create a dedicated `<AgentName>Agent.py` in `/src/`:
	- [ ] InvestigationAgent
	- [ ] RightsCheckAgent
	- [ ] RequestForInformationAgent
	- [ ] AdvisoryAgent
- [ ] Implement each agent class with the standard `handle_request(context)` interface.
- [ ] Encapsulate agent logic in its own module.
- [ ] Implement the Agent2Agent protocol (message schema, logging, correlation IDs).
- [ ] Register and orchestrate agents in `agent_main.py`.
- [ ] Implement error handling, retries, and escalation logic for agent-to-agent messages.
- [ ] Ensure all agent-to-agent messages are logged and auditable.

## 4. MCV Server Implementation
- [ ] Implement the MCV server as the only integration point for tool calls:
	- [ ] Authorization checks
	- [ ] Data lookups
	- [ ] Notifications (mocked)
	- [ ] Report generation
- [ ] Ensure all tool calls and results are logged for audit.
- [ ] Add stubs for future integrations (e.g., email, external APIs).
- [ ] Document the API/interface for the MCV server.

## 5. Workflow Orchestration
- [ ] Create `/src/agent_main.py` as the main entrypoint:
	- [ ] Load environment/config
	- [ ] Initialize agents and MCV server
	- [ ] Register agents and their toolsets
	- [ ] Route messages and handle agent lifecycles
	- [ ] Submit all tool calls to the MCV server and poll for responses
	- [ ] Log all actions and status changes
	- [ ] Orchestrate the end-to-end workflow: mutation entry → investigation → rights check → clarification → manager validation → advisory report → audit logging

## 6. UI Implementation (Streamlit)
- [ ] Build Streamlit pages as per `wireframe.md`:
	- [ ] HR Mutation Entry
	- [ ] Mutations Table
	- [ ] Audit Trail
	- [ ] Mocked User/Manager Response
	- [ ] Insights/Dashboard
	- [ ] Manual Trigger/Chat (optional, for testing)
- [ ] Add navigation (sidebar/top menu) to Streamlit UI for all pages.
- [ ] Implement UI for error states, loading, and edge cases.
- [ ] Add accessibility and usability checks.
- [ ] Add user stories as acceptance criteria for each UI page.

## 7. Audit & Logging
- [ ] Log every agent action and status change in `audit_trail.csv`.
- [ ] Ensure all status changes in `hr_mutations.csv` are logged.
- [ ] Implement a function to reconstruct the full audit trail for any mutation.
- [ ] Add log rotation/archiving if audit files grow large.

## 8. Testing & Validation
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