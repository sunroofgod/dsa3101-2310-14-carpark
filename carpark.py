import numpy as np
from car import Car
import simpy
from simpy import Environment, Resource

class CarPark:

    def __init__(self, 
                 id : str, 
                 capacity : int, 
                 env : simpy.Environment):
        
        self.id = id
        self.capacity = capacity
        self.env = env
        self.spots = Resource(env, capacity=capacity)

    # def get_hour(self):
    #     return self.env.now % 3600
    
    # def get_minute(self):
    #     return self.env.now % 60
    
    def car_gen(self, arrivalRate):
        car_id = 1
        while True:
            # Generate random arrival time intervals following a Poisson distribution
            arrival_time = np.random.poisson(arrivalRate)

            yield self.env.timeout(arrival_time)  # Wait for the next car to arrive

            car_type = "hourly" if np.random.random() < 0.8 else "staff"  # 80% hourly, 20% staff

            with self.spots.request() as request:
                yield request  # Request a parking spot

                car = Car(car_id, car_type)
                car.arrive(self.env.now)
                car.park()

                # Simulate car's stay time
                # TODO: get distribution of parking duration from data
                park_du = np.random.normal(3600, 60)  
                yield self.env.timeout(park_du)

                car.leave(self.env.now)
                car_id += 1



