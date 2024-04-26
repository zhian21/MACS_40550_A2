import random
from mesa import Agent

class PDAgent(Agent):
    def __init__(self, unique_id, model, initial_cooperate_prob=0.5, strategy=None):
        """
        Create a new Prisoner's Dilemma agent.

        Parameters:
        unique_id (int): The unique identifier for this agent.
        model (Model): The model instance that the agent is part of.
        strategy (str, optional): The strategy the agent will employ. Defaults to None.
        """
        super().__init__(unique_id, model)
        self.strategy = strategy
        self.move = "C" if random.random() < initial_cooperate_prob else "D" 
        self.score = 0

    def step(self):
        """
        A single step of the agent.
        """
        if self.strategy == "Majority Rule":
            self.apply_majority_rule()
        elif self.strategy == "Best Neighbor":
            self.apply_best_neighbor_strategy()
        elif self.strategy == "Random":
            self.copy_random_neighbor()
        self.calculate_payoff()    

    def apply_majority_rule(self):
        """
        apply the majority rule strategy where the agent adopts the move (either 'C' or 'D')
        that is most common among its immediate neighbors. In case of a tie, choose randomly.
        """
        neighbor_moves = [neighbor.move for neighbor in self.model.grid.get_neighbors(self.pos, moore=True)]
        if neighbor_moves.count("C") > neighbor_moves.count("D"):
            self.move = "C"
        elif neighbor_moves.count("C") < neighbor_moves.count("D"):
            self.move = "D"
        else:
            self.move = random.choice(["C", "D"])

    def apply_best_neighbor_strategy(self):
        """
        apply the best neighbor strategy where the agent mimics the behavior of the neighbor
        with the highest score. If the agent itself has the highest score, it retains its current move.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
        best_neighbor = max(neighbors, key=lambda a: a.score)
        self.move = best_neighbor.move

    def copy_random_neighbor(self):
        """
        apply the random strategy where the agent randomly selects one of its immediate neighbors
        and copies their move.
        """
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True)
        if neighbors:  
            random_neighbor = random.choice(neighbors)
            self.move = random_neighbor.move
        else:
            self.move = random.choice(["C", "D"])     

    def calculate_payoff(self):
        """
        calculate the payoff for the agent based on the moves of its immediate neighbors
        and the defined payoff matrix for the Prisoner's Dilemma.
        """
        
        neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=False)
        payoff_matrix = self.model.payoff_matrix
        self.score += sum(payoff_matrix[(self.move, neighbor.move)] for neighbor in neighbors)
