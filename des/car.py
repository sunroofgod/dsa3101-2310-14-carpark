class Car:

    def __init__(self, id : int, type="hourly"):
        self.id = id
        self.type = type.lower()

    def arrive(self, time : float):
        print(f"Car {self.id} arrives at {time:.2f}s")

    def park(self):
        colour = "white"
        if self.type == "staff":
            colour = "red"
        print(f"Car parks at {colour} lot")

    def leave(self, time : float):
        print(f"Car {self.id} left at {time:.2f}s")