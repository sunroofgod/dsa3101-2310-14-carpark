import numpy as np
import simpy
from simpy import Environment
from carpark import CarPark
from car import Car
import time
import params

## time unit : minutes

## TODO: take input from user / database
SIM_TIME = 24 * 60 # in minutes
ARRIVAL_RATE = 1 # n : 1 car every n minute
NSIM = 10

CP_CAPACITY = params.get_carpark_capacity()
CP_PROB = {
    # carpark name : probablity 
    'cp3' : 0.2, 
    'cp3a' : 0.2, 
    'cp4' : 0.05, 
    'cp5b' : 0.1, 
    'cp6b' : 0.15, 
    'cp10' : 0.3
}

CAR_PROB = {
    # parking type : probablity 
    'hourly' : 0.35, 
    'student' : 0.1, 
    'staff' : 0.5, 
    'esp' : 0.05
}

def custom_choice(items : list, prob : list):
    """
    Choose an item from a list based on specified probabilities.

    Args:
        items (list): List of items to choose from.
        prob (list): List of probabilities corresponding to each item.

    Returns:
        Any: The selected item based on the specified probabilities.
    """
    rng = np.random.default_rng()
    return rng.choice(items, p=prob)

def create_cp(env : simpy.Environment, cp_dict : dict):
    """
    Create a list of car parks based on provided parameters.

    Args:
        env (simpy.Environment): The SimPy environment in which the simulation runs.
        cp_dict (dict): A dictionary containing car park names and white/red lots.

    Returns:
        list: A list of CarPark instances created with the specified parameters.
    """
    carparks = []
    for name, lots in cp_dict.items():
        carparks.append(CarPark(name=name, whiteLots=lots[0], redLots=lots[1], env=env))
    return carparks

def car_arrival(env, id, type):
    time = np.random.exponential(ARRIVAL_RATE) # time before next car arrive
    yield env.timeout(time)
    car = Car(id, type)
    return car

## Generate entire process of 1 car
def car_generator(env : simpy.Environment, carparks : list, cp_prob_dict : dict, car_dict : dict):
    """
    Generate the entire process of car arrivals and parking.

    Args:
        env (simpy.Environment): The SimPy environment in which the simulation runs.
        carparks (list): A list of car parks available for parking.
        cp_prob_dict (dict): A dictionary specifying the probability of choosing each car park.
        car_dict (dict): A dictionary specifying the probability of parking types.

    Yields:
        SimPy events: Yields events representing car arrivals, parking, and departures.
    """
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
        assert time >= 0
        yield env.timeout(time)
        # car = car_arrival(env, car_id, tpe)

        ## Choose carpark
        cp = custom_choice(carparks, cp_prob)
        print(f"{env.now:<7.2f}: Car {car_id} arrived at {cp.get_name()}")

        ## Sim Process: park and leave when done
        env.process(cp.park_car(car))
        
        ## Next car
        car_id += 1

def stats_summary(carparks : list):
    """
    Generate summary statistics for a list of car parks.

    Args:
        carparks (list): A list of CarPark instances to collect statistics from.

    Returns:
        dict: A dictionary containing summary statistics for each car park.
    """
    d = {}
    for cp in carparks:
        d[cp.get_name()] = cp.stats()

    # for cp, stat in d.items():
    #     print(f"{cp:<5}: {stat}")
    return d

def stats_mean(dict1 : dict, dict2 : dict):
    if dict1 == {}:
        return dict2
    if dict2 == {}:
        return dict1
    
    ## merge dict2 into dict1
    for key, val in dict2.items():
        
        if key not in dict1.keys():
            ## no need to average, just take the value from dict2
            dict1[key] = val
        else:
            for i in range(len(val)):
                dict1[key][i] = (dict1[key][i] + dict2[key][i]) / 2
    
    return dict1

def print_stats(d : dict):
    for cp, stat in d.items():
        print(f"{cp:<5}: {stat}")
    return

def sim(cap=CP_CAPACITY, cp_prob=CP_PROB, car_prob=CAR_PROB, t=SIM_TIME):
    """
    Run a car park simulation.

    Args:
        cap (dict): A dictionary specifying car park capacities.
        cp_prob (dict): A dictionary specifying car park choice probabilities.
        car_prob (dict): A dictionary specifying car type probabilities.
        t (int): The simulation time in minutes.

    Returns:
        dict: A dictionary containing summary statistics for each car park.
    """

    ## init Environment
    campus = Environment()

    ## Start process
    carparks = create_cp(campus, cap)
    campus.process(car_generator(campus, carparks, cp_prob, car_prob))

    ## End
    campus.run(until=t)

    ## Output
    stats = stats_summary(carparks)
    return stats

if __name__ == "__main__":
    
    init_time = time.time()
    overall_stats = {}
    
    ## Run simulation for n times
    for i in range(NSIM):
        ## Track simulation time
        start = time.time() 

        ## Run simulation
        stats = sim()

        ## Simulation output
        overall_stats = stats_mean(overall_stats, stats)
        print_stats(stats)
        print(f"--- Simulation {i + 1} completed in {time.time() - start:.2f} seconds ---\n")

    duration = (time.time() - init_time) / 60 # convert to minutes
    print_stats(overall_stats)
    print(f"--- Total running time {duration:.2f} minutes ---")