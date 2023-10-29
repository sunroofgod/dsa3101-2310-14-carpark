import numpy as np
from params import get_parking_duration_stats

park_du = get_parking_duration_stats()
class Car:
    """
    Represents a car in a parking simulation.

    Attributes:
        id (int): A unique identifier for the car.
        type (str): The type of parking (e.g., "visitor," "staff").
    """

    def __init__(self, id : int, type="visitor"):
        """
        Initializes a new car.

        Args:
            id (int): A unique identifier for the car.
            type (str, optional): The type of parking (default is "visitor").
        """
        self.id = id
        self.type = type.lower()

    def get_id(self):
        """
        Get the unique identifier of the car.

        Returns:
            int: The car's unique identifier.
        """
        return self.id

    def get_type(self):
        """
        Get the type of parking for the car.

        Returns:
            str: The type of parking for the car (e.g., "visitor," "staff").
        """
        return self.type

    def park(self, cp : str):
        """
        Simulates the car parking at a specific location.

        Args:
            cp (str): The name or identifier of the parking location.

        Returns:
            None
        """
        colour = "white"
        if self.type == "staff":
            colour = "red"
        print(f"Car {self.id} parks at {cp} {colour} lot")
        return 

    def leave(self):
        """
        Simulates the car leaving the parking location.

        Returns:
            None
        """
        print(f"Car {self.id} leaves")
        return
    
    def park_duration(self, cp : str):
        """
        Generates a random parking duration for the car.

        Returns:
            float: The parking duration in minutes, following a normal distribution.
        """
        tup = park_du[(cp, self.type)]
        return max(0, np.random.normal(tup[0], tup[1]))