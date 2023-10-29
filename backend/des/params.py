import pandas as pd
import matplotlib.pyplot as plt

CAP_FPATH = "../../data/CP Lots NUS.xlsx"
DATA_FPATH = "../../data/Cleaned/all_carparks_cleaned.csv"

capacity_data = pd.read_excel(CAP_FPATH)
cp_data = pd.read_csv(DATA_FPATH, low_memory=False)

## TODO: filter based on carparks with non-0 capacity

def get_carpark_capacity(data=capacity_data):
    d = {}
    data = data[["CP", "White", "Red"]].to_dict(orient="list")

    for i in range(len(data["CP"])):
        cp = f"cp{data['CP'][i]}"
        d[cp] = (data["White"][i], data["Red"][i])
    
    return d

def get_carpark_prob(data=cp_data):
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
    ## Calculate proportion of parking types
    users = data.groupby("type").agg({"IU" : 'count'})
    users["total"] = users["IU"].sum()
    users["prop"] = users["IU"] / users["total"]

    users = users.drop(["IU", "total"], axis=1).to_dict()
    users = users["prop"]

    return users

def get_lambda(data=cp_data):
    data['enter_dt'] = pd.to_datetime(data['enter_dt'])
    data['enter_hour'] = data['enter_dt'].dt.hour
    data['month'] = data['enter_dt'].dt.month
    data['year'] = data['enter_dt'].dt.year

    users = data[["month", "year", "enter_hour"]]
    users = users.groupby(["month", "year", "enter_hour"]).size().reset_index()
    users = users.groupby(["month", "enter_hour"]).agg({0 : 'mean'})
    return users.to_dict()[0]

def get_parking_duration_stats(data=cp_data):
    du = data.groupby(['carpark', 'type']).agg({'parked_min' : ['median', 'std']})
    du = du.fillna(0)
    du.index = du.index.set_levels([level.str.lower() for level in du.index.levels])
    du = du.to_dict()
    du_median = du[('parked_min', 'median')]
    du_std = du[('parked_min', 'std')] 
    du = {key : (du_median[key], du_std[key]) for key in du_median.keys()}
    return du