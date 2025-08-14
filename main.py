import agentpy as ap
import matplotlib.pyplot as plt
import random

def main():
    class Person(ap.Agent):
        def setup(self):
            self.group = self.p.group_1 if self.id % 2 == 0 else self.p.group_2

        def happy(self):
            neighbors = self.model.grid.neighbors(self)
            if not neighbors:
                return True
            same_group = sum(1 for n in neighbors if n.group == self.group)
            return same_group / len(neighbors) >= self.p.homophily

        def step(self):
            if not self.happy():
                empty_cells = self.model.grid.empty
                if empty_cells:
                    new_cell = self.model.random.choice(empty_cells)
                    self.model.grid.move_to(self, new_cell)

    class SegregationModel(ap.Model):
        def setup(self):
            self.grid = ap.Grid(self, [10, 10], track_empty=True)
            self.agents = ap.AgentList(self, 80, Person)
            self.grid.add_agents(self.agents, random=True)

        def step(self):
            self.agents.step()

        def update(self):
            pass

        def end(self):
            # Fix here: get position from grid, not agent
            self.record('positions', [(a.group, self.grid.positions[a]) for a in self.agents])


    parameters = {
        'steps': 10,
        'group_1': 'red',
        'group_2': 'blue',
        'homophily': 0.7,
    }

    model = SegregationModel(parameters)
    results = model.run()

    def plot_grid(model):
        colors = {'red': 'red', 'blue': 'blue'}
        for agent in model.agents:
            x, y = model.grid.positions[agent]
            plt.scatter(x, y, color=colors[agent.group], s=100)
        plt.title("Final Positions of Agents")
        plt.grid(True)
        plt.xticks(range(model.grid.shape[0]))
        plt.yticks(range(model.grid.shape[1]))
        plt.gca().invert_yaxis()
        plt.show()

    plot_grid(model)

if __name__ == "__main__":
    main()
