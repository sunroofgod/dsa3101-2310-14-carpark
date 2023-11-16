import numpy as np
from params import CP_LIST, get_parking_duration_stats

park_du = get_parking_duration_stats(CP_LIST)
class Car:
    """
    Represents a car in a parking simulation.

    Attributes:
        id (int): A unique identifier for the car.
        type (str): The type of parking (e.g., "visitor", "staff").
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
    
    def park_duration(self, cp : str, hour : int):
        """
        Generate a random parking duration for a car based on car park type.

        This method generates a random parking duration for a car based on the specified car park type (cp).
        It uses a normal distribution with parameters for the mean and standard deviation specific to the car park type.

        Args:
            cp (str): The car park type (e.g., 'hourly', 'staff', 'visitor').

        Returns:
            float: A random parking duration in minutes for the given car park type.
        """
        tup = park_du[(cp, self.type, hour)]
        return max(0, np.random.normal(tup[0], tup[1]))
