import simpy
from simpy import Resource
from car import Car

class CarPark:
    """
    Represents a parking facility in a simulation.

    Attributes:
        name (str): The name or identifier of the car park.
        whiteLots (int): The total number of white parking lots available.
        redLots (int): The total number of red parking lots available.
        env (simpy.Environment): The SimPy environment in which the simulation runs.
        gracePeriod (int): The maximum period for waiting in a carpark for a parking lot.
        whiteCars (int): The number of cars parked at a white lot currently in the car park.
        redCars (int): The number of cars parked at a red lot currently in the car park.
        totalWhite (int): The total number of white cars served.
        totalRed (int): The total number of red cars served.
        spots (simpy.Resource): The resource representing available parking spots.

    Methods:
        get_name(self): Get the name of the car park.
        grace_period(self): Get the maximum period for waiting.
        white_available(self, ratio=False): Get the availability of white parking lots.
        red_available(self, ratio=False): Get the availability of red parking lots.
        occupied(self, ratio=False): Get the overall parking lot occupancy.
        enter(self, car): Simulate a car entering the car park.
        exit(self, car): Simulate a car leaving the car park.
        stats(self): Get statistics about the car park.
        park_car(self, car): Simulate a car parking in the car park.

    """

    def __init__(self, 
                 name : str, 
                 whiteLots : int,
                 redLots : int,
                 env : simpy.Environment,
                 gracePeriod = 10):
        """
        Initializes a new car park.

        Args:
            name (str): The name or identifier of the car park.
            whiteLots (int): The total number of white parking lots available.
            redLots (int): The total number of red parking lots available.
            env (simpy.Environment): The SimPy environment in which the simulation runs.
            gracePeriod (int, optional): The maximum period for waiting in car park (default is 10).
        """
        
        self.name = name # name of carpark
        self.env = env 
        self.whiteLots = whiteLots # total number of white lots
        self.redLots = redLots # total number of red lots
        self.capacity = whiteLots + redLots
        self.gracePeriod = gracePeriod

        ## Track number of cars currently in carpark
        self.whiteCars = 0 
        self.redCars = 0

        ## Track total cars served throughout
        self.totalWhite = 0 
        self.totalRed = 0

        self.spots = Resource(env, capacity=self.capacity)

    def get_name(self):
        """
        Get the name of the car park.

        Returns:
            str: The name of the car park.
        """
        return self.name
    
    def grace_period(self):
        """
        Get the grace period for waiting to enter the car park.

        Returns:
            int: The grace period in minutes.
        """
        return self.gracePeriod
    
    def white_available(self, ratio=False):
        """
        Get the availability of white parking lots.

        Args:
            ratio (bool, optional): If True, return availability as a ratio (default is False).

        Returns:
            float or int: The number of available white parking lots or the availability ratio.
        """
        if self.whiteLots == 0:
            return 0
        if ratio:
            return round(self.whiteCars / self.whiteLots, 2)
        return self.whiteCars / self.whiteLots
    
    def red_available(self, ratio=False):
        """
        Get the availability of red parking lots.

        Args:
            ratio (bool, optional): If True, return availability as a ratio (default is False).

        Returns:
            float or int: The number of available red parking lots or the availability ratio.
        """
        if self.redLots == 0:
            return 0
        if ratio:
            return round(self.redCars / self.redLots, 2)
        return self.redCars / self.redLots
    
    def occupied(self, ratio=False):
        """
        Get the overall parking lot occupancy.

        Args:
            ratio (bool, optional): If True, return occupancy as a ratio (default is False).

        Returns:
            float or int: The overall occupancy or the occupancy ratio.
        """
        if self.capacity == 0:
            return 0
        if ratio:
            return round((self.whiteCars + self.redCars) / self.capacity, 2)
        return self.redCars + self.whiteCars
    
    def enter(self, car : Car):
        """
        Simulate a car entering the car park.

        Args:
            car (Car): The car to be parked.

        Returns:
            str: The type of parking lot where the car is parked ("white" or "red").
        """
        if car.get_type() == 'staff':
            self.redCars += 1
            self.totalRed += 1
            return "red"
        else:
            self.whiteCars += 1
            self.totalWhite += 1
            return "white"
    
    def exit(self, car : Car):
        """
        Simulate a car leaving the car park.

        Args:
            car (Car): The car leaving the car park.

        Returns:
            str: The type of parking lot where the car was parked ("white" or "red").
        """
        if car.get_type() == 'staff':
            self.redCars -= 1
            return "red"
        else:
            self.whiteCars -= 1
            return "white"

    def stats(self):
        """
        Get statistics about the car park.

        Returns:
            tuple: A tuple containing the total number of white cars, total number of red cars,
            and the overall parking lot occupancy as a ratio.
        """
        return (self.totalWhite, self.totalRed, self.occupied(ratio=True))

    def park_car(self, car : Car):
        """
        Simulate a car parking in the car park.

        Args:
            car (Car): The car to be parked.

        Returns:
            int: A status code (e.g., 200) indicating the result of the parking operation.
        """
        with self.spots.request() as request:
            lot = self.enter(car)
            
            ## Wait for carpark lot up to grace period, if still no lot, leave
            res = yield request | self.env.timeout(self.grace_period())

            if request in res: # park
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} parking on {lot} lot at {self.get_name()}")
                duration = car.park_duration()
                assert duration >= 0
                yield self.env.timeout(duration)  # Parking duration
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} exited {self.get_name()}. Parked for {duration:4.2f} minutes")
            
            self.exit(car)

        return 200
