import numpy as np
class Car:

    def __init__(self, id : int, type="hourly"):
        self.id = id
        self.type = type.lower()

    def name(self):
        return f"Car {self.id}"

    def get_type(self):
        return self.type

    def park(self, cp : str):
        colour = "white"
        if self.type == "staff":
            colour = "red"
        print(f"Car {self.id} parks at {cp} {colour} lot")
        return 

    def leave(self):
        print(f"Car {self.id} leaves")
        return
    
    def park_duration(self):
        return np.random.normal(180, 60)