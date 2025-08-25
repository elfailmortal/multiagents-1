import agentpy as ap
import random
import matplotlib.pyplot as plt
import math
import json


"""
Authors:
- Lucas Mateo Tapia Callisperis
- Emiliano Enríquez López
- Diego Maciel Pliego
- Rafael Cárdenas Meneses
- ChatGPT (Assistant & Debugging/Optimization Support)
"""


class TrashTruck(ap.Agent):
    def setup(self):
        self.position = self.random_free_position()
        self.load = 0
        self.bins_picked_up = 0
        self.isActive = False
        self.max_load = self.model.p["truck_capacity"]
        self.target_bin = None

    def random_free_position(self):
        grid = self.model.p["grid_map"]
        free_cells = [(i, j) for i in range(len(grid))
                      for j in range(len(grid[0])) if grid[i][j] == 0]
        return random.choice(free_cells)

    def move_toward(self, target_pos):
        x, y = self.position
        tx, ty = target_pos

        options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
        options = [(nx,ny) for nx,ny in options if 0<=nx<len(self.model.p["grid_map"]) 
                                            and 0<=ny<len(self.model.p["grid_map"][0])
                                            and self.model.p["grid_map"][nx][ny]==0]
        if not options:
            return  # blocked
        # pick the neighbor closest to target
        options.sort(key=lambda pos: math.dist(pos,target_pos))
        self.position = options[0]


    def at_position(self, target):
        return self.position == target

    def distance_to(self, target):
        return math.dist(self.position, target)


class TrashBin(ap.Agent):
    def setup(self):
        self.position = self.random_free_position()
        self.status = 0
        self.max_trash = self.model.p["bin_capacity"]
        self.assigned = False

    def random_free_position(self):
        grid = self.model.p["grid_map"]
        free_cells = [(i, j) for i in range(len(grid))
                      for j in range(len(grid[0])) if grid[i][j] == 0]
        return random.choice(free_cells)


class CommunicationModel(ap.Model):
    def setup(self):
        self.step_count = 0
        self.trucks = ap.AgentList(self, self.p["trucks"], TrashTruck)
        self.bins = ap.AgentList(self, self.p["bins"], TrashBin)
        self.agents = self.trucks + self.bins
        self.log = {"steps": []}

    def step(self):

        for bin in self.bins:
            if bin.status == 0 and random.random() < 0.5 and not bin.assigned:
                bin.status = 1
                bin.assigned = False

        unassigned_bins = [b for b in self.bins if b.status == 1 and not b.assigned]
        for bin in unassigned_bins:
            eligible_trucks = [
                t for t in self.trucks if (t.max_load - t.load) >= bin.max_trash and not t.isActive
            ]
            if not eligible_trucks:
                continue

            eligible_trucks.sort(key=lambda t: (t.distance_to(bin.position), t.load))

            selected_truck = eligible_trucks[0]
            selected_truck.target_bin = bin
            selected_truck.isActive = True
            bin.assigned = True

        for truck in self.trucks:
            if truck.target_bin is None or not truck.isActive:
                unassigned_bins = [b for b in self.bins if b.status == 1 and not b.assigned]
                if unassigned_bins:
                    unassigned_bins.sort(key=lambda b: truck.distance_to(b.position))
                    target = unassigned_bins[0]
                    truck.target_bin = target
                    truck.isActive = True
                    target.assigned = True

            if truck.isActive and truck.target_bin:
                if not truck.at_position(truck.target_bin.position):
                    truck.move_toward(truck.target_bin.position)
                else:
                    truck.load += truck.target_bin.max_trash
                    truck.bins_picked_up += 1
                    truck.target_bin.status = 0
                    truck.target_bin.assigned = False
                    truck.isActive = False
                    truck.target_bin = None

    def update(self):
        self.step_count += 1
        if self.step_count % 5 == 0 or self.step_count == 1:
            self.plot_state()

        step_data = {"step": self.step_count, "agents": {}}

        for i, truck in enumerate(self.trucks):
            step_data["agents"][f"truck_{i}"] = {
                "type": "truck",
                "position": list(truck.position),
                "load": truck.load,
                "isActive": truck.isActive,
            }

        for i, bin in enumerate(self.bins):
            step_data["agents"][f"bin_{i}"] = {
                "type": "bin",
                "position": list(bin.position),
                "status": bin.status,
                "assigned": bin.assigned,
            }

        self.log["steps"].append(step_data)

    def get_grid_state(self):
        """Return a grid with trucks (2) and bins (3) marked on it."""
        base = [row[:] for row in self.p["grid_map"]]

        for bin in self.bins:
            x, y = bin.position
            if bin.status == 1:
                base[x][y] = 3

        for truck in self.trucks:
            x, y = truck.position
            base[x][y] = 2

        return base
    
    def print_grid(self):
        display_grid = [row[:] for row in self.model.p["grid_map"]]

        for bin in self.bins:
            x, y = bin.position
            display_grid[x][y] = 3

        for truck in self.trucks:
            x, y = truck.position
            display_grid[x][y] = 2

        for row in display_grid:
            print(" ".join(str(cell) for cell in row))
        print("\n" + "-"*40 + "\n")

    def plot_state(self):
        plt.figure(figsize=(6, 6))
        plt.title(f"Step {self.step_count}")

        grid = self.get_grid_state()
        colors = {0: "white", 1: "black", 2: "blue", 3: "red"}

        for i in range(len(grid)):
            for j in range(len(grid[0])):
                val = grid[i][j]
                plt.scatter(j, i, c=colors[val], marker="s", s=100)

        plt.xlim(-1, len(grid[0]))
        plt.ylim(-1, len(grid))
        plt.gca().invert_yaxis()
        plt.grid(True)
        plt.show()


    def end(self):
        print("Simulation ended.")
        for truck in self.trucks:
            print(
                f"Truck at {truck.position} has load {truck.load} and has picked up {truck.bins_picked_up} bins"
            )

def save_log_to_json(model, filename="simulation_log.json"):
    """
    Save the simulation log (all steps) to a JSON file.
    """
    # Build a structured JSON
    output = {
        "parameters": model.p,
        "steps": model.log["steps"]
    }

    # Save to file
    with open(filename, "w") as f:
        json.dump(output, f, indent=4)

def main():
    parameters = {
        "trucks": 5,
        "bins": 10,
        "steps": 100,
        "truck_capacity": 1000,
        "bin_capacity": 100,
        "grid_map": [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
    }

    model = CommunicationModel(parameters)
    results = model.run()
    save_log_to_json(model, "simulation_log.json")
    print(results)


if __name__ == "__main__":
    main()
