import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import os
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Access Control Management System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .alert-card {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .danger-card {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
    .success-card {
        background-color: #d1eddc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
</style>
""", unsafe_allow_html=True)

# Data loading functions
@st.cache_data
def load_data():
    """Load all CSV data files"""
    data_path = Path(__file__).parent.parent / "data"
    
    try:
        users_df = pd.read_csv(data_path / "users.csv", comment="#")
        roles_df = pd.read_csv(data_path / "roles.csv", comment="#")
        authorisations_df = pd.read_csv(data_path / "authorisations.csv", comment="#")
        role_authorisations_df = pd.read_csv(data_path / "role_authorisations.csv", comment="#")
        hr_mutations_df = pd.read_csv(data_path / "hr_mutations.csv", comment="#")

        # Convert timestamp columns and make them timezone-naive for comparison
        if 'Timestamp' in hr_mutations_df.columns:
            hr_mutations_df['Timestamp'] = pd.to_datetime(hr_mutations_df['Timestamp']).dt.tz_localize(None)
        if 'GrantedOn' in authorisations_df.columns:
            authorisations_df['GrantedOn'] = pd.to_datetime(authorisations_df['GrantedOn']).dt.tz_localize(None)
        if 'ExpiresOn' in authorisations_df.columns:
            authorisations_df['ExpiresOn'] = pd.to_datetime(authorisations_df['ExpiresOn']).dt.tz_localize(None)

        return {
            'users': users_df,
            'roles': roles_df,
            'authorisations': authorisations_df,
            'role_authorisations': role_authorisations_df,
            'hr_mutations': hr_mutations_df
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def analyze_anomalies(data):
    """Analyze mutations for potential anomalies"""
    anomalies = []
    hr_mutations = data['hr_mutations']
    authorisations = data['authorisations']
    users = data['users']
    
    # Detect salary changes above threshold
    salary_changes = hr_mutations[hr_mutations['FieldChanged'] == 'Salary'].copy()
    if not salary_changes.empty:
        salary_changes['OldValue'] = pd.to_numeric(salary_changes['OldValue'], errors='coerce')
        salary_changes['NewValue'] = pd.to_numeric(salary_changes['NewValue'], errors='coerce')
        salary_changes['Change'] = salary_changes['NewValue'] - salary_changes['OldValue']
        salary_changes['PercentChange'] = (salary_changes['Change'] / salary_changes['OldValue']) * 100
        
        # Flag salary changes > 20%
        high_salary_changes = salary_changes[abs(salary_changes['PercentChange']) > 20]
        for _, row in high_salary_changes.iterrows():
            anomalies.append({
                'type': 'High Salary Change',
                'mutation_id': row['MutationID'],
                'user': row['ChangedFor'],
                'details': f"Salary change of {row['PercentChange']:.1f}%",
                'severity': 'High' if abs(row['PercentChange']) > 50 else 'Medium',
                'timestamp': row['Timestamp']
            })
    
    # Detect terminated users with active authorizations
    terminated_users = users[users['Status'].isin(['Terminated', 'Removed'])]['UserID'].tolist()
    active_auth_terminated = authorisations[
        (authorisations['UserID'].isin(terminated_users)) & 
        (authorisations['Status'] == 'Active')
    ]
    
    for _, row in active_auth_terminated.iterrows():
        anomalies.append({
            'type': 'Terminated User with Active Access',
            'mutation_id': f"AUTH-{row['AuthorisationID']}",
            'user': row['UserID'],
            'details': f"Access to {row['System']} still active",
            'severity': 'High',
            'timestamp': datetime.now()
        })
    
    # Detect after-hours changes
    after_hours_mutations = hr_mutations.copy()
    if not after_hours_mutations.empty:
        after_hours_mutations['Hour'] = after_hours_mutations['Timestamp'].dt.hour
        after_hours = after_hours_mutations[
            (after_hours_mutations['Hour'] < 7) | (after_hours_mutations['Hour'] > 18)
        ]
        
        for _, row in after_hours.iterrows():
            anomalies.append({
                'type': 'After-Hours Change',
                'mutation_id': row['MutationID'],
                'user': row['ChangedFor'],
                'details': f"{row['ChangeType']} at {row['Timestamp'].strftime('%H:%M')}",
                'severity': 'Medium',
                'timestamp': row['Timestamp']
            })
    
    return pd.DataFrame(anomalies)

def main():
    """Main application function"""
    # Sidebar navigation
    st.sidebar.title("🔐 Access Control")
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Mutations Review", "Authorizations", "Anomaly Detection", "Audit Trail"]
    )
    
    # Load data
    data = load_data()
    if data is None:
        st.error("Failed to load data. Please check if data files exist.")
        return
    
    # Main content area
    if page == "Dashboard":
        show_dashboard(data)
    elif page == "Mutations Review":
        show_mutations_review(data)
    elif page == "Authorizations":
        show_authorizations(data)
    elif page == "Anomaly Detection":
        show_anomaly_detection(data)
    elif page == "Audit Trail":
        show_audit_trail(data)

def show_dashboard(data):
    """Show main dashboard with overview metrics"""
    st.markdown('<div class="main-header">Access Control Dashboard</div>', unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = len(data['users'])
        active_users = len(data['users'][data['users']['Status'] == 'Active'])
        st.metric("Total Users", total_users, delta=f"{active_users} active")
    
    with col2:
        total_auth = len(data['authorisations'])
        active_auth = len(data['authorisations'][data['authorisations']['Status'] == 'Active'])
        st.metric("Authorizations", total_auth, delta=f"{active_auth} active")
    
    with col3:
        recent_mutations = len(data['hr_mutations'][
            data['hr_mutations']['Timestamp'] > (datetime.now() - timedelta(days=7))
        ])
        st.metric("Recent Changes", recent_mutations, delta="Last 7 days")
    
    with col4:
        anomalies = analyze_anomalies(data)
        total_anomalies = len(anomalies) if not anomalies.empty else 0
        high_severity = len(anomalies[anomalies['severity'] == 'High']) if not anomalies.empty and 'severity' in anomalies.columns else 0
        st.metric("Anomalies", total_anomalies, delta=f"{high_severity} high severity")
    
    st.divider()
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Status Distribution")
        status_counts = data['users']['Status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index, 
                    title="User Status Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Authorizations by System")
        system_counts = data['authorisations']['System'].value_counts()
        fig = px.bar(x=system_counts.index, y=system_counts.values,
                    title="Active Authorizations by System")
        fig.update_xaxes(title="System")
        fig.update_yaxes(title="Count")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Mutations")
    recent_mutations = data['hr_mutations'].sort_values('Timestamp', ascending=False).head(10)
    st.dataframe(recent_mutations, use_container_width=True)

def show_mutations_review(data):
    """Show mutations review page"""
    st.markdown('<div class="main-header">Mutations Review</div>', unsafe_allow_html=True)
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        change_types = ['All'] + list(data['hr_mutations']['ChangeType'].unique())
        selected_type = st.selectbox("Change Type", change_types)
    
    with col2:
        environments = ['All'] + list(data['hr_mutations']['Environment'].unique())
        selected_env = st.selectbox("Environment", environments)
    
    with col3:
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=7), datetime.now()),
            max_value=datetime.now()
        )
    
    # Filter data
    filtered_mutations = data['hr_mutations'].copy()
    
    if selected_type != 'All':
        filtered_mutations = filtered_mutations[filtered_mutations['ChangeType'] == selected_type]
    
    if selected_env != 'All':
        filtered_mutations = filtered_mutations[filtered_mutations['Environment'] == selected_env]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_mutations = filtered_mutations[
            (filtered_mutations['Timestamp'].dt.date >= start_date) &
            (filtered_mutations['Timestamp'].dt.date <= end_date)
        ]
    
    # Display results
    st.subheader(f"Mutations ({len(filtered_mutations)} records)")
    
    # Add action buttons for each mutation
    if not filtered_mutations.empty:
        for idx, row in filtered_mutations.iterrows():
            with st.expander(f"Mutation {row['MutationID']} - {row['ChangeType']} for {row['ChangedFor']}"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Changed By:** {row['ChangedBy']}")
                    st.write(f"**Field:** {row['FieldChanged']}")
                    st.write(f"**Old Value:** {row['OldValue']}")
                    st.write(f"**New Value:** {row['NewValue']}")
                    st.write(f"**Timestamp:** {row['Timestamp']}")
                    st.write(f"**Metadata:** {row['Metadata']}")
                
                with col2:
                    if st.button(f"Approve", key=f"approve_{row['MutationID']}"):
                        st.success(f"Mutation {row['MutationID']} approved!")
                
                with col3:
                    if st.button(f"Flag", key=f"flag_{row['MutationID']}"):
                        st.warning(f"Mutation {row['MutationID']} flagged for review!")
    else:
        st.info("No mutations found for the selected criteria.")

def show_authorizations(data):
    """Show authorizations management page"""
    st.markdown('<div class="main-header">Authorization Management</div>', unsafe_allow_html=True)
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        active_count = len(data['authorisations'][data['authorisations']['Status'] == 'Active'])
        st.metric("Active Authorizations", active_count)
    
    with col2:
        revoked_count = len(data['authorisations'][data['authorisations']['Status'] == 'Revoked'])
        st.metric("Revoked Authorizations", revoked_count)
    
    with col3:
        # Count expired authorizations
        current_time = datetime.now()
        expired_count = len(data['authorisations'][
            (data['authorisations']['ExpiresOn'].notna()) &
            (data['authorisations']['ExpiresOn'] < current_time) &
            (data['authorisations']['Status'] == 'Active')
        ])
        st.metric("Expired (Active)", expired_count)
    
    st.divider()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        systems = ['All'] + list(data['authorisations']['System'].unique())
        selected_system = st.selectbox("System", systems)
    
    with col2:
        statuses = ['All'] + list(data['authorisations']['Status'].unique())
        selected_status = st.selectbox("Status", statuses)
    
    with col3:
        access_levels = ['All'] + list(data['authorisations']['AccessLevel'].unique())
        selected_access = st.selectbox("Access Level", access_levels)
    
    # Filter authorizations
    filtered_auth = data['authorisations'].copy()
    
    if selected_system != 'All':
        filtered_auth = filtered_auth[filtered_auth['System'] == selected_system]
    
    if selected_status != 'All':
        filtered_auth = filtered_auth[filtered_auth['Status'] == selected_status]
    
    if selected_access != 'All':
        filtered_auth = filtered_auth[filtered_auth['AccessLevel'] == selected_access]
    
    # Merge with user data for better display
    auth_with_users = filtered_auth.merge(
        data['users'][['UserID', 'Name', 'Department', 'Status']], 
        on='UserID', 
        how='left',
        suffixes=('_Auth', '_User')
    )
    
    # Display authorizations
    st.subheader(f"Authorizations ({len(filtered_auth)} records)")
    
    # Highlight expired authorizations
    if not auth_with_users.empty:
        # Color code by status
        def highlight_status(row):
            current_time = datetime.now()
            if row['Status_Auth'] == 'Revoked':
                return ['background-color: #f8d7da'] * len(row)
            elif row['Status_User'] in ['Terminated', 'Removed'] and row['Status_Auth'] == 'Active':
                return ['background-color: #fff3cd'] * len(row)
            elif pd.notna(row['ExpiresOn']) and row['ExpiresOn'] < current_time and row['Status_Auth'] == 'Active':
                return ['background-color: #fff3cd'] * len(row)
            else:
                return [''] * len(row)
        
        styled_df = auth_with_users.style.apply(highlight_status, axis=1)
        st.dataframe(styled_df, use_container_width=True)
    else:
        st.info("No authorizations found for the selected criteria.")

def show_anomaly_detection(data):
    """Show anomaly detection page"""
    st.markdown('<div class="main-header">Anomaly Detection</div>', unsafe_allow_html=True)
    
    # Generate anomalies
    anomalies = analyze_anomalies(data)
    
    if not anomalies.empty:
        # Summary by severity
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_count = len(anomalies[anomalies['severity'] == 'High'])
            st.markdown(f'<div class="danger-card"><h3>High Severity</h3><h2>{high_count}</h2></div>', 
                       unsafe_allow_html=True)
        
        with col2:
            medium_count = len(anomalies[anomalies['severity'] == 'Medium'])
            st.markdown(f'<div class="alert-card"><h3>Medium Severity</h3><h2>{medium_count}</h2></div>', 
                       unsafe_allow_html=True)
        
        with col3:
            low_count = len(anomalies[anomalies['severity'] == 'Low'])
            st.markdown(f'<div class="success-card"><h3>Low Severity</h3><h2>{low_count}</h2></div>', 
                       unsafe_allow_html=True)
        
        st.divider()
        
        # Anomaly details
        st.subheader("Detected Anomalies")
        
        # Group by severity
        for severity in ['High', 'Medium', 'Low']:
            severity_anomalies = anomalies[anomalies['severity'] == severity]
            if not severity_anomalies.empty:
                st.markdown(f"### {severity} Severity Anomalies")
                
                for _, anomaly in severity_anomalies.iterrows():
                    with st.expander(f"{anomaly['type']} - {anomaly['user']}"):
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.write(f"**Type:** {anomaly['type']}")
                            st.write(f"**User:** {anomaly['user']}")
                            st.write(f"**Details:** {anomaly['details']}")
                            st.write(f"**Timestamp:** {anomaly['timestamp']}")
                        
                        with col2:
                            if st.button(f"Send Alert", key=f"alert_{anomaly['mutation_id']}"):
                                st.success("Alert sent to compliance controller!")
                                # Here you would integrate with email/notification system
    else:
        st.success("No anomalies detected!")

def show_audit_trail(data):
    """Show audit trail page"""
    st.markdown('<div class="main-header">Audit Trail</div>', unsafe_allow_html=True)
    
    # Timeline view of all changes
    st.subheader("Change Timeline")
    
    # Combine mutations and authorization changes
    audit_events = []
    
    # Add HR mutations
    for _, row in data['hr_mutations'].iterrows():
        audit_events.append({
            'timestamp': row['Timestamp'],
            'event_type': 'HR Mutation',
            'user': row['ChangedFor'],
            'action': f"{row['ChangeType']} {row['FieldChanged']}",
            'details': f"Changed by {row['ChangedBy']}: {row['OldValue']} → {row['NewValue']}",
            'environment': row['Environment']
        })
    
    # Add authorization grants (using GrantedOn date)
    for _, row in data['authorisations'].iterrows():
        if pd.notna(row['GrantedOn']):
            audit_events.append({
                'timestamp': row['GrantedOn'],
                'event_type': 'Authorization Grant',
                'user': row['UserID'],
                'action': f"Granted {row['AccessLevel']} access to {row['System']}",
                'details': f"Granted by {row['GrantedBy']}",
                'environment': 'System'
            })
    
    # Convert to DataFrame and sort
    audit_df = pd.DataFrame(audit_events)
    if not audit_df.empty:
        audit_df = audit_df.sort_values('timestamp', ascending=False)
        
        # Filter options
        col1, col2 = st.columns(2)
        
        with col1:
            event_types = ['All'] + list(audit_df['event_type'].unique())
            selected_event = st.selectbox("Event Type", event_types)
        
        with col2:
            selected_user = st.selectbox("User", ['All'] + list(audit_df['user'].unique()))
        
        # Apply filters
        filtered_audit = audit_df.copy()
        
        if selected_event != 'All':
            filtered_audit = filtered_audit[filtered_audit['event_type'] == selected_event]
        
        if selected_user != 'All':
            filtered_audit = filtered_audit[filtered_audit['user'] == selected_user]
        
        # Display audit trail
        st.subheader(f"Audit Events ({len(filtered_audit)} records)")
        
        for _, event in filtered_audit.head(50).iterrows():  # Limit to 50 for performance
            with st.container():
                col1, col2, col3 = st.columns([2, 3, 2])
                
                with col1:
                    st.write(f"**{event['timestamp'].strftime('%Y-%m-%d %H:%M')}**")
                    st.write(f"*{event['event_type']}*")
                
                with col2:
                    st.write(f"**User:** {event['user']}")
                    st.write(f"**Action:** {event['action']}")
                    st.write(f"**Details:** {event['details']}")
                
                with col3:
                    st.write(f"**Environment:** {event['environment']}")
                
                st.divider()
    else:
        st.info("No audit events found.")

if __name__ == "__main__":
    main()