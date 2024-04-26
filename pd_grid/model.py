import mesa
from .agent import PDAgent
from mesa.datacollection import DataCollector

class PdGrid(mesa.Model):
    def __init__(self, initial_cooperate_prob=0.5,
                 payoff_CC=1, payoff_CD=0, payoff_DC=2, payoff_DD=0,
                 ratio_choice = "equal"):
        """
        Initializes the Prisoner's Dilemma grid model with specified agent ratios.

        Parameters:
        ratio_choice (str): Determines the ratio of different strategies in the population.
                            Can be 'equal', 'more_majority', 'more_best', or 'more_random'.
        """    
        super().__init__()
        width = 50
        height = 50
        self.grid = mesa.space.SingleGrid(width, height, torus=True)
        self.schedule = mesa.time.SimultaneousActivation(self)
        self.initial_cooperate_prob = initial_cooperate_prob
        self.set_ratios_by_choice(ratio_choice)

        #determine the number of agents for each strategy
        num_agents = width * height
        num_majority = int(num_agents * self.majority_ratio)
        num_best_neighbor = int(num_agents * self.best_neighbor_ratio)
        num_random = num_agents - (num_majority + num_best_neighbor)

        # create and place agents
        agent_id = 0
        for strategy, count in [("Majority Rule", num_majority),
                                ("Best Neighbor", num_best_neighbor),
                                ("Random", num_random)]:
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
                "Majority_Rule_Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Majority Rule"]),
                "Best_Neighbor_Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Best Neighbor"]),
                "Random_Agents": lambda m: len([a for a in m.schedule.agents if a.strategy == "Random"]),
                "Average_Score_Majority": lambda m: self.average_score_by_strategy("Majority Rule"),
                "Average_Score_Best_Neighbor": lambda m: self.average_score_by_strategy("Best Neighbor"),
                "Average_Score_Random": lambda m: self.average_score_by_strategy("Random"),
                "Defecting_Agents": lambda m: len([a for a in m.schedule.agents if a.move == "D"]),
                "Cooperating_Agents": lambda m: len([a for a in m.schedule.agents if a.move == "C"]),
            })


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

    def set_ratios_by_choice(self, choice):
        """
        Set the ratios of agents using different strategies based on the given choice.

        Parameters:
        choice (str): The ratio choice that defines the distribution of strategies among agents.
        """
        ratio_options = {
            'equal': (1/3, 1/3, 1/3),
            'more_majority': (0.5, 0.25, 0.25),
            'more_best': (0.25, 0.5, 0.25),
            'more_random': (0.25, 0.25, 0.5)
        }
        ratios = ratio_options.get(choice, ratio_options['equal'])
        self.majority_ratio, self.best_neighbor_ratio, self.random_ratio = ratios

    def step(self):
        self.schedule.step()  
        self.datacollector.collect(self)


        self.datacollector.collect(self)

    def run(self, n):
        """Run the model for n steps."""
        for _ in range(n):
            self.step()