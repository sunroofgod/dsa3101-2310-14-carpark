import numpy as np
import pandas as pd
from simpy import Environment
import preprocess
from carpark import CarPark

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


## TODO: Function to get mean parking duration for each type for each cp
def get_mean_duration(data):
    return data.groupby('type')['duration'].mean()

if __name__ == "__main__":

    cp5_df = preprocess.parse_xlsx('./data/raw_Cp5_a.xlsx')
    mean_duration = get_mean_duration(cp5_df)

    esp_mean_du = mean_duration['esp_du']
    hourly_mean_du = mean_duration['hourly_du']
    staff_mean_du = mean_duration['staff_du']
    student_mean_du = mean_duration['student_du']
    
    # Example usage:
    env = Environment()
    park = CarPark("Parking Lot 1", capacity=CAPACITY, env=env)
    env.process(park.car_gen(arrivalRate=60))  # Adjust arrivalRate as needed
    env.run(until=SIM_TIME)  # Adjust the simulation duration as needed
