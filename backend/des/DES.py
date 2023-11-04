import numpy as np
import simpy
from simpy import Environment
from carpark import CarPark
from car import Car
import time
import params

## time unit : minutes

def get_lambda(month : int, hour : int):
    """
    Get the number of arrivals lambda for a given month and hour from LAMBDAS.

    Args:
        month (int): The month (1-12).
        hour (int): The hour of the day (0-23).

    Returns:
        float: The number of arrivala (lambda).
    """
    return params.LAMBDAS[(month, hour)]

def arrivals_to_rate(arrivals : int):
    """
    Convert the number of arrivals to an arrival rate and return the result.

    Args:
        arrivals (int): The number of arrivals in a given time period.

    Returns:
        float: The calculated arrival rate per hour.
    """
    return 1 / (arrivals / 60)

def get_arrival_interval(month : int, minutes : int):
    """
    Calculate and return the time interval between arrivals based on a Poisson process.

    Args:
        month (int): The month (1-12).
        minutes (int): The time in minutes.

    Returns:
        float: The calculated time interval between arrivals (in minutes).
    """
    return arrivals_to_rate(np.random.poisson(get_lambda(month, params.minutes_to_hours(minutes))))

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

# def car_arrival(env, id, type):
#     time = np.random.exponential(ARRIVAL_RATE) # time before next car arrive
#     yield env.timeout(time)
#     car = Car(id, type)
#     return car

## Generate entire process of 1 car
def car_generator(env : simpy.Environment, carparks : list, cp_prob_dict : dict, car_dict : dict, month=params.MONTH):
    """
    Generate the entire process of car arrivals and parking.

    Args:
        env (simpy.Environment): The SimPy environment in which the simulation runs.
        carparks (list): A list of car parks available for parking.
        cp_prob_dict (dict): A dictionary specifying the probability of choosing each car park.
        car_dict (dict): A dictionary specifying the probability of parking types.
        month (int, optional): The current month for the simulation. Default is MONTH.
    Yields:
        SimPy events: Yields events representing car arrivals, parking, and departures.

    Note:
    - This function is intended for use with the SimPy library to create a car parking simulation.
    - The function continuously generates car arrivals and assigns them to car parks.
    - The simulation stops when the environment's time exceeds the specified simulation time.

    Example Usage:
    ```
    sim_env = simpy.Environment()
    car_parks = create_carparks()
    car_probabilities = get_car_probabilities()
    month = 5  # Example month
    car_generator(sim_env, car_parks, car_probabilities, car_probabilities, month=month)
    sim_env.run(until=SIMULATION_TIME)
    ```
    """
    car_id = 1

    ## Make corresponding list pair for choosing type
    car_types = list(car_dict.keys())
    car_prob = list(car_dict.values())
    
    while True:

        ## Choose parking type
        tpe = custom_choice(car_types, car_prob)
        
        ## Car arrive at campus
        car = Car(car_id, tpe)
        time = get_arrival_interval(month, env.now) # time before next car arrive
        assert time >= 0
        yield env.timeout(time)
        # car = car_arrival(env, car_id, tpe)

        ## Choose carpark
        cp_dict = cp_prob_dict[tpe]
        cp_prob = [cp_dict[cp.get_name()] for cp in carparks]
        assert sum(cp_prob) == 1.0

        ## TODO: car should only be able to choose from cp with given parking type
        
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
    """
    Merge two dictionaries of statistical values and calculate the average if keys are common.

    This function takes two dictionaries of statistical values and merges them into a single dictionary.
    If a key is common in both dictionaries, it calculates the average of the corresponding values.

    Parameters:
    - dict1 (dict): The first dictionary of statistical values.
    - dict2 (dict): The second dictionary of statistical values.

    Returns:
    - dict: A merged dictionary with the keys from both input dictionaries, and the average values for common keys.
    """
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
    """
    Print statistics stored in a dictionary.

    This function prints statistics stored in a dictionary, where each key represents a category,
    and the corresponding value is a list of statistical values. It prints each category and its values.

    Args:
        d (dict): A dictionary of statistics, where keys represent categories and values are lists of statistical values.

    Returns:
        None
    """
    for cp, stat in d.items():
        print(f"{cp:<5}: {stat}")
    return

def sim(cap=params.CP_CAPACITY, cp_prob=params.CP_PROB, car_prob=params.CAR_PROB, t=params.SIM_TIME):
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

def run_nsim(n=100, cap=params.CP_CAPACITY, cp_prob=params.CP_PROB, car_prob=params.CAR_PROB, t=params.SIM_TIME, overall_stats={}):
    init_time = time.time()

    ## Run simulation for n times
    for i in range(n):
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
    return overall_stats

if __name__ == "__main__":
    overall_stats = run_nsim()