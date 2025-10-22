
# Agent Setup Checklist

This checklist provides step-by-step instructions for implementing the multi-agent system as described in `architecture.md` and `application.md`.  
**Use this as your development and onboarding guide.**

---

## 1. Install Required Packages

- [ ] Install Azure AI Foundry SDKs and dependencies:
  - `azure-ai-agents`
  - `azure-ai-projects`
  - `azure-identity`
  - `python-dotenv`
  - `pandas`
  - `streamlit` (for UI)
  - Any other required tools

## 2. Project Structure & Environment

- [ ] Ensure `/src/.env` contains all required Azure credentials and deployment info:
  - `AGENT_MODEL_DEPLOYMENT_NAME`
  - `PROJECT_ENDPOINT`
  - `AZURE_SUBSCRIPTION_ID`
  - `AZURE_RESOURCE_GROUP`
  - Any other required environment variables
- [ ] Add `.env` to `.gitignore` if not already present

## 3. Data Foundation

- [ ] Verify and standardize all CSV files:
  - `authorisations.csv`, `hr_mutations.csv`, `role_authorisations.csv`, `roles.csv`, `users.csv`, `sickLeave.csv`, `vacation.csv`, `audit_trail.csv`
- [ ] Add or update columns as needed (e.g., `Reason`, `ManagerID`)
- [ ] Implement a data access layer for reading/writing CSVs

## 4. Agent Code Implementation

- [ ] Create agent classes/modules:
  - Investigation Agent
  - Rights Check Agent
  - Request for Information Agent
  - Advisory Agent
- [ ] Implement Agent2Agent protocol for structured messaging and context passing
- [ ] Implement standard agent interface (e.g., `handle_request(context)`)

## 5. MCV Server Implementation

- [ ] Implement the MCV server as the only integration point for tool calls:
  - Authorization checks
  - Data lookups
  - Sending/receiving (mocked) notifications
  - Report generation
- [ ] Ensure all tool calls and results are logged for audit

## 6. Orchestration & Entry Point

- [ ] Create `/src/agent_main.py` as the main entrypoint:
  - Load environment variables
  - Initialize agent clients and MCV server
  - Register agents and their toolsets
  - Handle message routing, tool call submission, and response polling
  - Log all actions and status changes

## 7. Frontend/UI

- [ ] Implement UI pages (e.g., with Streamlit):
  - HR mutation entry page
  - HR mutations table
  - Audit trail page
  - Mocked user/manager response page
  - Insights/dashboard page
  - (Optional) Manual trigger/chat page

## 8. Audit Trail & Logging

- [ ] Log every agent action and status change in `audit_trail.csv`
- [ ] Ensure all updates to `change_investigation` in `hr_mutations.csv` are logged

## 9. Testing & Validation

- [ ] Test agent initialization and message flow with sample queries
- [ ] Validate tool call execution and agent reasoning
- [ ] Mock all system interactions for end-to-end testing
- [ ] Validate with edge cases and sample data

## 10. Documentation

- [ ] Document environment variables and setup steps in `/docs/application.md`
- [ ] Add usage instructions and troubleshooting tips

---

