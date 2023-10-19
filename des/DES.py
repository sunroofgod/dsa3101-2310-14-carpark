import numpy as np
from simpy import Environment
from carpark import CarPark
from car import Car
import time

# cp.process()
# cp.timeout()
# cp.run()
# cp.now
## Resources (such as cp and parking lots)
## Resource() : limit num of processes, need request --> parking lot
## Container() :  discrete/continuous quantities
## Store() : unlimited --> carpark

## TODO: take input from user / database
# 1h = 3600s
# 1D = 86400s
# 1 week = 604800
SIM_TIME = 86400 # in seconds
ARRIVAL_RATE = 1
cp_info = {'cp3' : 236, 
           'cp3a' : 41, 
           'cp4' : 95, 
           'cp5' : 70, 
           'cp5b' : 24, 
           'cp6b' : 163, 
           'cp10' : 232}
cp_prob = [0.2, 0.2, 0.05, 0.05, 0.1, 0.15, 0.25]
car_types = ['hourly', 'student', 'staff', 'esp']
car_prob = [0.35, 0.1, 0.5, 0.05]

def custom_choice(list, prob):
    rng = np.random.default_rng()
    return rng.choice(list, p=prob)

def car_generator(env, carparks):
    car_id = 1
    while True:
        # Generate parking duration using a Poisson distribution
        park_duration = np.random.poisson(ARRIVAL_RATE)  # Adjust the arrival rate as needed
        yield env.timeout(park_duration)

        # Create a car
        car = Car(id=car_id, type=custom_choice(car_types, car_prob))
        car_id += 1

        # Choose a car park based on predefined probabilities
        cp = custom_choice(carparks, cp_prob)
        env.process(cp.park_car(car))

if __name__ == "__main__":
    start_time = time.time()

    ## init environment 
    campus = Environment()

    ## init carparks
    carparks = []
    for cp_id, capacity in cp_info.items():
        carparks.append(CarPark(id=cp_id, capacity=capacity, env=campus))
    
    ## Start process
    campus.process(car_generator(campus, carparks))
    campus.run(until=SIM_TIME)
    
    end_time = time.time()
    duration = (end_time - start_time) / 60
    print(f"--- Simulation completed in {duration:.2f} minutes ---")

    ## TODO: Summary statistics
    # total cars entered campus
    # total cars left campus
    # average parking duration
