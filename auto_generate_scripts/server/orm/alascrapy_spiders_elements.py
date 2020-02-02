from sqlalchemy import Column, ForeignKey, Integer, String, CHAR, Unicode, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class AlascrapySpiders(Base):
    __tablename__ = 'alascrapy_spiders'
    __table_args__ = {'schema':'temp', 'useexisting':True}
    
    spider_id = Column('spider_id', Integer, primary_key=True)
    source_id = Column('source_id', Integer)
    script_name = Column('script_name', String)
    crawl_type = Column('crawl_type', String)
    create_time = Column('create_time', DateTime)
    update_time = Column('update_time', DateTime)
    
class AlascrapyElements(Base):
    __tablename__ = 'alascrapy_elements'
    __table_args__ = {'schema':'temp', 'useexisting':True}
    
    element_id = Column('element_id', Integer, primary_key=True)
    spider_id = Column('spider_id', Integer)
    step_counter = Column('step_counter', Integer)
    function_name = Column('function_name', String)
    parameter_name = Column('parameter_name', String)
    parameter_value = Column('parameter_value', String)
    
def get_session():
    engine,session = None,None
    engine = create_engine('mysql+mysqldb://root:att.56@192.168.0.3:3306/temp')
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return engine, session
    
def update_spider_record(session, source_id, script_name, crawl_type = 'normal'):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        script_name_query = session.query(AlascrapySpiders).filter(AlascrapySpiders.script_name == script_name)
        spider_records = script_name_query.all()
        if spider_records:
            script_name_query.update({"source_id":source_id, "crawl_type":crawl_type, "update_time":time_now})
        else:
            spider_record = AlascrapySpiders(source_id = source_id, script_name = script_name, crawl_type = crawl_type, create_time = time_now, update_time = time_now)
            session.add(spider_record)
        session.commit()
    except Exception, e:
        print e
        session.rollback()
    pass


def get_spider_id(session, script_name):
    script_name_query = session.query(AlascrapySpiders).filter(AlascrapySpiders.script_name == script_name)
    spider_id = script_name_query.one().spider_id
    return spider_id


def update_element_record(session, spider_id, step_counter, function_name, parameter_name, parameter_value):
    try:
        spider_step_query = session.query(AlascrapyElements).filter(AlascrapyElements.spider_id == spider_id, AlascrapyElements.step_counter == step_counter)
        element_records = spider_step_query.all()
        if element_records:
            spider_step_query.update({"function_name":function_name, "parameter_name":parameter_name, "parameter_value":parameter_value})
        else:
            element_record = AlascrapyElements(spider_id = spider_id, step_counter = step_counter, function_name = function_name, parameter_name = parameter_name, parameter_value = parameter_value)
            session.add(element_record)
        session.commit()
    except Exception, e:
        print e
        session.rollback()
    pass


def close_session(engine,session):
    session.close()
    engine.dispose()
    

def main():
    engine, session = get_session()
    update_spider_record(session, 12345, 'abcdef', crawl_type = 'normal')
    spider_id = get_spider_id(session, 'abcdef')
    update_element_record(session, spider_id, 1, 'func_name_1', 'parm_name_1', 'parm_value_1')
    update_element_record(session, spider_id, 1, 'func_name_1', 'parm_name_2', 'parm_value_2')
    update_element_record(session, spider_id, 1, 'func_name_1', 'parm_name_3', 'parm_value_3')
    update_element_record(session, spider_id, 2, 'func_name_2', 'parm_name_1', 'parm_value_1')
    update_element_record(session, spider_id, 2, 'func_name_2', 'parm_name_2', 'parm_value_2')
    close_session(engine, session)
    

if __name__ == "__main__":
    main()
    
    
