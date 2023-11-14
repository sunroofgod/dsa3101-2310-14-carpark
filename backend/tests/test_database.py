from database import connect_db
from sqlalchemy import text
import unittest

class TestDatabase(unittest.TestCase):

    def setUp(self) -> None:
        self.db = connect_db()
        print(f"Successfully connected with DB.")

    def test_creating_tables(self) -> None:
        self.db.execute(text(
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
        print(f"Successfully CREATE visitors TABLE.")
        self.db.execute(text(
            '''INSERT INTO visitors
            VALUES ('0001', 'cp0', '0001', '2022-12-25 12:00:00', '2022-12-25 13:01:00', 'staff', 61, 1.02, 0)
            '''
            ))
        print(f"Successfully INSERT INTO visitors TABLE.")
        self.db.commit()

if __name__ == "__main__":
    unittest.main()
