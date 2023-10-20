import os
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy

load_dotenv('.env')

MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
CONNECTION_STRING = f'mysql://username:password@localhost:port/database'
NUM_OF_TABLES = 1

engine = sqlalchemy.create_engine(
    CONNECTION_STRING
)
db = engine.connect()

def drop_all_tables(db: sqlalchemy.engine.Connection) -> None:
    db.execute(text(
        '''
        DROP TABLE IF EXISTS visitors;
        '''
    ))

def create_all_tables(db: sqlalchemy.engine.Connection) -> None:
    db.execute(text(
        '''CREATE TABLE IF NOT EXISTS visitors(
            exit_id VARCHAR(3) NOT NULL,
            IU VARCHAR(8) NOT NULL,
            enter_dt DATE NOT NULL,
            exit_dt DATE NOT NULL,
            hourly_du INTEGER NOT NULL,
            staff_du INTEGER NOT NULL,
            student_du INTEGER NOT NULL,
            esp_du INTEGER NOT NULL'''
    ))
    db.commit()
    print("ALL TABLES CREATED SUCCESSFULLY")

def load_local_data(db: sqlalchemy.engine.Connection) -> None:
    # TO ADD: run data-preprocessing functions to obtain pd.Dataframe
    # ---
    # EXAMPLE:
    #
    # cleaned_visitor_data = pd.Dataframe()
    # cleaned_vistor_data.to_sql(
    #    name='visitors',
    #    con=db,
    #    if_exists='append',
    #    index=False,
    # )
    db.commit()
    print("ALL DATA POPULATED")

def setup_database(db: sqlalchemy.engine.Connection) -> None:
    drop_all_tables(db)
    create_all_tables(db)
    load_local_data(db)

