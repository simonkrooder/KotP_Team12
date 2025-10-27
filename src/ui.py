
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from data_access import read_csv, write_csv, get_audit_trail_for_mutation
import uuid
import os
import json
import time
from pending_actions import get_pending_actions, update_action_response

# --- Import InvestigationAgent for triggering on mutation ---
import sys
from pathlib import Path
AGENT_PATH = Path(__file__).parent
PROJECT_ROOT = AGENT_PATH.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
try:
    from src.InvestigationAgent import InvestigationAgent
except ImportError:
    InvestigationAgent = None

# Audit logging helper for UI actions
def log_ui_audit(action, mutation_id=None, old_status=None, new_status=None, agent=None, comment=None):
    import csv
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    AUDIT_FILE = os.path.join(DATA_DIR, 'audit_trail.csv')
    # Read existing data (preserve header and data)
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        header_idx = next((i for i, l in enumerate(lines) if l.strip().startswith('AuditID')), None)
        if header_idx is not None:
            header = lines[:header_idx+1]
            data = lines[header_idx+1:]
        else:
            header = []
            data = lines
    else:
        header = ["AuditID,MutationID,Timestamp,OldStatus,NewStatus,Agent,Comment\n"]
        data = []
    audit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now(timezone.utc).isoformat()
    # Prepare comment field as string
    if comment is not None:
        if not isinstance(comment, str):
            comment_str = json.dumps(comment, ensure_ascii=False)
        else:
            comment_str = comment
    else:
        comment_str = str(action)
    # Reasoning: extract from action or comment if present
    reasoning = ""
    if isinstance(action, dict) and "reasoning" in action:
        reasoning = action["reasoning"]
    elif isinstance(comment, dict) and "reasoning" in comment:
        reasoning = comment["reasoning"]
    # Serialize reasoning as JSON
    import json as _json
    try:
        reasoning_json = _json.dumps(reasoning, ensure_ascii=False)
    except Exception:
        reasoning_json = str(reasoning)
    row = [audit_id, mutation_id or "", timestamp, old_status or "", new_status or "", agent or "UI", comment_str, reasoning_json]
    # Write all rows back using csv.writer for robust quoting
    with open(AUDIT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        # Write header with Reasoning column
        writer.writerow(["AuditID", "MutationID", "Timestamp", "OldStatus", "NewStatus", "Agent", "Comment", "Reasoning"])
        # Write existing data rows (skip any blank lines)
        for line in data:
            if line.strip():
                reader = csv.reader([line])
                for parsed_row in reader:
                    # If old header, skip it
                    if parsed_row and parsed_row[0] == "AuditID":
                        continue
                    # If old row, pad to 8 columns
                    while len(parsed_row) < 8:
                        parsed_row.append("")
                    writer.writerow(parsed_row)
        # Write the new row
        writer.writerow(row)

st.set_page_config(page_title="Agentic HR Access Control Demo", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")

# Page name constants
PAGE_HR_MUTATION_ENTRY = "HR Mutation Entry"
PAGE_HR_MUTATIONS_TABLE = "HR Mutations Table"
PAGE_AUDIT_TRAIL = "Audit Trail"
PAGE_USER_MANAGER_RESPONSE = "Mocked User/Manager Response"
PAGE_INSIGHTS_DASHBOARD = "Insights/Dashboard"
PAGE_MANUAL_TRIGGER_CHAT = "Manual Trigger/Chat (Optional)"

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to page:",
    [
        PAGE_HR_MUTATION_ENTRY,
        PAGE_HR_MUTATIONS_TABLE,
        PAGE_AUDIT_TRAIL,
        PAGE_USER_MANAGER_RESPONSE,
        PAGE_INSIGHTS_DASHBOARD,
        PAGE_MANUAL_TRIGGER_CHAT
    ]
)

if page == "HR Mutation Entry":
    st.header("HR Mutation Entry")
    st.caption("All fields are required unless marked optional. Please provide accurate information for auditability.")
    users_df = read_csv('users')
    user_options = users_df['UserID'] + " - " + users_df['Name']
    user_map = dict(zip(user_options, users_df['UserID']))
    changed_by = st.selectbox("Changed By (User)", user_options, help="Select the user making the change.")
    changed_for = st.selectbox("Changed For (User)", user_options, help="Select the user whose data is being changed.")
    change_type = st.selectbox("Change Type", ["Create", "Update", "Terminate"], help="Type of change being made.")
    field_changed = st.text_input("Field Changed (e.g., Salary, JobTitle)", help="Specify the field that is being changed.")
    old_value = st.text_input("Old Value (optional)", help="Previous value before the change (if applicable).")
    new_value = st.text_input("New Value", help="New value after the change.")
    environment = st.selectbox("Environment", users_df['Environment'].unique(), help="System environment (e.g., HRProd, HRTest).")
    reason = st.text_input("Reason for Change", help="Provide a reason for the change.")
    manager_id = st.selectbox("Manager", user_options, help="Select the manager responsible for validation.")
    submit = st.button("Submit Mutation")
    if submit:
        try:
            hr_mut_df = read_csv('hr_mutations')
            mutation_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now(timezone.utc).isoformat()
            def safe_str(val):
                if val is None or (isinstance(val, float) and pd.isna(val)):
                    return ""
                return str(val)
            new_row = {
                "MutationID": safe_str(mutation_id),
                "Timestamp": safe_str(timestamp),
                "ChangedBy": safe_str(user_map[changed_by]),
                "ChangedFor": safe_str(user_map[changed_for]),
                "ChangeType": safe_str(change_type),
                "FieldChanged": safe_str(field_changed),
                "OldValue": safe_str(old_value),
                "NewValue": safe_str(new_value),
                "Environment": safe_str(environment),
                "Metadata": "{}",  # Always a string
                "change_investigation": "Pending",
                "Reason": safe_str(reason),
                "ManagerID": safe_str(user_map[manager_id])
            }
            hr_mut_df = pd.concat([hr_mut_df, pd.DataFrame([new_row])], ignore_index=True)
            write_csv('hr_mutations', hr_mut_df)
            # Log audit for mutation creation
            log_ui_audit(
                action="mutation_created",
                mutation_id=mutation_id,
                old_status="",
                new_status="Pending",
                agent=changed_by,
                comment={"field": field_changed, "new_value": new_value, "reason": reason}
            )

            # --- Trigger InvestigationAgent (with Agent2Agent chaining) ---
            if InvestigationAgent is not None:
                try:
                    agent = InvestigationAgent()
                    # Pass the new mutation as context
                    agent_response = agent.handle_request(new_row)
                    # Extract thoughts from all agents
                    summary_lines = []
                    if isinstance(agent_response, dict):
                        inv = agent_response.get('investigation', {})
                        rc = agent_response.get('rights_check', {})
                        info_user = agent_response.get('information_user_request', {})
                        info_manager = agent_response.get('information_manager_request', {})
                        advisory = agent_response.get('advisory_report', {})
                        # InvestigationAgent
                        inv_text = inv.get('response') or inv.get('error')
                        if inv_text:
                            summary_lines.append(f"**Investigation Agent:** {inv_text}")
                        # RightsCheckAgent
                        rc_text = rc.get('response') or rc.get('error')
                        if rc_text:
                            summary_lines.append(f"**Rights Check Agent:** {rc_text}")
                        # RequestForInformationAgent (user)
                        info_user_text = info_user.get('response') or info_user.get('error')
                        if info_user_text:
                            summary_lines.append(f"**User Clarification Agent:** {info_user_text}")
                        # RequestForInformationAgent (manager)
                        info_manager_text = info_manager.get('response') or info_manager.get('error')
                        if info_manager_text:
                            summary_lines.append(f"**Manager Validation Agent:** {info_manager_text}")
                        # AdvisoryAgent (final advisory)
                        advisory_text = advisory.get('response') or advisory.get('error')
                        if advisory_text:
                            summary_lines.append(f"**Advisory Agent (Final Advisory):** {advisory_text}")
                        summary = "\n\n".join(summary_lines) if summary_lines else str(agent_response)
                    else:
                        summary = agent_response.get('response', agent_response) if isinstance(agent_response, dict) else str(agent_response)
                    st.info(f"Agent Workflow Summary:\n\n{summary}")
                    # Optionally show full JSON result in expandable section
                    with st.expander("Show full agent response (JSON)"):
                        st.json(agent_response)
                except Exception as agent_exc:
                    st.warning(f"Investigation Agent trigger failed: {agent_exc}")
            else:
                st.warning("InvestigationAgent could not be imported; agent not triggered.")

            st.success(f"Mutation {mutation_id} submitted successfully!")
        except Exception as e:
            st.error(f"Error submitting mutation: {e}")

elif page == "HR Mutations Table":
    st.header("HR Mutations Table")
    try:
        hr_mut_df = read_csv('hr_mutations')
        users_df = read_csv('users')
        # Optional filters
        user_options = users_df['UserID'] + " - " + users_df['Name']
        filter_user = st.selectbox("Filter by Changed For (User)", ["All"] + list(user_options))
        filter_type = st.selectbox("Filter by Change Type", ["All"] + hr_mut_df['ChangeType'].dropna().unique().tolist())
        filter_status = st.selectbox("Filter by Investigation Status", ["All"] + hr_mut_df['change_investigation'].dropna().unique().tolist())
        df = hr_mut_df.copy()
        if filter_user != "All":
            user_id = filter_user.split(" - ")[0]
            df = df[df['ChangedFor'] == user_id]
        if filter_type != "All":
            df = df[df['ChangeType'] == filter_type]
        if filter_status != "All":
            df = df[df['change_investigation'] == filter_status]
        st.dataframe(df, use_container_width=True)

        # --- Mutation-centric audit trail view ---
        st.subheader("View Audit Trail for a Mutation")
        mutation_ids = df['MutationID'].tolist()
        if mutation_ids:
            selected_mutation = st.selectbox("Select MutationID to view audit trail", mutation_ids)
            if st.button("Show Audit Trail for Selected Mutation"):
                audit_df = get_audit_trail_for_mutation(selected_mutation)
                if not audit_df.empty:
                    st.write(f"Audit Trail for MutationID: {selected_mutation}")
                    st.dataframe(audit_df, use_container_width=True)
                    # Optional: Export as CSV
                    csv = audit_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Audit Trail as CSV",
                        data=csv,
                        file_name=f'audit_trail_{selected_mutation}.csv',
                        mime='text/csv',
                    )
                else:
                    st.info("No audit trail entries found for this mutation.")
        else:
            st.info("No mutations to display.")
    except Exception as e:
        st.error(f"Error loading HR mutations: {e}")

elif page == "Audit Trail":
    st.header("Audit Trail")
    try:
        audit_df = read_csv('audit_trail')
        # Coerce all columns to string type to avoid schema validation errors
        for col in audit_df.columns:
            audit_df[col] = audit_df[col].astype(str)
        # Optional filters
        action_types = ["All"] + audit_df['ActionType'].dropna().unique().tolist() if 'ActionType' in audit_df.columns else ["All"]
        filter_action = st.selectbox("Filter by Action Type", action_types)
        user_ids = ["All"] + audit_df['UserID'].dropna().unique().tolist() if 'UserID' in audit_df.columns else ["All"]
        filter_user = st.selectbox("Filter by User", user_ids)
        df = audit_df.copy()
        if filter_action != "All" and 'ActionType' in df.columns:
            df = df[df['ActionType'] == filter_action]
        if filter_user != "All" and 'UserID' in df.columns:
            df = df[df['UserID'] == filter_user]
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading audit trail: {e}")

elif page == "Mocked User/Manager Response":
    st.header("Mocked User/Manager Response")
    st.caption("Review and respond to pending agent actions in real time. This page polls for new actions every 2 seconds.")
    # Polling for new pending actions (simulate real-time)
    if 'last_poll' not in st.session_state:
        st.session_state['last_poll'] = time.time()
    if time.time() - st.session_state['last_poll'] > 2:
        st.session_state['last_poll'] = time.time()
        st.experimental_rerun()

    # For demo: assume current user is 'manager1' (replace with real user/session logic as needed)
    current_user_id = st.session_state.get('user_id', 'manager1')
    actions = get_pending_actions(recipient_id=current_user_id, status='pending')
    if not actions:
        st.info("No pending agent actions for you at this time.")
    else:
        now = datetime.utcnow()
        for action in actions:
            created_at = action.get('created_at')
            overdue = False
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at)
                    overdue = (now - created_dt).total_seconds() > 600  # 10 minutes
                except Exception:
                    pass
            st.subheader(f"Action: {action['type']} (ID: {action['action_id']})")
            st.write(f"**Context:** {action['context']}")
            if overdue:
                st.warning("This action has not been responded to for over 10 minutes. Please respond or escalate.")
            with st.form(f"respond_{action['action_id']}"):
                response = st.text_area("Your Response", value=action.get('response', ''))
                submitted = st.form_submit_button("Submit Response")
                if submitted:
                    update_action_response(action['action_id'], response)
                    # Log to audit trail
                    log_ui_audit(
                        action=f"pending_action_response_{action['type']}",
                        mutation_id=action.get('context', ''),
                        old_status="pending",
                        new_status="responded",
                        agent=current_user_id,
                        comment={"action_id": action['action_id'], "response": response}
                    )
                    st.success("Response submitted!")
                    st.experimental_rerun()

elif page == "Insights/Dashboard":
    st.header("Insights / Dashboard")
    st.caption("All status codes are standardized for audit and compliance. For accessibility, use keyboard navigation and screen reader support in Streamlit.")
    try:
        hr_mut_df = read_csv('hr_mutations')
        total_mutations = len(hr_mut_df)
        pending = (hr_mut_df['change_investigation'] == 'Pending').sum()
        approved = (hr_mut_df['change_investigation'] == 'Approved').sum()
        rejected = (hr_mut_df['change_investigation'] == 'Rejected').sum()
        st.metric("Total Mutations", total_mutations)
        st.metric("Pending Investigations", pending)
        st.metric("Approved", approved)
        st.metric("Rejected", rejected)
        st.subheader("Mutations by Type")
        st.bar_chart(hr_mut_df['ChangeType'].value_counts())
        st.subheader("Mutations by Status")
        st.bar_chart(hr_mut_df['change_investigation'].value_counts())
        st.subheader("Recent Mutations")
        st.dataframe(hr_mut_df.sort_values('Timestamp', ascending=False).head(10), use_container_width=True)
    except Exception as e:
        st.error(f"Error loading dashboard: {e}")
# Accessibility Note
#
# For future enhancements, consider adding ARIA labels, keyboard navigation tips, and color contrast checks for full accessibility compliance.

elif page == "Manual Trigger/Chat (Optional)":
    st.header("Manual Trigger / Chat (Demo)")
    try:
        msg = st.text_area("Enter a message or trigger for the agent system:")
        if st.button("Send Message"):
            # For demo: append to a chat_log.csv in data folder
            from pathlib import Path
            import csv
            chat_log_path = Path(__file__).parent.parent / 'data' / 'chat_log.csv'
            chat_log_exists = chat_log_path.exists()
            with open(chat_log_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not chat_log_exists:
                    writer.writerow(["Timestamp", "Message"])
                writer.writerow([datetime.now().isoformat(), msg])
            st.success("Message sent and logged.")
        # Show last 10 messages
        from pathlib import Path
        import pandas as pd
        chat_log_path = Path(__file__).parent.parent / 'data' / 'chat_log.csv'
        if chat_log_path.exists():
            chat_df = pd.read_csv(chat_log_path)
            st.subheader("Recent Messages")
            st.dataframe(chat_df.tail(10), use_container_width=True)
    except Exception as e:
        st.error(f"Error in manual trigger/chat: {e}")
