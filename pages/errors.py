import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import MtProcessingError
from db.generic_utils import get_unique_column_values, get_paginated_data, errors_query, get_total_count_orm

st.title("Błędy przetwarzań")

# Initialize connection
if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

# Get DB connection
engine = u.getEngine()
Session = sessionmaker(bind=engine)
session = Session()

if 'isInitialOpen_ERRORS' not in st.session_state:
    st.session_state['isInitialOpen_ERRORS'] = True
else:
    st.session_state['isInitialOpen_ERRORS'] = False

if st.session_state.get('isInitialOpen_ERRORS', True):
    session_defaults = {
        'errors_last_filters': {
            'workflow_name': None,
            'processing_date': None
        }
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

for key, default_value in st.session_state.errors_last_filters.items():
    if key not in st.session_state.errors_last_filters or st.session_state.errors_last_filters[key] is None:
        if key == 'workflow_name':
            st.session_state.errors_last_filters[key] = get_unique_column_values(session, MtProcessingError.workflow_name)

# Always use the full set of unique values for selectbox options
workflow_name_options = [v for v in st.session_state.errors_last_filters['workflow_name'] if v is not None]
col0, col1 = st.columns([1.5, 1])
with col0:
    workflow_name = st.multiselect("**Workflow Name**", options=sorted(workflow_name_options), key='selected_workflow_name')
with col1:
    processing_date = st.date_input("**Processing/Error Date**", value=None, key='selected_processing_date')

filters = []
if st.session_state.get('selected_workflow_name'):
    filters.extend([MtProcessingError.workflow_name == wname for wname in st.session_state['selected_workflow_name']])
if st.session_state.get('selected_processing_date') is not None:
    filters.append(MtProcessingError.error_timestamp.cast(pd.Timestamp).date() == st.session_state['selected_processing_date'])

# Defensive: Remove any non-SQLAlchemy filter expressions (e.g., int, str)
filters = [f for f in filters if hasattr(f, 'compare') or hasattr(f, 'key') or hasattr(f, 'left')]

# Ensure filters is always a list
if not isinstance(filters, (list, tuple)):
    filters = [filters]

filters_changed = (
    st.session_state.errors_last_filters.get("workflow_name") != st.session_state.get('selected_workflow_name') or
    st.session_state.errors_last_filters.get("processing_date") != st.session_state.get('selected_processing_date')
)

if filters_changed:
    st.session_state.errors_offset = 0
    st.session_state.errors_data_cache = pd.DataFrame()
    st.session_state.errors_initial_load_done = False
    st.session_state.errors_last_filters["workflow_name"] = st.session_state.get('selected_workflow_name')
    st.session_state.errors_last_filters["processing_date"] = st.session_state.get('selected_processing_date')

if "errors_offset" not in st.session_state:
    st.session_state.errors_offset = 0
if "errors_limit" not in st.session_state:
    st.session_state.errors_limit = 20
if "errors_data_cache" not in st.session_state:
    st.session_state.errors_data_cache = pd.DataFrame()
if "errors_initial_load_done" not in st.session_state:
    st.session_state.errors_initial_load_done = False

offset = st.session_state.errors_offset
limit = st.session_state.errors_limit

if "errors_total_count" not in st.session_state or filters_changed:
    st.session_state.errors_total_count = get_total_count_orm(
        session,
        session.query(MtProcessingError),
        filters
    )

if not st.session_state.errors_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        errors_query(session),
        filters,
        offset,
        limit,
        order_by=MtProcessingError.error_timestamp,
        desc=True
    )
    new_data = pd.DataFrame([r._asdict() for r in results])
    st.session_state.errors_data_cache = new_data
    st.session_state.errors_offset = st.session_state.errors_limit
    st.session_state.errors_initial_load_done = True

st.dataframe(st.session_state.errors_data_cache, use_container_width=True)
st.markdown(f"**Showing {len(st.session_state.errors_data_cache)} of {st.session_state.errors_total_count} records**")

if len(st.session_state.errors_data_cache) < st.session_state.errors_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            errors_query(session),
            filters,
            offset,
            limit,
            order_by=MtProcessingError.error_timestamp,
            desc=True
        )
        new_data = pd.DataFrame([r._asdict() for r in results])
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
