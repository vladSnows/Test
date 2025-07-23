import streamlit as st
import pandas as pd
from utils.db import get_dmsf_cml_connection, get_processing_names, get_total_count, get_paginated_processing_state
from utils.session import get_session_state, init_session_vars
from components.footer import render_footer
from components.header import render_header
from core.config import APP_TITLE, AUTH_USERS

"""
Page: Przetwarzania DMSF
Displays DMSF processing status records.
"""

st.title("Przetwarzania DMSF")
session = get_session_state()

# Use cached DB connection
connection_DMSF = get_dmsf_cml_connection()
if connection_DMSF is None:
    st.error("Could not connect to the database. Please check your credentials and connection settings.")
    st.stop()

# Initialize session variables
init_session_vars({
    "home_last_filters": {},
    "home_offset": 0,
    "home_limit": 20,
    "home_data_cache": pd.DataFrame(),
    "home_initial_load_done": False
})

with st.spinner("Loading processing names..."):
    processing_names = get_processing_names(connection_DMSF, "DEV03_DMSF_CML")

processing_names = get_processing_names()

col0, col1, col2 = st.columns([2, 2, 2])

with col0:
    processing_name = st.selectbox("**Processing Name**", [""] + processing_names)

with col1:
    processing_date = st.date_input("**Processing Date**", value=None)

for key in ["processing_name", "processing_date"]:
    if key not in session.home_last_filters:
        session.home_last_filters[key] = None

filters_changed = (
    session.home_last_filters["processing_name"] != processing_name or
    session.home_last_filters["processing_date"] != processing_date
)

if filters_changed:
    session.home_offset = 0
    session.home_data_cache = pd.DataFrame()
    session.home_initial_load_done = False
    session.home_last_filters["processing_name"] = processing_name
    session.home_last_filters["processing_date"] = processing_date

offset = session.home_offset
limit = session.home_limit

if "home_total_count" not in session or filters_changed:
    session.home_total_count = get_total_count(connection_DMSF, params_dict, "DEV03_DMSF_CML")

if not session.home_initial_load_done or filters_changed:
    with st.spinner("Loading data..."):
        new_data = get_paginated_processing_state(connection_DMSF, params_dict, session.home_offset, session.home_limit, "DEV03_DMSF_CML")
        session.home_data_cache = new_data
        session.home_offset = session.home_limit
        session.home_initial_load_done = True

st.dataframe(session.home_data_cache, use_container_width=True)

st.markdown(f"**Showing {len(session.home_data_cache)} of {session.home_total_count} records**")

if len(session.home_data_cache) < session.home_total_count:
    if st.button("Pokaż więcej"):
        with st.spinner("Loading more data..."):
            new_data = get_paginated_processing_state(connection_DMSF, params_dict, session.home_offset, session.home_limit, "DEV03_DMSF_CML")
            session.home_data_cache = pd.concat([session.home_data_cache, new_data], ignore_index=True)
            session.home_offset += session.home_limit
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
