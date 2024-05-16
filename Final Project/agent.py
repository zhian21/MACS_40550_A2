import random
from mesa import Agent

class ParentAgent(Agent):
    def __init__(self, unique_id, model, education_level, initial_time_investment, strategy=None):
        super().__init__(unique_id, model)
        self.education_level = education_level
        self.strategy = strategy
        self.time_investment = initial_time_investment
        self.child_outcome_score = 0

    def step(self):
        if self.strategy == "Individual Learning":
            self.update_time_investment()
        elif self.strategy == "Copying the highest-scoring neighbor":
            self.copy_highest_scoring_neighbor()
        elif self.strategy == "Copying the most frequently observed strategy":
            self.copy_most_frequent_strategy()
        elif self.strategy == "Copying randomly":
            self.copy_randomly()
        self.calculate_child_outcome_score()
        self.check_and_switch_strategy()

    def copy_highest_scoring_neighbor(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        best_neighbor = max(neighbors, key=lambda a: a.child_outcome_score, default=None)
        if best_neighbor and best_neighbor.child_outcome_score > self.child_outcome_score:
            self.time_investment = best_neighbor.time_investment

    def copy_most_frequent_strategy(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        neighbor_investments = [neighbor.time_investment for neighbor in neighbors if neighbor]
        if neighbor_investments:
            most_frequent_investment = max(set(neighbor_investments), key=neighbor_investments.count)
            self.time_investment = most_frequent_investment

    def copy_randomly(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        if neighbors:
            random_neighbor = random.choice(neighbors)
            self.time_investment = random_neighbor.time_investment

    def update_time_investment(self):
        pass  # Individual learners keep their time investment the same

    def calculate_child_outcome_score(self):
        optimal_time = self.model.optimal_time_investment
        discrepancy = abs(self.time_investment - optimal_time)
        if discrepancy <= 5:
            self.child_outcome_score = 20
        elif discrepancy <= 10:
            self.child_outcome_score = 10
        else:
            self.child_outcome_score = 0

    def check_and_switch_strategy(self):
        optimal_time = self.model.optimal_time_investment
        discrepancy = abs(self.time_investment - optimal_time)
        switch_probability = self.model.switch_probabilities[self.education_level]
        if discrepancy > self.model.discrepancy_thresholds[self.education_level] and random.random() < switch_probability:
            strategy_ratios = getattr(self.model, f"{self.education_level.lower()}_social_strategy_ratios")
            total_ratio = sum(strategy_ratios.values())
            strategy_map = {
                "Copying the highest-scoring neighbor": "highest",
                "Copying the most frequently observed strategy": "most_frequent",
                "Copying randomly": "random"
            }
            choice_weights = [strategy_ratios[strategy_map[strategy]] / total_ratio for strategy in self.model.social_learning_strategies]
            self.strategy = random.choices(list(strategy_map.keys()), weights=choice_weights, k=1)[0]
        print(f"Agent {self.unique_id} switched to strategy {self.strategy}")
