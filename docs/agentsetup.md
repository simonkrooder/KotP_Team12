
# Agent Setup Checklist

This checklist provides step-by-step instructions for implementing the multi-agent system as described in `architecture.md` and `application.md`.  
**Use this as your development and onboarding guide.**

---


## 1. Install Required Packages

- [ ] Install Azure AI Foundry SDKs and dependencies:
    - [ ] `azure-ai-agents`
    - [ ] `azure-ai-projects`
    - [ ] `azure-identity`
    - [ ] `python-dotenv`
    - [ ] `pandas`
    - [ ] `streamlit` (for UI)
    - [ ] Any other required tools
- [ ] Verify all packages are listed in `requirements.txt`
- [ ] Test package installation in a clean environment



## 2. Project Structure & Environment

- [ ] Ensure `/src/.env` contains all required Azure credentials and deployment info:
    - [ ] `AGENT_MODEL_DEPLOYMENT_NAME` (Name of the Azure OpenAI deployment for agents)
    - [ ] `PROJECT_ENDPOINT` (Base URL for the MCV server or Azure project)
    - [ ] `AZURE_SUBSCRIPTION_ID` (Azure subscription ID for resource access)
    - [ ] `AZURE_RESOURCE_GROUP` (Azure resource group name)
    - [ ] Any other required environment variables (document below)
- [ ] Add `.env` to `.gitignore` if not already present
- [ ] Document all environment variables in `/docs/application.md` under an 'Environment Variables' section
- [ ] Create a sample `.env.example` file for onboarding, listing all required variables with placeholder values
- [ ] Best practices:
    - Never commit real `.env` files or secrets to version control
    - Use `python-dotenv` to load environment variables in all entrypoints
    - Reference environment variables in code using `os.getenv()`
    - Update `.env.example` whenever a new variable is added


## 3. Data Foundation

- [ ] Verify and standardize all CSV files:
    - [ ] `authorisations.csv`
    - [ ] `hr_mutations.csv`
    - [ ] `role_authorisations.csv`
    - [ ] `roles.csv`
    - [ ] `users.csv`
    - [ ] `sickLeave.csv`
    - [ ] `vacation.csv`
    - [ ] `audit_trail.csv`
- [ ] For each CSV, define and document:
    - [ ] Column names
    - [ ] Data types
    - [ ] Required fields
    - [ ] Example row
- [ ] Add or update columns as needed (e.g., `Reason`, `ManagerID`)
- [ ] Implement a data access layer for reading/writing CSVs
- [ ] Add schema documentation to `/docs/csv_schemas.md`


## 4. Agent Code Implementation

- [ ] For each agent type, create a dedicated class/module:
    - [ ] Investigation Agent
    - [ ] Rights Check Agent
    - [ ] Request for Information Agent
    - [ ] Advisory Agent
- [ ] Define a base agent interface (e.g., `handle_request(context)`)
- [ ] Implement Agent2Agent protocol for structured messaging and context passing
- [ ] Add docstrings and usage examples for each agent
- [ ] Write unit tests for agent logic


## 5. MCV Server Implementation

- [ ] Implement the MCV server as the only integration point for tool calls:
    - [ ] Authorization checks
    - [ ] Data lookups
    - [ ] Sending/receiving (mocked) notifications
    - [ ] Report generation
- [ ] Define and document MCV server endpoints, expected inputs/outputs, and error handling in `/docs/architecture.md`
- [ ] Ensure all tool calls and results are logged for audit
- [ ] Add integration tests for MCV server


## 6. Orchestration & Entry Point

- [ ] Create `/src/agent_main.py` as the main entrypoint:
    - [ ] Load environment variables
    - [ ] Initialize agent clients and MCV server
    - [ ] Register agents and their toolsets
    - [ ] Handle message routing, tool call submission, and response polling
    - [ ] Log all actions and status changes
- [ ] Add CLI or config options for running in test/demo mode
- [ ] Add logging and error handling for orchestration logic


## 7. Frontend/UI

- [ ] Implement UI pages (e.g., with Streamlit):
    - [ ] HR mutation entry page
    - [ ] HR mutations table
    - [ ] Audit trail page
    - [ ] Mocked user/manager response page
    - [ ] Insights/dashboard page
    - [ ] (Optional) Manual trigger/chat page
- [ ] For each page, define required UI elements and data sources
- [ ] Add mock data and test UI flows
- [ ] Document UI navigation and wireframes in `/docs/wireframe.md`


## 8. Audit Trail & Logging

- [ ] Log every agent action and status change in `audit_trail.csv`
- [ ] Ensure all updates to `change_investigation` in `hr_mutations.csv` are logged
- [ ] Define audit log format and required fields in `/docs/application.md`
- [ ] Add automated tests for logging



## 9. Testing & Validation

- [ ] Test agent initialization and message flow with sample queries
- [ ] Validate tool call execution and agent reasoning
- [ ] Mock all system interactions for end-to-end testing
- [ ] Validate with edge cases and sample data
- [ ] Add unit and integration tests for all major components
- [ ] Document test scenarios and expected outcomes in `/docs/application.md`

### Mocking and Testing Strategy (Agent Flows & UI)

- Use mock data in `/data/` CSVs to simulate real-world scenarios (e.g., valid/invalid rights, sick leave, vacation, manager approval/denial).
- For agent-to-agent communication, use the Agent2Agent protocol with test correlation IDs and timestamps for traceability.
- For agent-to-UI interactions (e.g., user/manager responses), use Streamlit UI forms/buttons to allow manual/mock responses. All such responses should be logged in the audit trail.
- Simulate notifications and clarifications in the UI rather than sending real emails.
- For end-to-end testing, follow the workflow example in `/docs/application.md` and validate:
    - Status transitions in `hr_mutations.csv`
    - Audit trail entries in `audit_trail.csv`
    - Correct handling of edge cases (e.g., missing data, repeated errors)
- Use automated tests for agent logic, MCV server endpoints, and data access functions.
- Document new test scenarios and expected outcomes in `/docs/application.md` as the project evolves.


## 10. Documentation

- [ ] Document environment variables and setup steps in `/docs/application.md`
- [ ] Add usage instructions and troubleshooting tips
- [ ] Maintain a running changelog in `CHANGELOG.md`
- [ ] Add a developer onboarding/contribution guide in `/docs/CONTRIBUTING.md`

---

