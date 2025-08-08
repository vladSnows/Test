import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import EvRkProcDqApex
from db.generic_utils import get_unique_column_values, get_paginated_data, get_total_count_orm

st.title("LOGi Data Quality")


# Initialize connection
if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

# Get DB connection
engine = u.getEngine()
Session = sessionmaker(bind=engine)
session = Session()
connection_DMSF = engine.raw_connection()

# Remove st.cache_data from get_unique_column_values usage for dropdowns
batch_ids = get_unique_column_values(session, EvRkProcDqApex.t_batch_id)
dq_codes = get_unique_column_values(session, EvRkProcDqApex.dq_code)
process_names = get_unique_column_values(session, EvRkProcDqApex.t_process_name)

# Active filters
col0, col1, col2, col3 = st.columns([1, 0.5, 1.5, 3])

with col0:
    batch_id = st.selectbox("**Batch ID**", [""] + batch_ids)
with col1:
    dq_code = st.selectbox("**DQ Code**", [""] + [int(code) if code is not None and str(code).isdigit() else code for code in dq_codes])
with col2:
    process_name = st.selectbox("**Process Name**", [""] + process_names)

# Reset filters if changed
if "logs_last_filters" not in st.session_state or not isinstance(st.session_state.logs_last_filters, dict):
    st.session_state.logs_last_filters = {}

for key in ["batch_id", "dq_code", "process_name"]:
    if key not in st.session_state.logs_last_filters:
        st.session_state.logs_last_filters[key] = None

# Fix: On first load, do not apply any filters (show all records)
if (
    st.session_state.logs_last_filters["batch_id"] is None and
    st.session_state.logs_last_filters["dq_code"] is None and
    st.session_state.logs_last_filters["process_name"] is None and
    batch_id == "" and dq_code == "" and process_name == ""
):
    batch_id = None
    dq_code = None
    process_name = None
    # Also reset filters_changed to True to force full reload
    filters_changed = True
else:
    filters_changed = (
        st.session_state.logs_last_filters["batch_id"] != batch_id or
        st.session_state.logs_last_filters["dq_code"] != dq_code or
        st.session_state.logs_last_filters["process_name"] != process_name
    )

if filters_changed:
    st.session_state.logs_offset = 0
    st.session_state.logs_data_cache = pd.DataFrame()
    st.session_state.logs_initial_load_done = False
    st.session_state.logs_last_filters["batch_id"] = batch_id
    st.session_state.logs_last_filters["dq_code"] = dq_code
    st.session_state.logs_last_filters["process_name"] = process_name

if "logs_offset" not in st.session_state:
    st.session_state.logs_offset = 0
if "logs_limit" not in st.session_state:
    st.session_state.logs_limit = 20
if "logs_data_cache" not in st.session_state:
    st.session_state.logs_data_cache = pd.DataFrame()
if "logs_initial_load_done" not in st.session_state:
    st.session_state.logs_initial_load_done = False

params_dict = {
    "batch_id": batch_id if batch_id else None,
    "dq_code": dq_code if dq_code else None,
    "process_name": process_name if process_name else None
}

offset = st.session_state.logs_offset
limit = st.session_state.logs_limit

# Replace raw SQL count with SQLAlchemy ORM count
filters = []
# Only add filters if the value is not None and not an empty string
if batch_id not in (None, ""):
    filters.append(EvRkProcDqApex.t_batch_id == batch_id)
if dq_code not in (None, ""):
    filters.append(EvRkProcDqApex.dq_code == str(dq_code))
if process_name not in (None, ""):
    filters.append(EvRkProcDqApex.t_process_name == process_name)

if "logs_total_count" not in st.session_state or filters_changed:
    st.session_state.logs_total_count = get_total_count_orm(
        session,
        session.query(EvRkProcDqApex),
        filters
    )

# Use SQLAlchemy for paginated data
if not st.session_state.logs_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        session.query(EvRkProcDqApex),
        filters,
        st.session_state.logs_offset,
        st.session_state.logs_limit,
        order_by=EvRkProcDqApex.processing_date,
        desc=True
    )
    new_data = pd.DataFrame([r.__dict__ for r in results])
    if '_sa_instance_state' in new_data.columns:
        new_data = new_data.drop('_sa_instance_state', axis=1)
    st.session_state.logs_data_cache = new_data
    st.session_state.logs_offset = st.session_state.logs_limit
    st.session_state.logs_initial_load_done = True

st.dataframe(st.session_state.logs_data_cache, use_container_width=True)

st.markdown(f"**Showing {len(st.session_state.logs_data_cache)} of {st.session_state.logs_total_count} records**")

if len(st.session_state.logs_data_cache) < st.session_state.logs_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            session.query(EvRkProcDqApex),
            filters,
            st.session_state.logs_offset,
            st.session_state.logs_limit,
            order_by=EvRkProcDqApex.processing_date,
            desc=True
        )
        new_data = pd.DataFrame([r.__dict__ for r in results])
        if '_sa_instance_state' in new_data.columns:
            new_data = new_data.drop('_sa_instance_state', axis=1)
        st.session_state.logs_data_cache = pd.concat([st.session_state.logs_data_cache, new_data], ignore_index=True)
        st.session_state.logs_offset += st.session_state.logs_limit
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
