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

    def park_car(self, car):
        with self.spots.request() as request:
            yield request
            car.park(self.id)
            yield self.env.timeout(np.random.uniform(3600, 18000))  # Simulate car's stay time
            car.leave()

