import os
from dotenv import load_dotenv
from sqlalchemy import text
import sqlalchemy
from data_preprocessing.run_data_cleaning import load_and_clean_data

load_dotenv('.env')

DATABASE_NAME = os.environ['DATABASE_NAME']
MYSQL_USERNAME = os.environ['MYSQL_USERNAME']
MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@localhost:3306/{DATABASE_NAME}'
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
            IU VARCHAR(8) NOT NULL,
            carpark VARCHAR(10) NOT NULL,
            exit_id VARCHAR(3) NOT NULL,
            enter_dt DATETIME NOT NULL,
            exit_dt DATETIME NOT NULL,
            type VARCHAR(10) NOT NULL,
            parked_min INT NOT NULL,
            parked_hrs INT NOT NULL,
            parked_days INT NOT NULL,
            CONSTRAINT pk_visitors PRIMARY KEY (IU, carpark, enter_dt)
            );'''
    ))
    db.commit()
    print("ALL TABLES CREATED SUCCESSFULLY")

def load_local_data(db: sqlalchemy.engine.Connection) -> None:
    '''run data-preprocessing functions to obtain pd.Dataframe and upload into database'''
    file_paths = {'Cp5': '../data/raw_Cp5_a.csv',
                'Cp_multiple': '../data/raw_Cp33a45b6b_a.csv',
                'Cp10': '../data/Sample raw data format - duration_cp10_Apr2023_a.csv'}

    cleaned_visitor_data = load_and_clean_data(file_paths)
    cleaned_visitor_data.to_sql(
        name='visitors',
        con=db,
        if_exists='append',
        index=False,
     )
    
    db.commit()
    print("ALL DATA POPULATED")

def setup_database(db: sqlalchemy.engine.Connection) -> None:
    drop_all_tables(db)
    create_all_tables(db)
    load_local_data(db)

