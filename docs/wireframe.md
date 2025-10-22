# UI Wireframes for Multi-Agent Access Control System

This file provides text-based wireframes for the main UI pages, designed for implementation in Streamlit (Python). Each section describes the layout, navigation, and key UI elements.

---

## 1. HR Mutation Entry Page

```
------------------------------------------------------
| HR Mutation Entry                                  |
------------------------------------------------------
| User:        [Dropdown: Select User]               |
| Application: [Dropdown: Select Application]        |
| Reason:      [Text Input]                          |
| [Submit Button]                                    |
------------------------------------------------------
| [Success/Error Message]                            |
------------------------------------------------------
```

**Notes:**
- Submitting triggers the Investigation Agent.
- Fields are required.

---

## 2. HR Mutations Table

```
------------------------------------------------------
| HR Mutations Table                                |
------------------------------------------------------
| [Filter: Status] [Filter: User] [Filter: Date]     |
------------------------------------------------------
| ID | User | Application | Status | Date | [View]   |
|----|------|-------------|--------|------|--------  |
| .. | .... | ....        | ...    | ...  | [Btn]    |
| .. | .... | ....        | ...    | ...  | [Btn]    |
------------------------------------------------------
```

**Notes:**
- Clicking [View] opens the Audit Trail for that mutation.

---

## 3. Audit Trail Page

```
------------------------------------------------------
| Audit Trail for Mutation [ID]                      |
------------------------------------------------------
| Status Timeline:                                   |
| [Pending] -> [Investigation Started] -> ...        |
------------------------------------------------------
| Timestamp | Agent | Action/Status | Details        |
|-----------|-------|--------------|----------------|
| ...       | ...   | ...          | ...            |
------------------------------------------------------
| [Back to Table]                                    |
------------------------------------------------------
```

**Notes:**
- Shows all status changes and agent actions for the selected mutation.

---

## 4. Mocked User/Manager Response Page

```
------------------------------------------------------
| Respond to Agent Request                           |
------------------------------------------------------
| Request: [Text of agent's question/request]        |
------------------------------------------------------
| [Text Input or Yes/No Buttons]                     |
| [Submit Response Button]                           |
------------------------------------------------------
| [Back to Audit Trail]                              |
------------------------------------------------------
```

**Notes:**
- Only shown when a response is awaited.
- Submitting updates the audit trail and status.

---

## 5. Insights/Dashboard Page

```
------------------------------------------------------
| Insights & Dashboard                               |
------------------------------------------------------
| [Metric: # Pending] [Metric: # Approved] ...        |
| [Chart: Status Distribution]                        |
| [Chart: Investigation Time]                         |
| [Table: Anomalies/Outliers]                         |
------------------------------------------------------
```

**Notes:**
- Visualizes system health, status counts, and anomalies.

---

## 6. (Optional) Manual Trigger/Chat Page

```
------------------------------------------------------
| Manual Agent Trigger / Chat                        |
------------------------------------------------------
| [Dropdown: Select Agent]                           |
| [Text Input: Command/Message]                      |
| [Send Button]                                      |
| [Agent Response Output]                            |
------------------------------------------------------
```

**Notes:**
- For testing and debugging agent interactions.

---

## Navigation

- Sidebar or top menu with links to:
    - HR Mutation Entry
    - HR Mutations Table
    - Insights/Dashboard
    - (Optional) Manual Trigger/Chat

---

**How to use this wireframe:**
- Each section above maps directly to a Streamlit page or component.
- Use the layout and field names as a guide for building the UI.
- Adjust as needed for usability and aesthetics.