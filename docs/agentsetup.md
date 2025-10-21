# Agent Setup To-Do List

This document outlines the actionable steps required to set up an agent in the style of the Azure-AI-Foundry `main.py` example, including required frameworks, packages, and project structure. This assumes you have already created `/src/.env` with Azure Foundry subscription data.

---

## 1. Install Required Packages
- [ ] Install Azure AI Foundry SDKs and dependencies:
  - `azure-ai-agents`
  - `azure-ai-projects`
  - `azure-identity`
  - `python-dotenv`
  - Any additional tools (e.g., `streamlit`, `pandas`, etc. as needed)

## 2. Project Structure & Environment
- [ ] Ensure `/src/.env` contains all required Azure credentials and deployment info:
  - `AGENT_MODEL_DEPLOYMENT_NAME`
  - `PROJECT_ENDPOINT`
  - `AZURE_SUBSCRIPTION_ID`
  - `AZURE_RESOURCE_GROUP`
  - Any other required environment variables
- [ ] Add `.env` to `.gitignore` if not already present

## 3. Agent Code Setup
- [ ] Create a new agent entrypoint (e.g., `/src/agent_main.py`)
- [ ] In the entrypoint, implement:
  - Load environment variables with `dotenv`
  - Set up logging
  - Initialize Azure AI Project and Agent clients
  - Define agent instructions (can be loaded from a file or string)
  - Register tools (function tools, code interpreter, file search, etc.)
  - Create agent and thread objects
  - Implement message posting and run polling logic (handle tool calls, submit tool outputs, handle agent responses)
  - Implement cleanup logic

## 4. Tooling & Utilities
- [ ] Implement or adapt any required tool classes (e.g., for data access, file search, code execution)
- [ ] Add utility modules for colorized terminal output, file downloads, etc. (optional, for UX)

## 5. Testing & Iteration
- [ ] Test agent initialization and message flow with sample queries
- [ ] Validate tool call execution and agent reasoning
- [ ] Iterate on instructions and toolset as needed

## 6. Integration with Frontend
- [ ] Connect the agent backend to your frontend (e.g., via API, Streamlit, etc.)
- [ ] Ensure prompt/response flow is working end-to-end

## 7. Documentation
- [ ] Document environment variables and setup steps in `/docs/agentsetup.md`
- [ ] Add usage instructions and troubleshooting tips

---

**References:**
- [Azure-AI-Foundry main.py](https://github.com/Knights-of-the-Prompts/Azure-AI-Foundry/blob/main/src/workshop/main.py)
- [Azure AI Agents SDK Docs](https://learn.microsoft.com/en-us/python/api/overview/azure/ai-agents-readme)

