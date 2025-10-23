import streamlit as st  # type: ignore

st.set_page_config(
    page_title="Access Control Management System",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.title("🔐 Access Control")
st.sidebar.info("Navigation will be added here.")

st.markdown(
    """
    <div style='text-align:center; margin-top:3rem;'>
        <h1>Access Control Management System</h1>
        <p><em>This is a placeholder for the future UI. Implementation will follow the architecture and wireframes.</em></p>
    </div>
    """,
    unsafe_allow_html=True
)