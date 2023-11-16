from sqlalchemy import text
import sqlalchemy
import os, sys
## append backend path to sys to import database module
path = os.getcwd()
sys.path.append(os.path.join(path, "backend"))
from database.mysql_connector import connect_db
from data_preprocessing.run_data_cleaning import load_and_clean_data
import time

## connect to database
# db = connect_db()

def drop_all_tables(db: sqlalchemy.engine.Connection) -> None:
    """
    Drop all tables in the database.
    
    Args:
        db (sqlalchemy.engine.Connection): Connection object to the database.
        
    Returns:
        None
    """
    db.execute(text(
        '''
        DROP TABLE IF EXISTS visitors;
        '''
    ))

def create_all_tables(db: sqlalchemy.engine.Connection) -> None:
    """
    Create all tables in the database.
    
    Args:
        db (sqlalchemy.engine.Connection): Connection object to the database.
    
    Returns:
        None
    """
    db.execute(text(
        '''CREATE TABLE IF NOT EXISTS visitors(
            IU VARCHAR(8) NOT NULL,
            carpark VARCHAR(10) NOT NULL,
            exit_id VARCHAR(4) NOT NULL,
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
    """
    Run data-preprocessing functions to obtain pd.Dataframe and upload into database

    Args:
        db (sqlalchemy.engine.Connection): Connection object to the database.

    Returns:
        None
    """
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
    """
    Drop all tables, create all tables, and load data into database.
    
    Args:
        db (sqlalchemy.engine.Connection): Connection object to the database.
        
    Returns:
        None
    """
    drop_all_tables(db)
    create_all_tables(db)
    load_local_data(db)
    return 200

if __name__ == '__main__':
    # time.sleep(30)
    db = connect_db()
    setup_database(db)
