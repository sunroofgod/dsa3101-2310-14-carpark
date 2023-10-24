import simpy
from simpy import Resource

class CarPark:

    def __init__(self, 
                 name : str, 
                 whiteLots : int,
                 redLots : int,
                 env : simpy.Environment,
                 gracePeriod = 10):
        
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
        return self.name
    
    def grace_period(self):
        return self.gracePeriod
    
    def white_available(self, ratio=False):
        if self.whiteLots == 0:
            return 0
        if ratio:
            return round(self.whiteCars / self.whiteLots, 2)
        return self.whiteCars / self.whiteLots
    
    def red_available(self, ratio=False):
        if self.redLots == 0:
            return 0
        if ratio:
            return round(self.redCars / self.redLots, 2)
        return self.redCars / self.redLots
    
    def occupied(self, ratio=False):
        if self.capacity == 0:
            return 0
        if ratio:
            return round((self.whiteCars + self.redCars) / self.capacity, 2)
        return self.redCars + self.whiteCars
    
    def enter(self, car):
        if car.get_type() == 'staff':
            self.redCars += 1
            self.totalRed += 1
            return "red"
        else:
            self.whiteCars += 1
            self.totalWhite += 1
            return "white"
    
    def exit(self, car):
        if car.get_type() == 'staff':
            self.redCars -= 1
            return "red"
        else:
            self.whiteCars -= 1
            return "white"

    def stats(self):
        return (self.totalWhite, self.totalRed, self.occupied(ratio=True))

    def park_car(self, car):
        with self.spots.request() as request:
            lot = self.enter(car)
            
            ## Wait for carpark lot up to grace period, if still no lot, leave
            res = yield request | self.env.timeout(self.grace_period())

            if request in res: # park
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} parking on {lot} lot at {self.get_name()}")
                duration = car.park_duration()
                yield self.env.timeout(duration)  # Parking duration
                print(f"{self.env.now:<7.2f}: Car {car.get_id()} parked at {self.get_name()} for {duration:4.2f} minutes")
            
            self.exit(car)

        return 200
