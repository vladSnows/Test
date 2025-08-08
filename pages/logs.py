import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import EvRkProcDqApex
from db.generic_utils import get_unique_column_values, get_paginated_data, logs_query, get_total_count_orm

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

if 'isInitialOpen_LOGS' not in st.session_state:
    st.session_state['isInitialOpen_LOGS'] = True
else:
    st.session_state['isInitialOpen_LOGS'] = False

if st.session_state.get('isInitialOpen_LOGS', True):
    session_defaults = {
        'logs_last_filters': {
            'batch_id': None,
            'dq_code': None,
            'process_name': None
        }
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

for key, default_value in st.session_state.logs_last_filters.items():
    if key not in st.session_state.logs_last_filters or st.session_state.logs_last_filters[key] is None:
        if key == 'batch_id':
            st.session_state.logs_last_filters[key] = get_unique_column_values(session, EvRkProcDqApex.t_batch_id)
        if key == 'dq_code':
            st.session_state.logs_last_filters[key] = get_unique_column_values(session, EvRkProcDqApex.dq_code)
        if key == 'process_name':
            st.session_state.logs_last_filters[key] = get_unique_column_values(session, EvRkProcDqApex.t_process_name)

# Always use the full set of unique values for selectbox options
batch_id_options = [v for v in st.session_state.logs_last_filters['batch_id'] if v is not None]
dq_code_options = [v for v in st.session_state.logs_last_filters['dq_code'] if v is not None]
process_name_options = [v for v in st.session_state.logs_last_filters['process_name'] if v is not None]

col0, col1, col2 = st.columns([1, 0.5, 1.5])

with col0:
    batch_id = st.selectbox("**Batch ID**", options=[None] + sorted(batch_id_options), key='selected_batch_id')
with col1:
    dq_code = st.selectbox("**DQ Code**", options=[None] + sorted(dq_code_options), key='selected_dq_code')
with col2:
    process_name = st.selectbox("**Process Name**", options=[None] + sorted(process_name_options), key='selected_process_name')

filters = []
if st.session_state.get('selected_batch_id') is not None:
    filters.append(EvRkProcDqApex.t_batch_id == st.session_state['selected_batch_id'])
if st.session_state.get('selected_dq_code') is not None:
    filters.append(EvRkProcDqApex.dq_code == st.session_state['selected_dq_code'])
if st.session_state.get('selected_process_name') is not None:
    filters.append(EvRkProcDqApex.t_process_name == st.session_state['selected_process_name'])

# Defensive: Remove any non-SQLAlchemy filter expressions (e.g., int, str)
filters = [f for f in filters if hasattr(f, 'compare') or hasattr(f, 'key') or hasattr(f, 'left')]

# Ensure filters is always a list
if not isinstance(filters, (list, tuple)):
    filters = [filters]

filters_changed = (
    st.session_state.logs_last_filters.get("batch_id") != st.session_state.get('selected_batch_id') or
    st.session_state.logs_last_filters.get("dq_code") != st.session_state.get('selected_dq_code') or
    st.session_state.logs_last_filters.get("process_name") != st.session_state.get('selected_process_name')
)

if filters_changed:
    st.session_state.logs_offset = 0
    st.session_state.logs_data_cache = pd.DataFrame()
    st.session_state.logs_initial_load_done = False
    st.session_state.logs_last_filters["batch_id"] = st.session_state.get('selected_batch_id')
    st.session_state.logs_last_filters["dq_code"] = st.session_state.get('selected_dq_code')
    st.session_state.logs_last_filters["process_name"] = st.session_state.get('selected_process_name')

if "logs_offset" not in st.session_state:
    st.session_state.logs_offset = 0
if "logs_limit" not in st.session_state:
    st.session_state.logs_limit = 20
if "logs_data_cache" not in st.session_state:
    st.session_state.logs_data_cache = pd.DataFrame()
if "logs_initial_load_done" not in st.session_state:
    st.session_state.logs_initial_load_done = False

offset = st.session_state.logs_offset
limit = st.session_state.logs_limit

if "logs_total_count" not in st.session_state or filters_changed:
    st.session_state.logs_total_count = get_total_count_orm(
        session,
        session.query(EvRkProcDqApex),
        filters
    )

if not st.session_state.logs_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        logs_query(session),
        filters,
        offset,
        limit,
        order_by=EvRkProcDqApex.processing_date,
        desc=True
    )
    new_data = pd.DataFrame([r._asdict() for r in results])
    st.session_state.logs_data_cache = new_data
    st.session_state.logs_offset = st.session_state.logs_limit
    st.session_state.logs_initial_load_done = True

st.dataframe(st.session_state.logs_data_cache, use_container_width=True)
st.markdown(f"**Showing {len(st.session_state.logs_data_cache)} of {st.session_state.logs_total_count} records**")

if len(st.session_state.logs_data_cache) < st.session_state.logs_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            logs_query(session),
            filters,
            offset,
            limit,
            order_by=EvRkProcDqApex.processing_date,
            desc=True
        )
        new_data = pd.DataFrame([r._asdict() for r in results])
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
