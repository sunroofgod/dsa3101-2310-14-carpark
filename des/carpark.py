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

    # def car_gen(self, arrivalRate):
    #     car_id = 1
    #     while True:
    #         # Generate random arrival time intervals following a Poisson distribution
    #         arrival_time = np.random.poisson(arrivalRate)

    #         yield self.env.timeout(arrival_time)  # Wait for the next car to arrive

    #         car_type = "hourly" if np.random.random() < 0.8 else "staff"  # 80% hourly, 20% staff

    #         with self.spots.request() as request:
    #             yield request  # Request a parking spot

    #             car = Car(car_id, car_type)
    #             print(f"{int(self.env.now)} : {car.arrive()}")
    #             print(f"{car.park()} at {self.id}")

    #             # Simulate car's stay time
    #             # TODO: get distribution of parking duration from data
    #             park_du = np.random.normal(3600, 60)  
    #             yield self.env.timeout(park_du)

    #             print(f"{int(self.env.now)} : {car.leave()} {self.id}")
    #             car_id += 1



