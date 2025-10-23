
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

- [x] Ensure `/src/.env` contains all required Azure credentials and deployment info (see `/src/.env.example`). (Complete)
- [x] Add `.env` to `.gitignore` if not already present. (Complete)
- [x] Document all environment variables in `/docs/application.md` under an 'Environment Variables' section. (Complete)
- [x] Create a sample `.env.example` file for onboarding, listing all required variables with placeholder values. (Complete)
- [x] Best practices are followed: `.env` is never committed, `python-dotenv` is used, and onboarding docs are up to date. (Complete)

> **Note:** All environment and onboarding steps are now complete and production-ready. No further action required for this section.



## 3. Data Foundation

- [x] Verify and standardize all CSV files:
    - [x] `authorisations.csv`
    - [x] `hr_mutations.csv`
    - [x] `role_authorisations.csv`
    - [x] `roles.csv`
    - [x] `users.csv`
    - [x] `sickLeave.csv`
    - [x] `vacation.csv`
    - [x] `audit_trail.csv`
- [x] For each CSV, define and document:
    - [x] Column names
    - [x] Data types
    - [x] Required fields
    - [x] Example row
- [x] Add or update columns as needed (e.g., `Reason`, `ManagerID`).
- [x] Add schema documentation to `/docs/csv_schemas.md`.

> **Note:** All CSVs are present, standardized, and fully documented. Data foundation is complete and demo/test ready.


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

