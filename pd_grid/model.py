import mesa
from .agent import PDAgent
from mesa.datacollection import DataCollector

class PdGrid(mesa.Model):
    def __init__(self, initial_cooperate_prob=0.5, 
                 payoff_CC=1, payoff_CD=0, payoff_DC=2, payoff_DD=0,
                 primary_ratio=0.333, primary_strategy="Frequency Dependent Learning",
                 width = 50,
                 height = 50):
        """
        Initializes the Prisoner's Dilemma grid model with specified agent ratios.

        Parameters:
        primary_ratio (float): Determines the ratio of different strategies in the population.
        primary_strategy (str): Can be 'Frequency Dependent Learning', 'Success Base Learning', or 'Random Copying'.
        """    
        super().__init__()
        width = 50
        height = 50
        self.grid = mesa.space.SingleGrid(width, height, torus=True)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.initial_cooperate_prob = initial_cooperate_prob
        self.set_ratios_by_choice(primary_ratio, primary_strategy)

        # Determine the number of agents for each strategy
        num_agents = width * height
        num_frequency_dependent = int(num_agents * self.frequency_dependent_ratio)
        num_success_base = int(num_agents * self.success_base_ratio)
        num_random = num_agents - (num_frequency_dependent + num_success_base)

        # Create and place agents
        agent_id = 0
        for strategy, count in [("Frequency Dependent Learning", num_frequency_dependent),
                                ("Success Base Learning", num_success_base),
                                ("Random Copying", num_random)]:
            for _ in range(count):
                x = self.random.randrange(width)
                y = self.random.randrange(height)

                while not self.grid.is_cell_empty((x, y)):
                    x = self.random.randrange(width)
                    y = self.random.randrange(height)

                agent = PDAgent(agent_id, self, strategy=strategy, 
                                initial_cooperate_prob=self.initial_cooperate_prob)
                self.grid.place_agent(agent, (x, y))
                self.schedule.add(agent)
                agent_id += 1

        self.payoff_matrix = {
            ('C', 'C'): payoff_CC, 
            ('C', 'D'): payoff_CD,  
            ('D', 'C'): payoff_DC, 
            ('D', 'D'): payoff_DD   
        }       

        self.datacollector = DataCollector(
            model_reporters={
                "Frequency Dependent Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Frequency Dependent Learning"]),
                "Success Base Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Success Base Learning"]),
                "Random Copying Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Random Copying"]),
                "Average Score(Frequency Dependent)": lambda m: self.average_score_by_strategy("Frequency Dependent Learning"),
                "Average Score(Success Base)": lambda m: self.average_score_by_strategy("Success Base Learning"),
                "Average Score(Random Copying)": lambda m: self.average_score_by_strategy("Random Copying"),
                "Defecting Agents": lambda m: len([a for a in m.schedule.agents if a.move == "D"]),
                "Cooperating Agents": lambda m: len([a for a in m.schedule.agents if a.move == "C"]),
            }
            )

        self.running = True
        self.datacollector.collect(self)
    
    def random_position(self):
        x = self.random.randrange(self.grid.width)
        y = self.random.randrange(self.grid.height)
        while not self.grid.is_cell_empty((x, y)):
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
        return x, y

    def average_score_by_strategy(self, strategy):
        """
        Calculate and return the average score of agents employing a specific strategy.

        Parameters:
        strategy (str): The strategy to calculate the average score for.

        Returns:
        float: The average score of agents using the specified strategy.
        """
        agents_with_strategy = [
            agent for agent in self.schedule.agents if agent.strategy == strategy]
        if agents_with_strategy:
            total_score = sum(agent.score for agent in agents_with_strategy)
            average_score = total_score / len(agents_with_strategy)
            return average_score
        else:
            return 0

    def set_ratios_by_choice(self, primary_ratio, primary_strategy):
        remaining_ratio = (1 - primary_ratio) / 2
        if primary_strategy == "Frequency Dependent Learning":
            self.frequency_dependent_ratio = primary_ratio
            self.success_base_ratio = remaining_ratio
            self.random_ratio = remaining_ratio
        elif primary_strategy == "Success Base Learning":
            self.success_base_ratio = primary_ratio
            self.frequency_dependent_ratio = remaining_ratio
            self.random_ratio = remaining_ratio
        elif primary_strategy == "Random Copying":
            self.random_ratio = primary_ratio
            self.frequency_dependent_ratio = remaining_ratio
            self.success_base_ratio = remaining_ratio

    def step(self):
        self.schedule.step()  
        self.datacollector.collect(self)

         # Determine if all agents are cooperating or defecting
        cooperating_agents = [agent for agent in self.schedule.agents if agent.move == 'C']
        defecting_agents = [agent for agent in self.schedule.agents if agent.move == 'D']

        # Stop the model if all agents are either cooperating or defecting
        if len(cooperating_agents) == len(self.schedule.agents) or len(defecting_agents) == len(self.schedule.agents):
            self.running = False

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()