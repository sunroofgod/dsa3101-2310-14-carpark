import os
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy

def connect_db():
    """
    Connect to the database and return a Connection object.
    
    Returns:
        sqlalchemy.engine.Connection: Connection object to the database.
    """
    load_dotenv('.env')
    DATABASE_NAME = os.environ['DATABASE_NAME']
    MYSQL_USERNAME = os.environ['MYSQL_USERNAME']
    MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
    CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@db:3306/{DATABASE_NAME}'
    print(CONNECTION_STRING)
    engine = sqlalchemy.create_engine(
        CONNECTION_STRING
    )
    db = engine.connect()
    return db

## connect to database
db = connect_db()

def get_table(table_name: str, db: sqlalchemy.engine.Connection=db):
    """
    Get the table from the database and return a Pandas DataFrame.
    
    Args:
        table_name (str): Name of the table in the database.
        db (sqlalchemy.engine.Connection): Connection object to the database.
        
    Returns:
        pandas.DataFrame: Pandas DataFrame of the table.
    """
    import pandas as pd

    # catch error of table not in database
    if not db.execute(text(f'''SELECT EXISTS (SELECT 1 FROM information_schema.tables \
                       WHERE table_name = '{table_name}') ''')).fetchone()[0]:
        raise ValueError(f"Table {table_name} does not exist in database")
    
    else:
        results = db.execute(text(f'''SELECT * FROM {table_name};'''))
        df = pd.DataFrame(results.fetchall(), columns=results.keys())
        return df
