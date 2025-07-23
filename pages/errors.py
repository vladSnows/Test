import streamlit as st
import pandas as pd
from utils.db import get_dmsf_cml_connection, get_workflow_names, get_total_count, get_paginated_processing_error
from utils.session import get_session_state, init_session_vars
from components.footer import render_footer
from components.header import render_header
from core.config import APP_TITLE, AUTH_USERS

"""
Page: Błędy przetwarzań
Displays error records from DMSF processing.
"""

st.title("Błędy przetwarzań")
session = get_session_state()

# Initialize DB connection
connection_DMSF = get_dmsf_cml_connection()
if connection_DMSF is None:
    st.error("Could not connect to the database. Please check your credentials and connection settings.")
    st.stop()

with st.spinner("Loading workflow names..."):
    workflow_names = get_workflow_names(connection_DMSF, "DEV03_DMSF_CML")

col0, col1, col2, col3 = st.columns([1.5, 1, 3, 3])

with col0:
    workflow_name = st.selectbox("**Workflow Name**", [""] + workflow_names)

with col1:
    processing_date = st.date_input("**Processing/Error Date**", value=None)

# Initialize session variables
init_session_vars({
    "errors_last_filters": {},
    "errors_offset": 0,
    "errors_limit": 20,
    "errors_data_cache": pd.DataFrame(),
    "errors_initial_load_done": False
})

for key in ["workflow_name", "processing_date"]:
    if key not in session.errors_last_filters:
        session.errors_last_filters[key] = None

filters_changed = (
    session.errors_last_filters["workflow_name"] != workflow_name or
    session.errors_last_filters["processing_date"] != processing_date
)

if filters_changed:
    session.errors_offset = 0
    session.errors_data_cache = pd.DataFrame()
    session.errors_initial_load_done = False
    session.errors_last_filters["workflow_name"] = workflow_name
    session.errors_last_filters["processing_date"] = processing_date

if "errors_offset" not in st.session_state:
    st.session_state.errors_offset = 0
if "errors_limit" not in st.session_state:
    st.session_state.errors_limit = 20
if "errors_data_cache" not in st.session_state:
    st.session_state.errors_data_cache = pd.DataFrame()
if "errors_initial_load_done" not in st.session_state:
    st.session_state.errors_initial_load_done = False

params_dict = {
    "workflow_name": workflow_name if workflow_name else None,
    "processing_date": processing_date if processing_date else None
}

offset = st.session_state.errors_offset
limit = st.session_state.errors_limit

if "errors_total_count" not in st.session_state or filters_changed:
    st.session_state.errors_total_count = get_total_count(connection_DMSF, params_dict, "DEV03_DMSF_CML")

if not st.session_state.errors_initial_load_done or filters_changed:
    with st.spinner("Loading error data..."):
        new_data = get_paginated_processing_error(connection_DMSF, params_dict, st.session_state.errors_offset, st.session_state.errors_limit, "DEV03_DMSF_CML")
        st.session_state.errors_data_cache = new_data
        st.session_state.errors_offset = st.session_state.errors_limit
        st.session_state.errors_initial_load_done = True

st.dataframe(st.session_state.errors_data_cache, use_container_width=True)

st.markdown(f"**Showing {len(st.session_state.errors_data_cache)} of {st.session_state.errors_total_count} records**")

if len(st.session_state.errors_data_cache) < st.session_state.errors_total_count:
    if st.button("Pokaż więcej"):
        with st.spinner("Loading more error data..."):
            new_data = get_paginated_processing_error(connection_DMSF, params_dict, st.session_state.errors_offset, st.session_state.errors_limit, "DEV03_DMSF_CML")
            st.session_state.errors_data_cache = pd.concat([st.session_state.errors_data_cache, new_data], ignore_index=True)
            st.session_state.errors_offset += st.session_state.errors_limit
            st.rerun()
else:
    st.info("All records loaded.")

st.markdown(
    """
    <style>
    .stDataFrame > div {
        height: 55vh !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

render_footer()
