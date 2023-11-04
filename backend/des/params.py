import pandas as pd
import datetime

CAP_FPATH = "../../data/CP Lots NUS.xlsx"
DATA_FPATH = "../../data/Cleaned/all_carparks_cleaned.csv"

capacity_data = pd.read_excel(CAP_FPATH)
cp_data = pd.read_csv(DATA_FPATH, low_memory=False)

## TODO: filter based on carparks with non-0 capacity

def get_month_arrival_rate(month : int):
    """
    Get the arrival rate for each hour of a given month.

    Args:
        month (int): The month (1-12).

    Returns:
        dict: A dictionary where key is hour (0-23) and values are the mean arrivals for each corresponding time interval.
    """
    return {h : val for (m, h), val in get_arrival_rates().items() if m == month}

def get_day_arrival_rate(day : str, data=cp_data):
    """
    Get the arrival rate for each hour of a given day.

    Args:
        day (str): The date in YYYY-MM-DD format.

    Returns:
        dict: A dictionary where key is hour (0-23) and values are the mean arrivals for each corresponding time interval.
    """
    day = pd.to_datetime(day)
    data['enter_dt'] = pd.to_datetime(data['enter_dt'])
    filtered_data = data[data['enter_dt'].dt.date == day.date()]
    filtered_data['enter_hour'] = filtered_data['enter_dt'].dt.hour
    filtered_data['year'] = filtered_data['enter_dt'].dt.year

    users = filtered_data[["year", "enter_hour"]]
    users = users.groupby(["year", "enter_hour"]).size().reset_index()
    users = users.groupby(["enter_hour"]).agg({0 : 'mean'})
    return users.to_dict()[0]


def minutes_to_hours(minutes : int):
    """
    Convert minutes to hours and return the result.

    Args:
        minutes (int): The number of minutes to convert to hours.

    Returns:
        int: The equivalent number of hours.
    """
    return int(minutes / 60)

def get_carpark_capacity(data=capacity_data):
    """
    Get the car park capacity (number of white and red lots) for each car park.

    Args:
        data: Pandas DataFrame with columns 'CP' (car park identifier), 'White' (number of white lots), and 'Red' (number of red lots).

    Returns:
        dict: A dictionary where keys are car park names (in lowercase), and values are tuples containing the number of white and red lots.
    """
    d = {}
    data = data[["CP", "White", "Red"]].to_dict(orient="list")

    for i in range(len(data["CP"])):
        cp = f"cp{data['CP'][i]}"
        d[cp] = (data["White"][i], data["Red"][i])
    
    return d

def get_carpark_prob(data=cp_data):
    """
    Get the probability of car park utilization by user type for each car park.

    Args:
        data: Pandas DataFrame with columns 'carpark' (car park name), 'type' (user type), and 'IU' (count of users).

    Returns:
        dict: A nested dictionary with user types as the first level keys and car park names (in lowercase) as the second level keys.
             The values are the probabilities of car park utilization by that user type for the corresponding car park.
    """
    d = {}

    ## Calculate proportion of user type for each carpark
    cap = data.groupby(["carpark", "type"])["IU"].count().reset_index()
    cap["total"] = cap.groupby("type")['IU'].transform('sum')
    cap["prop"] = cap["IU"] / cap["total"]
    cap = cap.drop(["IU", "total"], axis=1)
    # cap.groupby("type")['prop'].sum()
    cap = cap.set_index(["carpark", "type"]).to_dict() 
    cap = cap["prop"]

    for key, val in cap.items():
        cp = key[0].lower()
        tpe = key[1].lower()
        # print(cp, tpe, val)

        ## Insert type as key
        if tpe not in d.keys():
            d[tpe] = {}

        ## Create nested dict {type : {cp : prob}}        
        d[tpe][cp] = val
        
    return d

def get_parking_type_prop(data=cp_data):
    """
    Get the proportion of each parking type in the dataset.

    Args:
        data: Pandas DataFrame with a 'type' column representing the parking type.

    Returns:
        dict: A dictionary where keys are parking types, and values are the proportions of each type in the dataset.
    """
    ## Calculate proportion of parking types
    users = data.groupby("type").agg({"IU" : 'count'})
    users["total"] = users["IU"].sum()
    users["prop"] = users["IU"] / users["total"]

    users = users.drop(["IU", "total"], axis=1).to_dict()
    users = users["prop"]

    return users

def get_arrival_rates(data=cp_data):
    """
    Calculate the mean arrival (lambda) of users for each month and hour.

    Args:
        data: Pandas DataFrame with 'enter_dt' column for entry date-time.

    Returns:
        dict: A dictionary where keys are tuples of (month, hour) and values are the mean arrivals for each corresponding time interval.
    """
    data['enter_dt'] = pd.to_datetime(data['enter_dt'])
    data['enter_hour'] = data['enter_dt'].dt.hour
    data['month'] = data['enter_dt'].dt.month
    data['year'] = data['enter_dt'].dt.year

    users = data[["month", "year", "enter_hour"]]
    users = users.groupby(["month", "year", "enter_hour"]).size().reset_index()
    users = users.groupby(["month", "enter_hour"]).agg({0 : 'mean'})
    return users.to_dict()[0]

def get_parking_duration_stats(data=cp_data):
    """
    Get parking duration statistics (median and standard deviation) for each car park and user type.

    Args:
        data: Pandas DataFrame with columns 'carpark' (car park name), 'type' (user type), and 'parked_min' (parking duration in minutes).

    Returns:
        dict: A dictionary where keys are tuples of (car park name, user type), and values are tuples containing the median and standard deviation of parking durations.
    """
    data['enter_dt'] = pd.to_datetime(data['enter_dt'])
    data['hour'] = data['enter_dt'].dt.hour

    unique_carparks = data[['carpark']].drop_duplicates()
    unique_types = data[['type']].drop_duplicates()
    unique_hours = pd.DataFrame({'hour':range(24)})

    unique_df = unique_carparks.merge(unique_types, how="cross").merge(unique_hours, how="cross")

    data = data.merge(unique_df, how="right")
    du = data.groupby(['carpark', 'type', 'hour']).agg({'parked_min' : ['median', 'std']})

    du = du.ffill()
    du = du.bfill()

    du.index = du.index.set_levels([du.index.levels[0].str.lower(), du.index.levels[1].str.lower(), du.index.levels[2]])
    du = du.to_dict()
    du_median = du[('parked_min', 'median')]
    du_std = du[('parked_min', 'std')] 
    du = {key : (du_median[key], du_std[key]) for key in du_median.keys()}
    return du

## TODO: take input from user / database
SIM_TIME = 24 * 60 # in minutes
NSIM = 1
CP_CAPACITY = get_carpark_capacity()
CP_PROB = get_carpark_prob()
CAR_PROB = get_parking_type_prop()
LAMBDAS = get_arrival_rates()
MONTH = datetime.date.today().month
