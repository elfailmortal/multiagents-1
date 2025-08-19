import agentpy as ap
import random
import matplotlib.pyplot as plt
import math


class TrashTruck(ap.Agent):
    def setup(self):
        self.position = self.random_position()
        self.load = 0
        self.bins_picked_up = 0
        self.isActive = False
        self.max_load = self.model.p["truck_capacity"]
        self.target_bin = None

    def random_position(self):
        size_x, size_y = self.model.p["grid_size"]
        return (random.randint(0, size_x - 1), random.randint(0, size_y - 1))

    def move_toward(self, target_pos):
        x, y = self.position
        tx, ty = target_pos
        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0
        self.position = (x + dx, y + dy)

    def at_position(self, target):
        return self.position == target

    def distance_to(self, target):
        return math.dist(self.position, target)


class TrashBin(ap.Agent):
    def setup(self):
        self.position = self.random_position()
        self.status = 0
        self.max_trash = self.model.p["bin_capacity"]
        self.assigned = False

    def random_position(self):
        size_x, size_y = self.model.p["grid_size"]
        return (random.randint(0, size_x - 1), random.randint(0, size_y - 1))


class CommunicationModel(ap.Model):
    def setup(self):
        self.step_count = 0
        self.trucks = ap.AgentList(self, self.p["trucks"], TrashTruck)
        self.bins = ap.AgentList(self, self.p["bins"], TrashBin)
        self.agents = self.trucks + self.bins
        self.log = {"steps" : []}

    def step(self):
        for bin in self.bins:
            if bin.status == 0 and random.random() < 0.1:
                bin.status = 1
                bin.assigned = False

        for bin in self.bins:
            if bin.status == 1 and not bin.assigned:
                eligible_trucks = [
                    t for t in self.trucks if (t.max_load - t.load) >= bin.max_trash and not t.isActive
                ]
                if not eligible_trucks:
                    continue

                eligible_trucks.sort(
                    key=lambda t: (t.distance_to(bin.position), t.load)
                )
                selected_truck = eligible_trucks[0]
                selected_truck.target_bin = bin
                selected_truck.isActive = True
                bin.assigned = True

        for truck in self.trucks:
            if truck.isActive and truck.target_bin:
                bin = truck.target_bin

                if not truck.at_position(bin.position):
                    truck.move_toward(bin.position)
                else:
                    truck.load += bin.max_trash
                    truck.bins_picked_up += 1
                    bin.status = 0
                    bin.assigned = False
                    truck.isActive = False
                    truck.target_bin = None

    def update(self):
        self.step_count += 1
        if self.step_count % 5 == 0 or self.step_count == 1:
            self.plot_state()
        
        step_data = {
            "step": self.step_count,
            "agents": {}
        }

        for i, truck in enumerate(self.trucks):
            step_data["agents"][f"truck_{i}"] = {
                "type": "truck",
                "position": list(truck.position),
                "load": truck.load,
                "isActive": truck.isActive
            }

        for i, bin in enumerate(self.bins):
            step_data["agents"][f"bin_{i}"] = {
                "type": "bin",
                "position": list(bin.position),
                "status": bin.status,
                "assigned": bin.assigned
            }

        self.log["steps"].append(step_data)

    def plot_state(self):
        plt.figure(figsize=(6, 6))
        plt.title(f"Step {self.step_count}")

        for bin in self.bins:
            x, y = bin.position
            color = 'red' if bin.status == 1 else 'green'
            plt.scatter(x, y, c=color, marker='s', s=100, label='Bin' if self.step_count == 1 else "")

        for truck in self.trucks:
            x, y = truck.position
            color = 'yellow' if truck.isActive else 'blue'
            plt.scatter(x, y, c=color, marker='^', s=100, label='Truck' if self.step_count == 1 else "")

        plt.xlim(0, self.p["grid_size"][0])
        plt.ylim(0, self.p["grid_size"][1])
        plt.grid(True)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.show()

    def end(self):
        print("Simulation ended.")
        for truck in self.trucks:
            print(f"Truck at {truck.position} has load {truck.load} and has picked up {truck.bins_picked_up} bins")

def main():
    parameters = {
        "trucks": 5,
        "bins": 10,
        "steps": 100,
        "truck_capacity": 1000,
        "bin_capacity": 100,
        "grid_size": (50, 50),
    }

    model = CommunicationModel(parameters)
    results = model.run()
    print(results)


if __name__ == "__main__":
    main()
