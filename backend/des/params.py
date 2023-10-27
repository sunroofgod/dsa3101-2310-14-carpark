import pandas as pd

def get_carpark_capacity(fpath="../../data/CP Lots NUS.xlsx"):
    d = {}
    data = pd.read_excel(fpath)
    data = data[["CP", "White", "Red"]].to_dict(orient="list")

    for i in range(len(data["CP"])):
        cp = f"cp{data['CP'][i]}"
        d[cp] = (data["White"][i], data["Red"][i])
    
    return d
        
