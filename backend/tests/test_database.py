from database import create_all_tables, drop_all_tables
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import text
import unittest, os, sqlalchemy

class TestDatabaseSetUp(unittest.TestCase):

    def setUp(self) -> None:
        load_dotenv(find_dotenv())
        DATABASE_NAME = os.environ['DATABASE_NAME']
        MYSQL_USERNAME = os.environ['MYSQL_USERNAME']
        MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
        CONNECTION_STRING = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@localhost:3306/{DATABASE_NAME}'
        engine = sqlalchemy.create_engine(
            CONNECTION_STRING
        )
        db = engine.connect()
        self.db = db

    def test_creating_tables(self) -> None:
        create_all_tables(self.db)
        self.db.commit()
        print(f"Successfully CREATE visitors TABLE.")
        self.db.execute(text(
            """INSERT INTO visitors
            VALUES ('0001', 'cp0', '0001', '2022-12-25 12:00:00', '2022-12-25 13:01:00', 'staff', 61, 1.02, 0)
            """
            ))
        self.db.commit()
        print(f"Successfully INSERT INTO visitors TABLE.")

    def test_deleting_from_table(self) -> None:
        self.db.execute(text(
            """
            DELETE FROM visitors 
            WHERE IU='0001'
            """
            ))
        self.db.commit()
        print(f"Successfully DELETED ROW from visitors TABLE.")

    def test_dropping_tables(self) -> None:
        drop_all_tables(self.db)
        print(f"Successfully DROPPED visitors TABLE.")


if __name__ == "__main__":
    unittest.main()
