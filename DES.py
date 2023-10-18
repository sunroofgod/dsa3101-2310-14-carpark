import numpy as np
import pandas as pd
import simpy
import preprocess

# cp.process()
# cp.timeout()
# cp.run()
# cp.now

## Resources (such as cp and parking lots)
## Resource() : limit num of processes, need request --> parking lot
## Container() :  discrete/continuous quantities
## Store() : unlimited --> carpark


## TODO: Function to get mean parking duration for each type for each cp
def get_mean_duration(data):
    return data.groupby('type')['duration'].mean()

## generator function
def car_gen(env):
    car_num = 0
    while True:
        car_num += 1

        yield env.timeout(15)
        print(f"Car {car_num}: arrives")

        yield env.timeout(30)
        print(f"Car {car_num}: leaves")

if __name__ == "__main__":

    cp5_df = preprocess.parse_xlsx('./data/raw_Cp5_a.xlsx')
    mean_duration = get_mean_duration(cp5_df)

    esp_mean_du = mean_duration['esp_du']
    hourly_mean_du = mean_duration['hourly_du']
    staff_mean_du = mean_duration['staff_du']
    student_mean_du = mean_duration['student_du']
    
    

    env = simpy.Environment()
    
    env.process(car_gen(env))

    env.run(until=100)
