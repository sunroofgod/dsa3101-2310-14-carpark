class Car:

    def __init__(self, id : int, type="hourly"):
        self.id = id
        self.type = type.lower()

    def park(self, cp : str):
        colour = "white"
        if self.type == "staff":
            colour = "red"
        print(f"Car {self.id} parks at {cp} {colour} lot")

    def leave(self):
        print(f"Car {self.id} leaves")