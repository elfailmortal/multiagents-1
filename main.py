import agentpy as ap
import matplotlib.pyplot as plt
import random

def main():
    class TrashTruck(ap.Agent):
        def setup(self):
            self.position = (0, 0)
            self.load = 0
            self.isActive = False
            self.max_load = self.model.p["truck_capacity"]

    
    class TrashBin(ap.Agent):
        def setup(self):
            self.position = (0, 0)
            self.isActive = False
            self.status = 0
            self.max_trash = self.model.p["bin_capacity"]


    class CommunicationModel(ap.Model):
        def setup(self):
            num_trucks = self.p["trucks"]
            num_bins = self.p["bins"]
            self.trucks = ap.AgentList(self, num_trucks, TrashTruck)
            self.bins = ap.AgentList(self, num_bins, TrashBin)
            self.agents = self.trucks + self.bins
                
        def step(self):
            #TODO: Update trucks position
            #TODO: Update trash bins status

            pass

        def update(self):
            pass

        def end(self):
            pass


    parameters = {
        "trucks": 5,
        "bins": 10,
        "steps": 100,
        "truck_capacity": 1000,
        "bin_capacity" : 100,
        "grid_size" : (50, 50),
    }

    model = CommunicationModel(parameters)
    results = model.run()


if __name__ == "__main__":
    main()
