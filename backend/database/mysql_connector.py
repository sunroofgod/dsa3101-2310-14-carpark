import os
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy

def connect_db():
    '''
    returns a sqlalchemy.engine.Connection object to connect to database storing processed data
    '''
    load_dotenv('.env')
    DATABASE_NAME = os.environ['DATABASE_NAME']
    MYSQL_USERNAME = os.environ['MYSQL_USERNAME']
    MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
    CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@localhost:3306/{DATABASE_NAME}'

    engine = sqlalchemy.create_engine(
        CONNECTION_STRING
    )
    db = engine.connect()
    return db

db = connect_db()

def get_table(table_name: str, db: sqlalchemy.engine.Connection=db):
    '''
    returns a pandas DataFrame object containing all rows from table_name
    '''
    import pandas as pd

    # catch error of table not in database
    if not db.execute(text(f'''SELECT EXISTS (SELECT 1 FROM information_schema.tables \
                       WHERE table_name = '{table_name}') ''')).fetchone()[0]:
        raise ValueError(f"Table {table_name} does not exist in database")
    
    else:
        results = db.execute(text(f'''SELECT * FROM {table_name};'''))
        df = pd.DataFrame(results.fetchall(), columns=results.keys())
        return df
