import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from data_access import read_csv, write_csv, get_audit_trail_for_mutation
import uuid
import os
import json
import time
from pending_actions import get_pending_actions, update_action_response

# Audit logging helper for UI actions
def log_ui_audit(action, mutation_id=None, old_status=None, new_status=None, agent=None, comment=None):
    DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
    AUDIT_FILE = os.path.join(DATA_DIR, 'audit_trail.csv')
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
    row = f'{audit_id},{mutation_id or ""},{timestamp},{old_status or ""},{new_status or ""},{agent or "UI"},{json.dumps(comment) if comment else action}\n'
    with open(AUDIT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(header + data + [row])

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
            new_row = {
                "MutationID": mutation_id,
                "Timestamp": timestamp,
                "ChangedBy": user_map[changed_by],
                "ChangedFor": user_map[changed_for],
                "ChangeType": change_type,
                "FieldChanged": field_changed,
                "OldValue": old_value,
                "NewValue": new_value,
                "Environment": environment,
                "Metadata": "{}",
                "change_investigation": "Pending",
                "Reason": reason,
                "ManagerID": user_map[manager_id]
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
