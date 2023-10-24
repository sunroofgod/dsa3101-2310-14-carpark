import numpy as np
from simpy import Environment
from carpark import CarPark
from car import Car
import time

## time unit : minutes

## TODO: take input from user / database
SIM_TIME = 24 * 60 # in minutes
ARRIVAL_RATE = 60 # n : 1 car every n minute

CP_CAPACITY = {
    'cp3' : (3, 1), 
    # 'cp3a' : (41, 0), 
    # 'cp4' : (95, 0), 
    # 'cp5' : (70, 0), 
    # 'cp5b' : (24, 0), 
    # 'cp6b' : (163, 0), 
    # 'cp10' : (232, 0)
}

CP_PROB = {
    'cp3' : 1 # 0.2, 
    # 'cp3a' : 0.2, 
    # 'cp4' : 0.05, 
    # 'cp5' : 0.05, 
    # 'cp5b' : 0.1, 
    # 'cp6b' : 0.15, 
    # 'cp10' : 0.25
}

CAR_PROB = {
    'hourly' : 0.35, 
    'student' : 0.1, 
    'staff' : 0.5, 
    'esp' : 0.05
}

def custom_choice(items, prob):
    rng = np.random.default_rng()
    return rng.choice(items, p=prob)

def create_cp(env, cp_dict):
    carparks = []
    for name, lots in cp_dict.items():
        carparks.append(CarPark(name=name, whiteLots=lots[0], redLots=lots[1], env=env))
    return carparks

# def car_arrival(env, id, type):
#     time = np.random.exponential(ARRIVAL_RATE) # time before next car arrive
#     yield env.timeout(time)
#     car = Car(id, type)
#     return car

## Generate entire process of 1 car
def car_generator(env, carparks, cp_prob_dict, car_dict):
    car_id = 1
    cp_prob = [cp_prob_dict[cp.get_name()] for cp in carparks]
    assert sum(cp_prob) == 1
    car_types = list(car_dict.keys())
    car_prob = list(car_dict.values())
    
    while True:

        ## Choose parking type
        tpe = custom_choice(car_types, car_prob)
        
        ## Car arrive at campus
        car = Car(car_id, tpe)
        time = np.random.exponential(ARRIVAL_RATE) # time before next car arrive
        yield env.timeout(time)

        # car = car_arrival(env, car_id, tpe)

        ## Choose carpark
        cp = custom_choice(carparks, cp_prob)
        # print(f"Car {car_id} arrived at {cp.get_name()}")

        ## Sim Process: park and leave when done
        env.process(cp.park_car(car))
        
        ## Next car
        car_id += 1

## TODO: implement output 
def stats_summary(carparks):
    d = {}
    for cp in carparks:
        d[cp.get_name()] = cp.stats()
    return d

def sim(cap=CP_CAPACITY, cp_prob=CP_PROB, car_prob=CAR_PROB, t=SIM_TIME):
    start = time.time()

    ## init Environment
    campus = Environment()

    ## Start process
    carparks = create_cp(campus, cap)
    campus.process(car_generator(campus, carparks, cp_prob, car_prob))

    ## End
    campus.run(until=t)
    end = time.time()
    duration = end - start

    ## Output
    print(f"--- Simulation completed in {duration:.2f} seconds ---")
    stats = stats_summary(carparks)
    return stats

if __name__ == "__main__":
    
    ## Run simulation
    stats = sim()
    print(stats)
