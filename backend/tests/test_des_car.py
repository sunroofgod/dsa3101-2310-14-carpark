from des.car import Car
import io
import unittest
from contextlib import redirect_stdout

class TestDESCar(unittest.TestCase):

    def setUp(self) -> None:
        self.car = Car(id=1, type="staff")

    def tearDown(self) -> None:
        del self.car

    def test_get_id(self) -> None:
        self.assertEqual(self.car.get_id(), 1)

    def test_park(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            self.car.park(cp="cp10")
        self.assertEqual(f.getvalue(), f"Car {self.car.get_id()} parks at cp10 red lot")

    def test_leave(self) -> None:
        f = io.StringIO()
        with redirect_stdout(f):
            self.car.leave()
        self.assertEqual(f.getvalue(), f"Car {self.car.get_id()} leaves")

if __name__ == "__main__":
    unittest.main()
