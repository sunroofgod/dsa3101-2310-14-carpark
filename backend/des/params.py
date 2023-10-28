import pandas as pd

CAP_FPATH = "../../data/CP Lots NUS.xlsx"
DATA_FPATH = "../../data/Cleaned/all_carparks_cleaned.csv"

capacity_data = pd.read_excel(CAP_FPATH)
cp_data = pd.read_csv(DATA_FPATH, low_memory=False)

# TODO: filter based on carparks with non-0 capacity

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

data = cp_data
# summary = data.groupby(['carpark', "type"]).agg({'parked_min' : ['sum', 'mean', 'std'], 'IU' : 'count'})
# users = data.groupby(['month', 'enter_hour'])['IU'].count()
# du = data.groupby(['carpark', 'type']).agg({'parked_min' : ['sum', 'mean', 'median', 'std']})
