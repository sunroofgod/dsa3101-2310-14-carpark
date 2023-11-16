import simpy
from simpy import Resource
from car import Car
import numpy as np
import params

class CarPark:
    """
    Represents a parking facility in a simulation.

    Attributes:
        name (str): The name or identifier of the car park.
        whiteLots (int): The total number of white parking lots available.
        redLots (int): The total number of red parking lots available.
        env (simpy.Environment): The SimPy environment in which the simulation runs.
        gracePeriod (int): The maximum period for waiting in car park.
        whiteCars (int): The number of white cars currently in the car park.
        redCars (int): The number of red cars currently in the car park.
        totalWhite (int): The total number of white cars served throughout the simulation.
        totalRed (int): The total number of red cars served throughout the simulation.
        whiteRejected (int): The total number of white cars turned away throughout the simulation.
        redRejected (int): The total number of red cars turned away throughout the simulation.
        whiteCars24 (list): The number of white cars in the car park at each hour.
        redCars24 (list): The number of red cars in the car park at each hour.
        whiteTotal24 (list): The total number of white cars served at each hour.
        redTotal24 (list): The total number of red cars served at each hour.
        whiteRejected24 (list): The total number of white cars turned away at each hour.
        redRejected24 (list): The total number of red cars turned away at each hour.
        spots (simpy.Resource): A SimPy resource representing the parking lots in the car park.

    Methods:
        get_name(): Get the name of the car park.
        grace_period(): Get the grace period for waiting to enter the car park.
        white_available(): Get the availability of white parking lots.
        red_available(): Get the availability of red parking lots.
        occupied(): Get the overall parking lot occupancy.
        enter(): Simulate a car entering the car park.
        exit(): Simulate a car leaving the car park.
        turn_away(): Simulate a car being turned away from the car park.
        record(): Record metrics for the current hour.
        stats(): Get statistics related to the car park.
        park_car(): Simulate a car parking in the car park.
    """

    def __init__(self, 
                 name : str, 
                 whiteLots : int,
                 redLots : int,
                 env : simpy.Environment,
                 gracePeriod = 10):
        """
        Initialize a CarPark object.
        
        Args:
            name (str): The name or identifier of the car park.
            whiteLots (int): The total number of white parking lots available.
            redLots (int): The total number of red parking lots available.
            env (simpy.Environment): The SimPy environment in which the simulation runs.
            gracePeriod (int, optional): The maximum period for waiting in car park (default is 10).
        
        Returns:
            None
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

        ## Track total cars turned away
        self.whiteRejected = 0
        self.redRejected = 0 

        ## Track metrics over 24 hours
        self.whiteCars24 = []
        self.redCars24 = []
        self.whiteTotal24 = []
        self.redTotal24 = []
        self.whiteRejected24 = []
        self.redRejected24 = []

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
            return 1 - round(self.whiteCars / self.whiteLots, 2)
        return self.whiteLots - self.whiteCars
    
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
            return 1 - round(self.redCars / self.redLots, 2)
        return self.redLots - self.redCars
    
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
        
    def turn_away(self, car : Car):
        """
        Simulate a car being turned away from the car park if there are no available parking lots.

        Args:
            car: A Car object representing the arriving car.

        Returns:
            str: The parking type ("red" for staff, "white" for others) of the turned-away car.
        """
        if car.get_type() == "staff":
            self.redRejected += 1
            return "red"
        else: 
            self.whiteRejected += 1
            return "white"
        
    def record(self):
        """
        Record metrics for the current hour.
        
        Returns:
            list: A list of metrics containing the following values:
                - The number of white cars in the car park.
                - The number of red cars in the car park.
                - The total number of white cars served.
                - The total number of red cars served.
                - The total number of white cars turned away (rejected).
                - The total number of red cars turned away (rejected).
        """
        self.whiteCars24.append(self.whiteCars)
        self.redCars24.append(self.redCars)
        self.whiteTotal24.append(self.totalWhite)
        self.redTotal24.append(self.totalRed)
        self.whiteRejected24.append(self.whiteRejected)
        self.redRejected24.append(self.redRejected)
        return self.stats()

    def stats(self):
        """
        Get statistics related to the car park.

        Returns:
            list: A list of statistics containing the following values:
                - The total number of white cars served.
                - The total number of red cars served.
                - The total number of white cars turned away (rejected).
                - The total number of red cars turned away (rejected).
                - The number of white cars in the car park at each hour.
                - The number of red cars in the car park at each hour.
        """
        return [self.whiteTotal24, 
                self.redTotal24, 
                self.whiteRejected24, 
                self.redRejected24, 
                self.whiteCars24, 
                self.redCars24]

    def park_car(self, car : Car):
        """
        Simulate a car parking in the car park.

        Args:
            car (Car): The car to be parked.

        Returns:
            int: A status code (e.g., 200) indicating the result of the parking operation.
        """
        with self.spots.request() as request:
            ## Car enter, increment respective count
            lot = self.enter(car)

            ## Wait for carpark lot up to grace period, if still no lot, leave
            wait = np.random.uniform(0, self.grace_period())
            res = yield request | self.env.timeout(wait)

            if request in res:

                ## Lot available but not correct lot type
                if (
                    (car.get_type() == "staff" and self.red_available() == 0) or 
                    (car.get_type() != "staff" and self.white_available() == 0)
                ):
                    ## Car exit, decrement respective count
                    self.turn_away(car)
                    self.exit(car)
                    return 200
                
                ## Car successfully found a lot and parked
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} parking on {lot} lot at {self.get_name()}")

                ## Get parking duration
                duration = car.park_duration(self.name, params.minutes_to_hours(self.env.now))
                assert duration >= 0
                yield self.env.timeout(duration)
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} exited {self.get_name()}. Parked for {duration:4.2f} minutes.")
            else:
                ## No lots found, car exit without parking
                self.turn_away(car)
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} exited {self.get_name()} without parking.")
            
            ## Car exit, decrement respective count
            self.exit(car)

        return 200
