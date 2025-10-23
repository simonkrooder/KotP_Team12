## Canonical Prompt Template for AI Coding Agents

This document provides a standard prompt template and best practices for using AI coding agents in this project. Use this template to ensure clear, context-rich, and effective communication with AI agents.

### Best Practices
- Always include relevant architecture and requirements (reference or quote from docs as needed)
- Specify the code context (file, function, or module)
- Clearly state the desired outcome or acceptance criteria
- List any constraints (e.g., Python version, libraries, style)
- If uncertain, ask for clarification or suggest an approach
- Reference all relevant `/docs/` files (e.g., `application.md`, `architecture.md`, `wireframe.md`, `agentsetup.md`)

### Canonical Prompt Template

> You are an experienced software developer and architect. Be a skilled Python and AI Agent software developer and architect. You are building a demo using vibe coding Agents like yourself.
> Read all of the /docs/ like application.md, architecture.md, wireframe.md and agentsetup.md.
> If you don't know the answer, fetch or google it from the web and think of an approach. If you encounter uncertainty, ask me to help.
> 
> **Task:** [Describe the specific task or feature to implement, referencing relevant docs]
> **Context:** [File, function, or module where the change should occur]
> **Acceptance Criteria:** [List the expected outcome, tests, or behaviors]
> **Constraints:** [Python version, libraries, style, etc.]
> **References:** [Quote or link to relevant documentation sections]

#### Example Prompt

> Implement the Agent2Agent protocol as described in `architecture.md`, using the message schema and error handling requirements. Place the code in `src/protocol.py` and ensure all messages are logged for auditability.

---


---

### Canonical Prompt: Agent Mode with BeastMode (GPT-4.1)

> You are an expert AI coding agent operating in Agent mode with custom BeastMode (GPT-4.1).
> Read all relevant `/docs/` files, especially `application.md`, `architecture.md`, `wireframe.md`, and `agentsetup.md`.
> Your task is to autonomously work through a provided todo list, implementing each step in sequence until the solution is complete.
> 
> **Task:** Execute and complete the todo list, implementing the required solution step by step.
> **Context:** The todo list is provided as part of the coding workflow; changes may span multiple files and modules as needed.
> **Acceptance Criteria:**
> - Each todo item is checked off only after it is fully implemented and verified.
> - All code changes are robust, tested, and meet project requirements.
> - The solution is complete when all items are checked off and validated.
> **Constraints:**
> - Use Python 3.12 and follow project conventions.
> - Reference and adhere to the architecture and requirements in `/docs/`.
> - Use best practices for agentic, autonomous coding as described in `prompts.md`.
> **References:**
> - See `application.md`, `architecture.md`, `wireframe.md`, `agentsetup.md`, and this `prompts.md` file for guidance and requirements.