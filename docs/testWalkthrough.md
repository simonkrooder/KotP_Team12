# Walkthrough: Testing All Flows and Components

This section provides a step-by-step guide to test the full workflow and all major components. Follow these steps to validate the system end-to-end:

## 1. Preparation
- Ensure all dependencies are installed:
  - `pip install -r requirements.txt`
- Ensure all CSV files in `/data/` are present and contain sample/mock data.
- Ensure your `.env` file is set up in `/src/` with the required environment variables (see `/src/.env.example`).

## 2. Start the MCP Server
- Open a terminal in the project root.
- Start the MCP server:
	- `python src/mcp_server.py`
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
- Stop all running Python processes (UI, MCP server, agent orchestrator) when done.
