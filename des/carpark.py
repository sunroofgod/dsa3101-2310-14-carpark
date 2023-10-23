import numpy as np
from car import Car
import simpy
from simpy import Resource

class CarPark:

    def __init__(self, 
                 id : str, 
                 capacity : int, 
                 env : simpy.Environment):
        
        self.id = id
        self.capacity = capacity
        self.env = env
        self.spots = Resource(env, capacity=capacity)
        self.whiteTaken = 0
        self.redTaken = 0
        self.total = 0

    def stats(self):
        return (self.total, self.perc_filled())
    
    def perc_filled(self):
        return round(((self.whiteTaken + self.redTaken) / self.capacity) * 100, 2)

    def park_car(self, car):
        with self.spots.request() as request:
            yield request
            car.park(self.id)
            if car.get_type() == 'staff':
                self.redTaken += 1
            else:
                self.whiteTaken += 1
            
            yield self.env.timeout(np.random.uniform(3600, 18000))  # Simulate car's stay time
            car.leave()
            if car.get_type() == 'staff':
                self.redTaken -= 1
            else:
                self.whiteTaken -= 1

            self.total += 1

