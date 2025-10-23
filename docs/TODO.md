# Migration Plan: Refactor Agents to Local Class + Azure Model Pattern

This section describes the steps to refactor all agents to the correct pattern:

```markdown
# High-level steps (for intent and onboarding):
- [x] For each agent (`InvestigationAgent`, `RightsCheckAgent`, `RequestForInformationAgent`, `AdvisoryAgent`):
	- [x] Refactor the agent as a local Python class with a `handle_request(context)` method.
	- [x] In `handle_request`, use the Azure AI SDK (using credentials from `.env`) to call the appropriate Azure-hosted model endpoint for reasoning/decision-making.
	- [x] Remove any code that attempts to register or persist agents in Azure.
	- [x] Ensure all orchestration, message passing, and workflow logic is handled locally in Python (see `agent_main.py`).
	- [x] Use the structure and best practices from `src/old/agent_example.py` as a template for model calls and tool integration.
	- [x] Add or update docstrings to clarify the agent's pattern and responsibilities.

# Detailed implementation steps:
- [x] For each agent:
	- [x] Import and use `get_project_client` and `get_model_deployment` from `azure_client.py`.
	- [x] In `handle_request`:
		- [x] Construct a prompt from the context (see `agent_example.py`).
		- [x] Call the Azure model using the SDK and return the result.
		- [x] Integrate async tool functions if needed.
		- [x] Handle errors, retries, and escalation as before.
	- [x] Remove or refactor any local business logic now handled by the model.
	- [x] Add or update docstrings to clarify the agent's pattern and responsibilities.
	- [x] Add a code comment referencing the relevant docs section.
- [x] Update `agent_main.py` to instantiate and orchestrate the refactored agents.
- [x] Update or add unit and integration tests for the new agent pattern (mock Azure model calls, validate prompt construction and response handling).
- [x] Add minimal example usage for each agent in `/tests/` or `/examples/`.
- [x] Update onboarding/setup docs and troubleshooting tips in `/docs/CONTRIBUTING.md` and `/docs/agentsetup.md`.
```

**Summary:**
> All agents should be local Python classes that use Azure-hosted models for inference. No persistent agent registration in Azure. All orchestration is local.

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