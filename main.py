import agentpy as ap
import random
import math


class TrashTruck(ap.Agent):
    def setup(self):
        self.position = self.random_position()
        self.load = 0
        self.isActive = False
        self.max_load = self.model.p["truck_capacity"]
        self.target_bin = None

    def random_position(self):
        size_x, size_y = self.model.p["grid_size"]
        return (random.randint(0, size_x - 1), random.randint(0, size_y - 1))

    def move_toward(self, target_pos):
        # Move one unit toward target
        x, y = self.position
        tx, ty = target_pos
        dx = 1 if tx > x else -1 if tx < x else 0
        dy = 1 if ty > y else -1 if ty < y else 0
        self.position = (x + dx, y + dy)

    def at_position(self, pos):
        return self.position == pos

    def distance_to(self, pos):
        return math.dist(self.position, pos)


class TrashBin(ap.Agent):
    def setup(self):
        self.position = self.random_position()
        self.status = 0  # 0 = empty, 1 = full
        self.max_trash = self.model.p["bin_capacity"]
        self.assigned = False  # if a truck is already coming

    def random_position(self):
        size_x, size_y = self.model.p["grid_size"]
        return (random.randint(0, size_x - 1), random.randint(0, size_y - 1))


class CommunicationModel(ap.Model):
    def setup(self):
        self.trucks = ap.AgentList(self, self.p["trucks"], TrashTruck)
        self.bins = ap.AgentList(self, self.p["bins"], TrashBin)
        self.agents = self.trucks + self.bins

    def step(self):
        # Randomly fill some bins to simulate trash accumulation
        for bin in self.bins:
            if bin.status == 0 and random.random() < 0.1:
                bin.status = 1
                bin.assigned = False

        # Contract negotiation
        for bin in self.bins:
            if bin.status == 1 and not bin.assigned:
                # Find eligible trucks
                eligible_trucks = [
                    t for t in self.trucks
                    if (t.max_load - t.load) >= bin.max_trash and not t.isActive
                ]
                if not eligible_trucks:
                    continue

                # Sort by distance, then by load
                eligible_trucks.sort(
                    key=lambda t: (t.distance_to(bin.position), t.load)
                )
                selected_truck = eligible_trucks[0]
                selected_truck.target_bin = bin
                selected_truck.isActive = True
                bin.assigned = True

        # Truck actions
        for truck in self.trucks:
            if truck.isActive and truck.target_bin:
                bin = truck.target_bin

                # Move toward bin
                if not truck.at_position(bin.position):
                    truck.move_toward(bin.position)
                else:
                    # Empty the bin
                    truck.load += bin.max_trash
                    bin.status = 0
                    bin.assigned = False
                    truck.isActive = False
                    truck.target_bin = None

    def update(self):
        pass

    def end(self):
        print("Simulation ended.")
        for truck in self.trucks:
            print(f"Truck at {truck.position} has load {truck.load}")


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


if __name__ == "__main__":
    main()
