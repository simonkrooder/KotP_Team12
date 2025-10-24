
# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [flow.md](flow.md): Canonical workflow diagram
- [toolcalls.md](toolcalls.md): MCP tool call protocol and agent tool call details
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

## Best Practice: Maintain a Running Changelog or Dev Diary

Maintain a running changelog or development diary throughout the project. This should capture:
- Key decisions and their rationale
- Blockers and how they were resolved
- Lessons learned and best practices
- Major milestones and feature completions

This log can be kept in a dedicated `CHANGELOG.md`, a section in the project README, or a shared document. It helps onboard new contributors, provides transparency, and supports continuous improvement.
## Best Practice: Crafting Prompts for AI Coding Assistants

To maximize the effectiveness of AI coding assistants (like Copilot or GPT-4o), always craft clear, context-rich prompts. Each prompt should include:
- Relevant architecture and requirements (reference or quote from docs as needed)
- The specific code context (file, function, or module)
- The desired outcome or acceptance criteria
- Any constraints (e.g., Python version, libraries, style)

Example prompt:
> “Implement the Agent2Agent protocol as described in architecture.md, using the message schema and error handling requirements. Place the code in `src/protocol.py` and ensure all messages are logged for auditability.”

This approach ensures the AI assistant has all the information needed to generate high-quality, relevant code or documentation.
# Approach: Building the Multi-Agent Access Control Demo with AI Coding Agents

## 1. Vision & Scope

We are building a fully auditable, multi-agent access control investigation and advisory system, orchestrated by AI coding agents. The system leverages a modular, agent-based architecture, with all agent actions routed through a central MCP (Model Context Protocol) server. The UI is built in Streamlit, and all data is stored in CSVs for demo/testability.

**Key goals:**
- End-to-end automation of HR mutation investigation, rights checking, clarification, and advisory.
- Full auditability and explainability (every action/status logged).
- Modular, extensible agent design (easy to add/replace agents).
- Demo-ready, with mockable user/manager responses and clear UI.

---

## 2. Technology Stack & Model Selection

### Core Stack

-- **Python 3.10+**: Main language for agents, MCP server, and data access.
- **Streamlit**: For rapid UI prototyping and demo.
- **pandas**: For CSV data access/manipulation.
- **python-dotenv**: For environment/config management.
- **Azure AI SDKs**: For agent orchestration and (optionally) LLM integration.
- **Custom agent classes**: For Investigation, Rights Check, RFI, Advisory.
- **MCP server**: (Legacy) Python module exposing tool call endpoints. Now replaced by local Python orchestration.

### AI Model Choices

- **Agentic Orchestration/Reasoning**: Use GPT-4o or GPT-4.1 for best reasoning, code generation, and context handling. These models excel at multi-step workflows, code synthesis, and structured messaging.
- **Claude 3 Sonnet/Opus**: Good for summarization, critique, and high-level planning, but GPT-4o/4.1 is preferred for Python/Streamlit code generation and agentic workflows.
- **GPT-3.5/3o**: Sufficient for simple code tasks, but not recommended for complex agent orchestration or architectural reasoning.
- **Recommendation**: Use GPT-4o/4.1 for all code, agent, and protocol generation. Use Claude 3 Sonnet/Opus for documentation review or if you need a second opinion on requirements.

**Assumption:** All code and orchestration is performed by an AI coding agent (like Copilot or GPT-4o) with access to the full codebase and documentation.

---

## 3. Documentation & Assumptions

### What to Document

- **Agent interfaces and message schemas** (see `architecture.md`)
- **MCP server endpoints and tool call contracts**
- **Data model: CSV schemas, required columns, and status codes**
- **UI wireframes and navigation**
- **Environment/config requirements**
- **Audit/logging requirements**
- **Testing/mocking strategy**
- **Assumptions**:
	- All agent-to-agent and agent-to-MCP communication is via structured Python dicts (see Agent2Agent protocol).
	- No direct DB or external API access from agents; all via MCP.
	- All user/manager responses are mockable via UI for demo.
	- The system is designed for demo/test, not production scale.

### What to Critique/Clarify

- **Model selection rationale**: Document why GPT-4o/4.1 is chosen for code/agent tasks.
- **Extensibility**: How to add new agents, tool calls, or data sources.
- **Error handling**: How retries, failures, and manual interventions are managed.
- **Security**: Minimal for demo, but note where real-world hardening would be needed.

---

## 4. Actionable Workflow

### 4.1. Project Setup

- Install all required packages (see `agentsetup.md`).
- Ensure `.env` is configured and ignored by git.
- Standardize all CSVs and add missing columns.

### 4.2. Agent & Protocol Implementation

- Implement agent classes with `handle_request(context)` interface.
- Implement Agent2Agent protocol (message schema, logging, correlation IDs).
- Implement MCP server as the only integration point for tool calls.

### 4.3. Orchestration

- Create a main entrypoint (`agent_main.py`) to:
	- Load config/env
	- Initialize agents and MCP server
	- Route messages and handle agent lifecycles
	- Log all actions/status changes

### 4.4. UI Implementation

- Build Streamlit pages as per `wireframe.md`:
	- HR Mutation Entry
	- Mutations Table
	- Audit Trail
	- Mocked Response
	- Insights/Dashboard

### 4.5. Audit & Logging

- Log every agent action and status change in `audit_trail.csv`.
- Ensure all status changes in `hr_mutations.csv` are logged.

### 4.6. Testing & Validation

- Test agent flows with sample data (see example in `application.md`).
- Mock user/manager responses via UI.
- Validate audit trail and status transitions.

---

## 5. How to Use This Approach

- **For AI coding agents**: Follow the documented interfaces, message schemas, and workflow. Use GPT-4o/4.1 for all code and orchestration tasks. Use the provided wireframes and CSV schemas as ground truth for UI/data.
- **For human devs/architects**: Use this as a blueprint for onboarding, extension, or migration to other stacks/models.

---

## 6. Open Questions & Next Steps

- **Model access**: Ensure GPT-4o/4.1 is available for all code/agent tasks.
- **MCP server**: Decide if it’s a REST API, Python class, or both for demo.
- **UI polish**: Prioritize demo functionality over production polish.
- **Security**: Note demo limitations; real-world use would require auth, input validation, etc.

---

## 7. Summary Table: Model Selection

| Task/Component         | Recommended Model | Rationale                                 |
|------------------------|------------------|-------------------------------------------|
| Agent code generation  | GPT-4o/4.1       | Best for Python, agentic workflows        |
| Protocol/schema design | GPT-4o/4.1       | Handles structured messaging well         |
| UI (Streamlit) code    | GPT-4o/4.1       | Best for Python/Streamlit                 |
| Documentation review   | Claude 3 Sonnet  | Good for summarization, critique          |
| High-level planning    | GPT-4o/4.1       | Handles context, dependencies, workflows  |
| Simple code tasks      | GPT-3.5/3o       | Sufficient, but not recommended here      |

---

## 8. Final Notes

- This approach is designed for rapid, agentic, demo-driven development.
- All documentation, code, and UI should be kept in sync and updated as the system evolves.
- Use the todo lists in `agentsetup.md` and this file to track progress and next actions.

---

**This document is the canonical approach for building the demo. All AI coding agents and human collaborators should follow it for consistent, auditable, and extensible development.**
