import numpy as np
import pandas as pd
from simpy import Environment
from carpark import CarPark
import time

# cp.process()
# cp.timeout()
# cp.run()
# cp.now
## Resources (such as cp and parking lots)
## Resource() : limit num of processes, need request --> parking lot
## Container() :  discrete/continuous quantities
## Store() : unlimited --> carpark

## TODO: take input from user
# 1h = 3600s
# 1D = 86400s
# 1 week = 604800
SIM_TIME = 86400 # in seconds
CAPACITY = 150 
ARRIVAL_RATE = 60

if __name__ == "__main__":
    start_time = time.time()

    env = Environment()
    cp = CarPark("5", capacity=CAPACITY, env=env)
    env.process(cp.car_gen(arrivalRate=ARRIVAL_RATE))  # Adjust arrivalRate as needed
    env.run(until=SIM_TIME)  # Adjust the simulation duration as needed

    end_time = time.time()
    duration = (end_time - start_time) / 60
    print(f"--- Simulation completed in {duration:.2f} minutes ---")

    ## TODO: Summary statistics
    # total cars entered campus
    # total cars left campus
    # average parking duration
