import logging
import mesa
from mesa.visualization import ModularServer
from mesa.visualization.modules import NetworkModule, ChartModule, TextElement
from mesa.visualization.UserParam import Choice, Slider
from .model import ParentalLearningModel 


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("Starting server setup...")

def network_portrayal(G):
    def node_color(agent):
        return "blue" if agent.strategy == "Individual Learning" else "green"

    def edge_color(agent1, agent2):
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = {
        "nodes": [
            {
                "id": node_id,
                "size": 6,
                "color": node_color(agents[0]),
                "tooltip": f"id: {agents[0].unique_id}<br>strategy: {agents[0].strategy}",
            }
            for node_id, agents in G.nodes.data("agent")
        ],
        "edges": [
            {
                "source": source,
                "target": target,
                "color": edge_color(*get_agents(source, target)),
                "width": edge_width(*get_agents(source, target)),
            }
            for source, target in G.edges
        ],
    }

    return portrayal

network = NetworkModule(network_portrayal, 500, 500)

class StrategyTextElement(TextElement):
    def render(self, model):
        individual_learning = len([a for a in model.schedule.agents if a.strategy == "Individual Learning"])
        social_learning = len([a for a in model.schedule.agents if a.strategy != "Individual Learning"])
        return f"Individual Learning Agents: {individual_learning}<br>Social Learning Agents: {social_learning}"

strategy_text_element = StrategyTextElement()

average_score_chart = ChartModule(
    [
        {"Label": "Average Child Outcome Score (High)", "Color": "Blue"},
        {"Label": "Average Child Outcome Score (Medium)", "Color": "Green"},
        {"Label": "Average Child Outcome Score (Low)", "Color": "Red"},
        {"Label": "Average Time Investment (High)", "Color": "Orange"},
        {"Label": "Average Time Investment (Medium)", "Color": "Purple"},
        {"Label": "Average Time Investment (Low)", "Color": "Brown"}
    ],
    data_collector_name='datacollector'
)

model_params = {
    "initial_density": Slider("Initial Density of Agents", 0.8, 0.1, 1.0, 0.1),
    "optimal_time_investment": Slider("Optimal Time Investment", 40, 0, 100, 1),
    "primary_edu_ratio": Slider("Ratio of Education Levels", 0.33, 0.1, 0.9, 0.01),
    "high_individual_learning_ratio": Slider("High Education: Individual Learning Ratio", 0.7, 0.1, 1.0, 0.01),
    "medium_individual_learning_ratio": Slider("Medium Education: Individual Learning Ratio", 0.7, 0.1, 1.0, 0.01),
    "low_individual_learning_ratio": Slider("Low Education: Individual Learning Ratio", 0.7, 0.1, 1.0, 0.01),
    "high_primary_social_ratio": Slider("High Education: Primary Social Ratio", 0.5, 0.1, 1.0, 0.01),
    "medium_primary_social_ratio": Slider("Medium Education: Primary Social Ratio", 0.5, 0.1, 1.0, 0.01),
    "low_primary_social_ratio": Slider("Low Education: Primary Social Ratio", 0.5, 0.1, 1.0, 0.01),
    "high_primary_social_strategy": Choice("High Education: Primary Social Strategy", 
                                           choices=["Copying the highest-scoring neighbor", "Copying the most frequently observed strategy", "Copying randomly"], 
                                           value="Copying the highest-scoring neighbor"),
    "medium_primary_social_strategy": Choice("Medium Education: Primary Social Strategy", 
                                             choices=["Copying the highest-scoring neighbor", "Copying the most frequently observed strategy", "Copying randomly"], 
                                             value="Copying the highest-scoring neighbor"),
    "low_primary_social_strategy": Choice("Low Education: Primary Social Strategy", 
                                          choices=["Copying the highest-scoring neighbor", "Copying the most frequently observed strategy", "Copying randomly"], 
                                          value="Copying the highest-scoring neighbor"),
    "avg_degree_high": Slider("Average Degree High", 4, 1, 20, 1),
    "rewiring_prob_high": Slider("Rewiring Probability High", 0.1, 0, 1, 0.01),
    "avg_degree_medium": Slider("Average Degree Medium", 6, 1, 20, 1),
    "rewiring_prob_medium": Slider("Rewiring Probability Medium", 0.3, 0, 1, 0.01),
    "avg_degree_low": Slider("Average Degree Low", 8, 1, 20, 1),
    "rewiring_prob_low": Slider("Rewiring Probability Low", 0.5, 0, 1, 0.01),
    "high_discrepancy_threshold": Slider("High Education: Discrepancy Threshold", 5, 0, 20, 1),
    "medium_discrepancy_threshold": Slider("Medium Education: Discrepancy Threshold", 10, 0, 20, 1),
    "low_discrepancy_threshold": Slider("Low Education: Discrepancy Threshold", 15, 0, 20, 1),
    "high_switch_probability": Slider("High Education: Switch Probability", 0.1, 0, 1, 0.01),
    "medium_switch_probability": Slider("Medium Education: Switch Probability", 0.3, 0, 1, 0.01),
    "low_switch_probability": Slider("Low Education: Switch Probability", 0.5, 0, 1, 0.01)
}

try:
    server = mesa.visualization.ModularServer(
        ParentalLearningModel,
        [network, strategy_text_element, average_score_chart],
        "Parental Learning Strategies Model",
        model_params
    )
    server.port = 8521 
    logger.debug("Server setup complete.")
except Exception as e:
    logger.exception("Error during server setup: %s", e)
