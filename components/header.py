import streamlit as st

def render_header():
    st.markdown(
        """
        <div style='display: flex; align-items: center; justify-content: space-between; padding: 0.5em 0;'>
            <h1 style='margin: 0;'>DMSF Professional App</h1>
            <span style='font-size: 1.1em; color: #888;'>Status & Reports</span>
        </div>
        <hr style='margin-top: 0.5em; margin-bottom: 1em;'>
        """,
        unsafe_allow_html=True
    )

