
## 1. Data Foundation
[ ] Verify and standardize the structure of `users.csv`.
[ ] Verify and standardize the structure of `hr_mutations.csv`.
[ ] Verify and standardize the structure of `authorisations.csv`.
[ ] Verify and standardize the structure of `role_authorisations.csv`.
[ ] Verify and standardize the structure of `roles.csv`.
[ ] Verify and standardize the structure of `sickLeave.csv`.
[ ] Verify and standardize the structure of `vacation.csv`.
[ ] Verify and standardize the structure of `audit_trail.csv`.
[ ] Add missing columns (e.g., `Reason`, `ManagerID`) to relevant CSVs.
[ ] Review if the available data in all CSV files is sufficient to answer all agent questions (e.g., sick leave, vacation, authorizations).
[ ] Implement a data access function for reading/writing a single CSV file.
[ ] Implement a data access layer for all CSV files.

## 2. Environment & Dependencies
[ ] Install required Python dependencies (`azure-ai-agents`, `azure-ai-projects`, `azure-identity`, `python-dotenv`, `pandas`, `streamlit`, etc.).
[ ] Create and populate `/src/.env` with required Azure credentials and deployment info.
[ ] Add `.env` to `.gitignore` if not already present.

## 3. Core Agent Implementation
[ ] For each new agent, create a dedicated `<AgentName>Agent.py` file in `/src/` (replace `<AgentName>` with the specific agent’s name, e.g., `InvestigationAgent.py`, `RightsCheckAgent.py`, etc.):
	- [ ] Implement the agent class with a standard interface (e.g., `handle_request(context)`)
	- [ ] Ensure agent logic is encapsulated in its own module
	- [ ] Update agent registration and orchestration in `agent_main.py` as new agents are added
[ ] Create a minimal Investigation Agent class with a stub method.
[ ] Create a minimal Rights Check Agent class with a stub method.
[ ] Create a minimal Request for Information Agent class with a stub method.
[ ] Create a minimal Advisory Agent class with a stub method.
[ ] Implement the Agent2Agent protocol for message passing (stub).

## 4. MCV Server Implementation
[ ] Implement the MCV server with a stub endpoint for authorization checks.
[ ] Implement the MCV server with a stub endpoint for data lookups.
[ ] Implement the MCV server with a stub endpoint for notifications.
[ ] Implement the MCV server with a stub endpoint for report generation.

## 5. UI Features (Streamlit)
[ ] Create a minimal Streamlit HR mutation entry page.
[ ] Create a minimal Streamlit HR mutations table page.
[ ] Create a minimal Streamlit audit trail page.
[ ] Create a minimal Streamlit mocked user/manager response page.
[ ] Create a minimal Streamlit insights/dashboard page.
[ ] Implement a Streamlit Manual Trigger/Chat page for agent testing/debugging.
[ ] Add navigation (sidebar/top menu) to Streamlit UI for all pages.

## 6. Workflow Orchestration
[ ] Create `/src/agent_main.py` with environment variable loading.
[ ] Initialize agent clients and MCV server in `/src/agent_main.py`.
[ ] Register agents and their toolsets in `/src/agent_main.py`.
[ ] Implement agent workflow orchestration in `/src/agent_main.py`:
	- [ ] Route messages between agents using the Agent2Agent protocol
	- [ ] Submit all tool calls to the MCV server and poll for responses
	- [ ] Ensure all agent actions and status changes are orchestrated through `agent_main.py`
	- [ ] Orchestrate the end-to-end workflow: mutation entry → investigation → rights check → clarification → manager validation → advisory report → audit logging
[ ] Implement message routing and logging in `/src/agent_main.py`.
[ ] Implement logging of agent actions to `audit_trail.csv`.
[ ] Implement status updates to `hr_mutations.csv`.

## 7. Testing & Validation
[ ] Test agent initialization with a sample query.
[ ] Test message flow between agents with sample data.
[ ] Test tool call execution and agent reasoning (mocked).
[ ] Validate system workflow with edge cases and sample data.

## 8. Documentation
[ ] Document environment variables and setup steps in `/docs/application.md`.
[ ] Add usage instructions and troubleshooting tips to documentation.