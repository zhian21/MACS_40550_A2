import logging
import networkx as nx
import mesa
from mesa.datacollection import DataCollector
from .agent import ParentAgent
import random


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ParentalLearningModel(mesa.Model):
    def __init__(self, initial_density=0.8, width=50, height=50,  # Include initial_density
                 optimal_time_investment=40,
                 primary_edu_ratio=0.33, primary_edu_level="High",
                 high_individual_learning_ratio=0.7, medium_individual_learning_ratio=0.7, low_individual_learning_ratio=0.7,
                 high_primary_social_ratio=0.5, medium_primary_social_ratio=0.5, low_primary_social_ratio=0.5,
                 high_primary_social_strategy="Copying the highest-scoring neighbor",
                 medium_primary_social_strategy="Copying the highest-scoring neighbor",
                 low_primary_social_strategy="Copying the highest-scoring neighbor",
                 avg_degree_high=4, rewiring_prob_high=0.1,
                 avg_degree_medium=6, rewiring_prob_medium=0.3,
                 avg_degree_low=8, rewiring_prob_low=0.5,
                 initial_time_investment=30,
                 high_discrepancy_threshold=5, medium_discrepancy_threshold=10, low_discrepancy_threshold=15,
                 high_switch_probability=0.1, medium_switch_probability=0.3, low_switch_probability=0.5,
                 max_attempts=2000):
        super().__init__()
        logger.debug("Initializing the model...")

        self.width = width
        self.height = height
        self.max_attempts = max_attempts

        # Calculate the total number of nodes
        total_nodes = width * height
        logger.debug(f"Total nodes: {total_nodes}")

        # Calculate the number of agents based on initial_density
        num_agents = int(total_nodes * initial_density)
        logger.debug(f"Initial density: {initial_density}")
        logger.debug(f"Number of agents: {num_agents}")

        # Ensure num_agents does not exceed total_nodes
        if num_agents > total_nodes:
            num_agents = total_nodes
            logger.warning(f"Adjusted number of agents to fit available nodes: {num_agents}")

        # Initialize individual learning ratios
        self.high_individual_learning_ratio = high_individual_learning_ratio
        self.medium_individual_learning_ratio = medium_individual_learning_ratio
        self.low_individual_learning_ratio = low_individual_learning_ratio

        # Calculate the number of agents for each education level
        self.set_education_ratios(primary_edu_ratio, primary_edu_level)
        num_high_edu = int(num_agents * self.high_edu_ratio)
        num_medium_edu = int(num_agents * self.medium_edu_ratio)
        num_low_edu = int(num_agents * self.low_edu_ratio)
        logger.debug(f"High education agents: {num_high_edu}, Medium education agents: {num_medium_edu}, Low education agents: {num_low_edu}")

        # Create separate network graphs for different education levels with varying parameters
        high_network = nx.watts_strogatz_graph(num_high_edu, avg_degree_high, rewiring_prob_high)
        medium_network = nx.watts_strogatz_graph(num_medium_edu, avg_degree_medium, rewiring_prob_medium)
        low_network = nx.watts_strogatz_graph(num_low_edu, avg_degree_low, rewiring_prob_low)

        # Combine the networks
        combined_network = nx.union(high_network, medium_network, rename=('high-', 'medium-'))
        combined_network = nx.union(combined_network, low_network, rename=('', 'low-'))

        self.grid = mesa.space.NetworkGrid(combined_network)
        self.G = combined_network  # Assign the combined network to self.G
        logger.debug("Network grid initialized.")

        self.schedule = mesa.time.RandomActivation(self)
        self.optimal_time_investment = optimal_time_investment

        self.set_social_learning_ratios("High", high_individual_learning_ratio, high_primary_social_ratio, high_primary_social_strategy)
        self.set_social_learning_ratios("Medium", medium_individual_learning_ratio, medium_primary_social_ratio, medium_primary_social_strategy)
        self.set_social_learning_ratios("Low", low_individual_learning_ratio, low_primary_social_ratio, low_primary_social_strategy)

        # Verify that there are enough nodes to place agents
        empty_nodes = list(self.grid.G.nodes())
        random.shuffle(empty_nodes)
        logger.debug(f"Number of nodes: {len(empty_nodes)}")

        agent_id = 0

        for education_level, count in [("High", num_high_edu), 
                                       ("Medium", num_medium_edu), 
                                       ("Low", num_low_edu)]:
            logger.debug(f"Placing agents for {education_level} education level...")
            for _ in range(count):
                logger.debug(f"Placing agent {agent_id}...")
                attempts = 0
                while attempts < self.max_attempts:
                    if not empty_nodes:
                        logger.error(f"Ran out of nodes while placing agent {agent_id}.")
                        raise RuntimeError(f"Ran out of nodes while placing agent {agent_id}.")
                    
                    node = empty_nodes.pop()
                    if not self.grid.is_cell_empty(node):
                        attempts += 1
                        continue

                    logger.debug(f"Node {node} is empty, placing agent...")
                    individual_learning_ratio = getattr(self, f"{education_level.lower()}_individual_learning_ratio")
                    if random.random() < individual_learning_ratio:
                        strategy = "Individual Learning"
                    else:
                        strategy_weights = getattr(self, f"{education_level.lower()}_social_strategy_ratios")
                        strategy = random.choices(
                            ["Copying the highest-scoring neighbor", "Copying the most frequently observed strategy", "Copying randomly"], 
                            weights=[strategy_weights['highest'], strategy_weights['most_frequent'], strategy_weights['random']], k=1
                        )[0]
                    agent = ParentAgent(agent_id, self, education_level, initial_time_investment, strategy=strategy)
                    self.grid.place_agent(agent, node)
                    self.schedule.add(agent)
                    logger.debug(f"Agent {agent_id} placed at node {node} with strategy {strategy}.")
                    break
                else:
                    logger.error(f"Could not place agent {agent_id} after {self.max_attempts} attempts.")
                    raise RuntimeError(f"Could not place agent {agent_id} after {self.max_attempts} attempts.")

        logger.debug("Agents initialized.")

        self.datacollector = DataCollector(
            model_reporters={
                "Average Time Investment (High)": lambda m: self.average_time_investment("High"),
                "Average Time Investment (Medium)": lambda m: self.average_time_investment("Medium"),
                "Average Time Investment (Low)": lambda m: self.average_time_investment("Low"),
                "Average Child Outcome Score (High)": lambda m: self.average_child_outcome_score("High"),
                "Average Child Outcome Score (Medium)": lambda m: self.average_child_outcome_score("Medium"),
                "Average Child Outcome Score (Low)": lambda m: self.average_child_outcome_score("Low")
            },
            agent_reporters={"Strategy": "strategy", "Time Investment": "time_investment"}
        )

        self.discrepancy_thresholds = {"High": high_discrepancy_threshold, "Medium": medium_discrepancy_threshold, "Low": low_discrepancy_threshold}
        self.switch_probabilities = {"High": high_switch_probability, "Medium": medium_switch_probability, "Low": low_switch_probability}
        self.social_learning_strategies = ["Copying the highest-scoring neighbor",
                                           "Copying the most frequently observed strategy",
                                           "Copying randomly"]

        self.running = True
        self.datacollector.collect(self)
        logger.debug("Model initialization complete.")

    def set_education_ratios(self, primary_ratio, primary_edu_level):
        remaining_ratio = (1 - primary_ratio) / 2
        if primary_edu_level == "High":
            self.high_edu_ratio = primary_ratio
            self.medium_edu_ratio = remaining_ratio
            self.low_edu_ratio = remaining_ratio
        elif primary_edu_level == "Medium":
            self.medium_edu_ratio = primary_ratio
            self.high_edu_ratio = remaining_ratio
            self.low_edu_ratio = remaining_ratio
        elif primary_edu_level == "Low":
            self.low_edu_ratio = primary_ratio
            self.high_edu_ratio = remaining_ratio
            self.medium_edu_ratio = remaining_ratio

    def set_social_learning_ratios(self, education_level, individual_ratio, primary_social_ratio, primary_social_strategy):
        social_ratio = 1 - individual_ratio
        remaining_ratio = (social_ratio - primary_social_ratio) / 2
        if primary_social_strategy == "Copying the highest-scoring neighbor":
            social_strategy_ratios = {
                "highest": primary_social_ratio,
                "most_frequent": remaining_ratio,
                "random": remaining_ratio
            }
        elif primary_social_strategy == "Copying the most frequently observed strategy":
            social_strategy_ratios = {
                "highest": remaining_ratio,
                "most_frequent": primary_social_ratio,
                "random": remaining_ratio
            }
        elif primary_social_strategy == "Copying randomly":
            social_strategy_ratios = {
                "highest": remaining_ratio,
                "most_frequent": remaining_ratio,
                "random": primary_social_ratio
            }
        setattr(self, f"{education_level.lower()}_social_strategy_ratios", social_strategy_ratios)

    def average_time_investment(self, education_level):
        agents = [agent for agent in self.schedule.agents if agent.education_level == education_level]
        total_investment = sum(agent.time_investment for agent in agents)
        return total_investment / len(agents) if agents else 0

    def average_child_outcome_score(self, education_level):
        agents = [agent for agent in self.schedule.agents if agent.education_level == education_level]
        total_score = sum(agent.child_outcome_score for agent in agents)
        return total_score / len(agents) if agents else 0

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)

    def run(self, n):
        for _ in range(n):
            self.step()
