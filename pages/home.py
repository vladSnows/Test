import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import MtProcessingState
from db.generic_utils import get_unique_column_values, get_total_count_orm, get_paginated_data, home_query

st.title("Przetwarzania DMSF")

# Initialize connection
if "connector" not in st.session_state:
    st.session_state.connector = None
if "connected" not in st.session_state:
    st.session_state.connected = False

# Get DB connection
engine = u.getEngine()
Session = sessionmaker(bind=engine)
session = Session()

if 'isInitialOpen_HOME' not in st.session_state:
    st.session_state['isInitialOpen_HOME'] = True
else:
    st.session_state['isInitialOpen_HOME'] = False

if st.session_state.get('isInitialOpen_HOME', True):
    session_defaults = {
        'home_last_filters': {
            'processing_names': None,
            'processing_date': None
        }
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

for key, default_value in st.session_state.home_last_filters.items():
    if key not in st.session_state.home_last_filters or st.session_state.home_last_filters[key] is None:
        if key == 'processing_names':
            st.session_state.home_last_filters[key] = get_unique_column_values(session, MtProcessingState.processing_name)

col0, col1 = st.columns([1.5, 1])

with col0:
    processing_name_options = [v for v in st.session_state.home_last_filters['processing_names'] if v is not None]
    processing_name = st.selectbox("**Processing Name**", options=[None] + sorted(processing_name_options), key='PROCESSING_NAME')
with col1:
    processing_date = st.date_input("**Processing Date**", value=None)

filters = []
if processing_name:
    filters.append(MtProcessingState.processing_name == processing_name)
if processing_date:
    filters.append(MtProcessingState.processing_date == processing_date)

# Defensive: Remove any non-SQLAlchemy filter expressions (e.g., int, str)
filters = [f for f in filters if hasattr(f, 'compare') or hasattr(f, 'key') or hasattr(f, 'left')]

# Ensure filters is always a list
if not isinstance(filters, (list, tuple)):
    filters = [filters]

for key in ["processing_name", "processing_date"]:
    if key not in st.session_state.home_last_filters:
        st.session_state.home_last_filters[key] = None

filters_changed = (
    st.session_state.home_last_filters["processing_name"] != processing_name or
    st.session_state.home_last_filters["processing_date"] != processing_date
)

if filters_changed:
    st.session_state.home_offset = 0
    st.session_state.home_data_cache = pd.DataFrame()
    st.session_state.home_initial_load_done = False
    st.session_state.home_last_filters["processing_name"] = processing_name
    st.session_state.home_last_filters["processing_date"] = processing_date

if "home_offset" not in st.session_state:
    st.session_state.home_offset = 0
if "home_limit" not in st.session_state:
    st.session_state.home_limit = 20
if "home_data_cache" not in st.session_state:
    st.session_state.home_data_cache = pd.DataFrame()
if "home_initial_load_done" not in st.session_state:
    st.session_state.home_initial_load_done = False

offset = st.session_state.home_offset
limit = st.session_state.home_limit

if "home_total_count" not in st.session_state or filters_changed:
    st.session_state.home_total_count = get_total_count_orm(
        session,
        session.query(MtProcessingState),
        filters
    )

if not st.session_state.home_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        home_query(session),
        filters,
        offset,
        limit,
        order_by=MtProcessingState.processing_date,
        desc=True
    )
    new_data = pd.DataFrame([r._asdict() for r in results])
    st.session_state.home_data_cache = new_data
    st.session_state.home_offset = st.session_state.home_limit
    st.session_state.home_initial_load_done = True

st.dataframe(st.session_state.home_data_cache, use_container_width=True)
st.markdown(f"**Showing {len(st.session_state.home_data_cache)} of {st.session_state.home_total_count} records**")

if len(st.session_state.home_data_cache) < st.session_state.home_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            home_query(session),
            filters,
            offset,
            limit,
            order_by=MtProcessingState.processing_date,
            desc=True
        )
        new_data = pd.DataFrame([r._asdict() for r in results])
        st.session_state.home_data_cache = pd.concat([st.session_state.home_data_cache, new_data], ignore_index=True)
        st.session_state.home_offset += st.session_state.home_limit
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
