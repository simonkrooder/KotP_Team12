
import streamlit as st
import pandas as pd
from datetime import datetime, timezone
from data_access import read_csv, write_csv, get_audit_trail_for_mutation
import uuid
import os
import json
import time
from pending_actions import get_pending_actions, update_action_response

# --- Option Menu for Navigation ---
from streamlit_option_menu import option_menu

# --- Custom UI Styling (Capgemini-inspired dark mode) ---
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(120deg, #0a0e1a 0%, #1a1f2e 100%) !important;
        color: #e3e9f7 !important;
        font-family: 'Segoe UI', 'SF Pro Display', 'Roboto', Arial, sans-serif;
    }
    .stSidebar {
        background-color: #002542 !important;
        border-right: 3px solid #0052cc !important;
    }
    .stSidebar .css-1d391kg, .stSidebar .css-1v3fvcr {
        color: #ffffff !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #0052cc 0%, #00b8d9 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 8px 0 rgba(0,184,217,0.3);
        border: none !important;
        font-weight: 600;
        transition: background 0.3s, box-shadow 0.3s;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #00b8d9 0%, #0052cc 100%) !important;
        box-shadow: 0 0 12px 0 rgba(0,184,217,0.4);
    }
    .stTextInput > div > input {
        background-color: #1a1f2e !important;
        color: #e3e9f7 !important;
        border: 2px solid #0052cc !important;
        border-radius: 8px !important;
    }
    /* Remove blue border from selectbox dropdowns */
    .stSelectbox > div > div {
        background-color: #1a1f2e !important;
        color: #e3e9f7 !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }
    .stDataFrame, .stTable {
        background-color: #1a1f2e !important;
        border-radius: 14px !important;
        box-shadow: 0 0 8px 0 rgba(0,184,217,0.15);
        color: #e3e9f7 !important;
    }
    .stCaption, .stMarkdown, .stExpanderHeader {
        color: #a0aec0 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00b8d9 !important;
        font-weight: 700 !important;
    }
    .stExpander {
        background-color: #1a1f2e !important;
        border-radius: 10px !important;
        color: #e3e9f7 !important;
    }
    .stAlert, .stInfo, .stSuccess, .stWarning, .stError {
        background: rgba(0,82,204,0.1) !important;
        border-left: 5px solid #00b8d9 !important;
        color: #e3e9f7 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

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
st.markdown("<h1 style='color:#00b8d9;font-weight:700;'>Agentic HR Access Control Demo</h1>", unsafe_allow_html=True)

# Sidebar navigation with icons
PAGE_HR_MUTATION_ENTRY = "HR Mutation Entry"
PAGE_AUDIT_TRAIL = "Audit Trail"
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=[PAGE_HR_MUTATION_ENTRY, PAGE_AUDIT_TRAIL],
        icons=["person-fill", "journal-text"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"background-color": "#002542", "padding": "0.5em 0.5em 2em 0.5em", "border-right": "3px solid #0052cc"},
            "icon": {"color": "#00b8d9", "font-size": "1.3em"},
            "nav-link": {"font-size": "1.1em", "color": "#fff", "margin":"0.2em 0", "border-radius": "6px"},
            "nav-link-selected": {"background-color": "#0052cc", "color": "#fff"},
        },
    )

if selected == PAGE_HR_MUTATION_ENTRY:
    st.markdown("<h2 style='color:#00b8d9;font-weight:700;'>HR Mutation Entry</h2>", unsafe_allow_html=True)
    st.caption("All fields are required unless marked optional. Please provide accurate information for auditability.")
    users_df = read_csv('users')
    user_options = users_df['UserID'] + " - " + users_df['Name']
    user_map = dict(zip(user_options, users_df['UserID']))
    with st.container():
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
        with st.spinner("Submitting mutation and triggering agent workflow..."):
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
                                summary_lines.append(f"<span style='color:#00b8d9;font-weight:600;'>Investigation Agent:</span> {inv_text}")
                            # RightsCheckAgent
                            rc_text = rc.get('response') or rc.get('error')
                            if rc_text:
                                summary_lines.append(f"<span style='color:#00b8d9;font-weight:600;'>Rights Check Agent:</span> {rc_text}")
                            # RequestForInformationAgent (user)
                            info_user_text = info_user.get('response') or info_user.get('error')
                            if info_user_text:
                                summary_lines.append(f"<span style='color:#00b8d9;font-weight:600;'>User Clarification Agent:</span> {info_user_text}")
                            # RequestForInformationAgent (manager)
                            info_manager_text = info_manager.get('response') or info_manager.get('error')
                            if info_manager_text:
                                summary_lines.append(f"<span style='color:#00b8d9;font-weight:600;'>Manager Validation Agent:</span> {info_manager_text}")
                            # AdvisoryAgent (final advisory)
                            advisory_text = advisory.get('response') or advisory.get('error')
                            if advisory_text:
                                summary_lines.append(f"<span style='color:#00b8d9;font-weight:600;'>Advisory Agent (Final Advisory):</span> {advisory_text}")
                            summary = "<br><br>".join(summary_lines) if summary_lines else str(agent_response)
                        else:
                            summary = agent_response.get('response', agent_response) if isinstance(agent_response, dict) else str(agent_response)
                        st.markdown(f"<div style='background:rgba(0,82,204,0.1);border-left:5px solid #00b8d9;padding:12px;border-radius:8px;color:#e3e9f7;'>Agent Workflow Summary:<br><br>{summary}</div>", unsafe_allow_html=True)
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


elif selected == PAGE_AUDIT_TRAIL:
    st.markdown("<h2 style='color:#00b8d9;font-weight:700;'>Audit Trail</h2>", unsafe_allow_html=True)
    try:
        audit_df = read_csv('audit_trail')
        # Coerce all columns to string type to avoid schema validation errors
        for col in audit_df.columns:
            audit_df[col] = audit_df[col].astype(str)
        st.dataframe(audit_df, use_container_width=True)
    except Exception as e:
        st.error(f"Error loading audit trail: {e}")



