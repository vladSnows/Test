from db.models import MtProcessingState, MtProcessingError, EvRkProcDqApex


def get_unique_column_values(session, column):
    values = session.query(column).distinct().all()
    return [v[0] for v in values if v[0] is not None]


def get_paginated_data(session, query, filters, offset, limit, order_by=None, desc=False):
    if filters:
        query = query.filter(*filters)
    if order_by is not None:
        if desc:
            query = query.order_by(order_by.desc())
        else:
            query = query.order_by(order_by)
    query = query.offset(offset).limit(limit)
    return query.all()


# Queries for each page
home_query = lambda session: session.query(
    MtProcessingState.processing_name.label("PROCESSING NAME"),
    MtProcessingState.batch_id.label("BATCH ID"),
    MtProcessingState.processing_date.label("PROCESSING DATE"),
    MtProcessingState.processing_state.label("PROCESSING STATE"),
    MtProcessingState.prc_period_flag.label("PRC PERIOD FLAG"),
    MtProcessingState.processing_mode.label("PROCESSING MODE"),
    MtProcessingState.scheduling_date.label("SCHEDULING_DATE"),
)

errors_query = lambda session: session.query(
    MtProcessingError.t_batch_id.label("Batch ID"),
    MtProcessingError.t_process_name.label("Process Name"),
    MtProcessingError.t_process_exec_id.label("Process Exec ID"),
    MtProcessingError.table_name.label("Table Name"),
    MtProcessingError.workflow_name.label("Workflow Name"),
    MtProcessingError.mapping_name.label("Mapping Name"),
    MtProcessingError.error_timestamp.label("Error Timestamp"),
    MtProcessingError.error_msg.label("Error Msg"),
)

logs_query = lambda session: session.query(
    EvRkProcDqApex.t_batch_id.label("Batch ID"),
    EvRkProcDqApex.t_process_name.label("Process Name"),
    EvRkProcDqApex.t_process_exec_id.label("Process Exec ID"),
    EvRkProcDqApex.dq_code.label("DQ Code"),
    EvRkProcDqApex.dq_msg.label("DQ Msg"),
    EvRkProcDqApex.dq_add_msg.label("DQ Add Msg"),
    EvRkProcDqApex.dq_msg_object.label("DQ Msg Object"),
    EvRkProcDqApex.dq_msg_object_value.label("DQ Msg Object Value"),
    EvRkProcDqApex.rec_id.label("Rec ID"),
    EvRkProcDqApex.rec_col01.label("Rec Col01"),
    EvRkProcDqApex.rec_col02.label("Rec Col02"),
    EvRkProcDqApex.rec_col03.label("Rec Col03"),
    EvRkProcDqApex.processing_date.label("Processing Date"),
    EvRkProcDqApex.processing_name.label("Processing Name"),
    EvRkProcDqApex.processing_mode.label("Processing Mode"),
)
