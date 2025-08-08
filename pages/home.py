import streamlit as st
import pandas as pd
from utils import helper as u
from sqlalchemy.orm import sessionmaker
from db.models import MtProcessingState
from db.generic_utils import get_unique_column_values, get_paginated_data, get_total_count_orm, home_query
from st_aggrid import AgGrid, GridOptionsBuilder

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

if 'isInitialOpen_HOME'  not in st.session_state:
    st.session_state['isInitialOpen_HOME'] = True
else:
    st.session_state['isInitialOpen_HOME'] = False

if st.session_state.get('isInitialOpen_HOME', True):
    # Session defaults
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

# Active filters
col0, col1, col2, col3 = st.columns([1.5, 1, 3, 3])

with col0:
    processing_name = st.selectbox("**Processing Name**", options=[None] + sorted(st.session_state.home_last_filters['processing_names']), key='PROCESSING_NAME')

with col1:
    processing_date = st.date_input("**Processing Date**", value=None)

filters = []
if processing_name:
    filters.append(MtProcessingState.processing_name == processing_name)
if processing_date:
    filters.append(MtProcessingState.processing_date == processing_date)

# Reset danych jeśli zmieniono filtr
# Upewnij się, że wszystkie klucze istnieją
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

# Stan sesji
if "home_offset" not in st.session_state:
    st.session_state.home_offset = 0
if "home_limit" not in st.session_state:
    st.session_state.home_limit = 20
if "home_data_cache" not in st.session_state:
    st.session_state.home_data_cache = pd.DataFrame()
if "home_initial_load_done" not in st.session_state:
    st.session_state.home_initial_load_done = False

params_dict = {
    "processing_name": processing_name if processing_name else None,
    "processing_date": processing_date if processing_date else None
}

offset = st.session_state.home_offset
limit = st.session_state.home_limit

# Wywołanie
if "home_total_count" not in st.session_state or filters_changed:
    st.session_state.home_total_count = get_total_count_orm(
        session,
        home_query(session),
        filters
    )

# Automatyczne pierwsze ładowanie
if not st.session_state.home_initial_load_done or filters_changed:
    results = get_paginated_data(
        session,
        home_query(session),
        filters,
        offset,
        limit,
        order_by=None,
        desc=True
    )
    new_data = pd.DataFrame([r._asdict() for r in results])
    st.session_state.home_data_cache = new_data
    st.session_state.home_offset = st.session_state.home_limit
    st.session_state.home_initial_load_done = True

# Wyświetlenie danych
if st.session_state.home_data_cache is not None and not st.session_state.home_data_cache.empty and len(st.session_state.home_data_cache.columns) > 0:
    gb = GridOptionsBuilder.from_dataframe(st.session_state.home_data_cache)
    gb.configure_default_column(
        filter=True,
        sortable=True,
        groupable=True,
        resizable=True,
        wrapText=True,
        autoHeight=True,
        enableRowGroup=True,
        enablePivot=True,
        enableValue=True,
        headerCheckboxSelection=True,
    )
    gb.configure_grid_options(
        pagination=True,
        paginationAutoPageSize=False,
        domLayout='normal',
        suppressRowClickSelection=False,
        rowSelection='single',
        enableRangeSelection=True,
        suppressAggFuncInHeader=False,
        animateRows=True,
        defaultColDef={
            "resizable": True,
            "sortable": True,
            "filter": True
        },
        groupSelectsChildren=True,
        suppressRowDeselection=False,
        suppressCellSelection=False,
        suppressHorizontalScroll=False
    )
    gb.configure_side_bar()
    grid_options = gb.build()
    AgGrid(st.session_state.home_data_cache, gridOptions=grid_options, enable_enterprise_modules=True, theme="streamlit", update_mode="NO_UPDATE", pagination=True, height=400)
    st.markdown(f"**Showing {len(st.session_state.home_data_cache)} of {st.session_state.home_total_count} records**")
else:
    st.info("No data to display for the selected filters.")

# Przycisk ładowania
if len(st.session_state.home_data_cache) < st.session_state.home_total_count:
    if st.button("Pokaż więcej"):
        results = get_paginated_data(
            session,
            home_query(session),
            filters,
            offset,
            limit,
            order_by=None,
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
