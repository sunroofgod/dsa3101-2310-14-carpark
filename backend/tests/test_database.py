from database import db, create_all_tables, drop_all_tables
from sqlalchemy import text
import unittest

class TestDatabaseSetUp(unittest.TestCase):

    def setUp(self) -> None:
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
