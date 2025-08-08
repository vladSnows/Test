from sqlalchemy import Column, String, Date, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class MtProcessingState(Base):
    __tablename__ = 'MT_PROCESSING_STATE'
    __table_args__ = {'schema': 'DEV03_DMSF_CML'}

    processing_name = Column('PROCESSING_NAME', String(30), primary_key=True, nullable=False)
    batch_id = Column('BATCH_ID', String(12), nullable=False)
    processing_date = Column('PROCESSING_DATE', Date, nullable=False)
    processing_state = Column('PROCESSING_STATE', String(2), nullable=False)
    prc_period_flag = Column('PRC_PERIOD_FLAG', String(1), nullable=True)
    processing_mode = Column('PROCESSING_MODE', String(30), nullable=True)
    scheduling_date = Column('SCHEDULING_DATE', Date, nullable=True)
    t_upddate = Column('T_UPDDATE', Date, nullable=True)
    t_upduser = Column('T_UPDUSER', String(30), nullable=True)
    remap_batch_id = Column('REMAP_BATCH_ID', String(12), nullable=True)

class MtProcessingError(Base):
    __tablename__ = 'MT_PROCESSING_ERROR'
    __table_args__ = {'schema': 'DEV03_DMSF_CML'}

    t_batch_id = Column('T_BATCH_ID', String(50), primary_key=True)
    t_process_name = Column('T_PROCESS_NAME', String(100))
    t_process_exec_id = Column('T_PROCESS_EXEC_ID', String(100))
    table_name = Column('TABLE_NAME', String(100))
    workflow_name = Column('WORKFLOW_NAME', String(100))
    mapping_name = Column('MAPPING_NAME', String(100))
    error_timestamp = Column('ERROR_TIMESTAMP', DateTime)
    error_msg = Column('ERROR_MSG', Text)

class EvRkProcDqApex(Base):
    __tablename__ = 'EV_RK_PROC_DQ_APEX'
    __table_args__ = {'schema': 'DEV03_DMSF_EXL'}

    t_batch_id = Column('T_BATCH_ID', String(50), primary_key=True)
    t_process_name = Column('T_PROCESS_NAME', String(100))
    t_process_exec_id = Column('T_PROCESS_EXEC_ID', String(100))
    dq_code = Column('DQ_CODE', String(100))
    dq_msg = Column('DQ_MSG', Text)
    dq_add_msg = Column('DQ_ADD_MSG', Text)
    dq_msg_object = Column('DQ_MSG_OBJECT', String(100))
    dq_msg_object_value = Column('DQ_MSG_OBJECT_VALUE', String(100))
    rec_id = Column('REC_ID', String(100))
    rec_col01 = Column('REC_COL01', String(100))
    rec_col02 = Column('REC_COL02', String(100))
    rec_col03 = Column('REC_COL03', String(100))
    processing_date = Column('PROCESSING_DATE', Date)
    processing_name = Column('PROCESSING_NAME', String(100))
    processing_mode = Column('PROCESSING_MODE', String(100))
