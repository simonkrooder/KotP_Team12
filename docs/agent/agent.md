# Agent Design Plan for HR Mutations & Access Control System

## 1. Purpose

The agent will serve as an intelligent assistant within the HR Mutations & Access Control system. Its main goals are:
- To answer user queries about HR mutations, roles, and authorisations.
- To automate and streamline approval workflows.
- To detect and flag anomalies or policy violations.
- To provide a conversational interface for interacting with system data.

---

## 2. Agent Type

We will implement a **hybrid agent**:
- **Rule-based logic** for deterministic tasks (e.g., fetching user roles, listing recent mutations).
- **LLM-powered responses** for natural language queries and explanations (optional, for future extensibility).

---

## 3. Data Access Layer

- Abstract data access through a dedicated Python class (e.g., `HRMutationsAgent`).
- This class will encapsulate all logic for querying and updating the core dataframes:
  - `users_df`
  - `roles_df`
  - `auths_df`
  - `role_auths_df`
  - `mutations_df`

---

## 4. Agent Interface

- **Streamlit Integration:** Add an "Agent" tab to the sidebar for user interaction.
- **Chat UI:** Use Streamlit's chat components (`st.chat_input`, `st.chat_message`) for conversational interaction.
- **API Layer (optional):** Expose agent actions via REST API for integration with other systems.

---

## 5. Core Agent Functions

- `get_user_roles(user_id)`: List all roles for a given user.
- `get_user_authorisations(user_id)`: List all authorisations for a user.
- `get_recent_mutations(n)`: Show the most recent HR mutations.
- `approve_mutation(mutation_id)`: Approve a pending mutation (future).
- `detect_anomalies()`: Identify suspicious changes or access patterns (future).
- `answer_query(query)`: (Optional) Use LLM to answer free-form questions.

---

## 6. Security & Access Control

- Ensure agent actions respect user permissions.
- Log all agent actions for auditability.
- Prevent sensitive operations unless user is authorised.

---

## 7. Implementation Steps

1. **Design Agent Class:** Implement `HRMutationsAgent` with core methods.
2. **Integrate with Streamlit:** Add an "Agent" tab and chat UI.
3. **Wire Up Data Access:** Pass loaded dataframes to the agent.
4. **Implement Core Functions:** Start with read-only queries, then add mutation/approval logic.
5. **Add Security Checks:** Validate user permissions for each action.
6. **(Optional) LLM Integration:** Add natural language query support.
7. **Testing:** Write unit tests for agent methods.
8. **Documentation:** Document agent usage and API.

---

## 8. File Structure

```
/docs/agent/agent.md         # This plan
/src/agent.py                # Agent class implementation
/src/application.py          # Streamlit app (integration point)
/data/                       # CSV data files
/tests/                      # Unit tests for agent
```

---

## 9. Future Extensions

- Integrate with external HR systems.
- Add notification/alerting features.
- Expand LLM capabilities for richer conversations.

---

## 10. Next Steps

- Review and approve this plan.
- Proceed to scaffold the agent class and Streamlit integration.