from mesa.visualization.ModularVisualization import ModularServer, TextElement
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import Choice, Slider
from .model import ParentalLearningModel

def agent_portrayal(agent):
    portrayal = {
        "Shape": "rect",
        "w": 0.8,
        "h": 0.8,
        "Filled": "true",
        "Layer": 0,
        "Color": "blue" if agent.strategy == "Individual Learning" else "green",
        "text": round(agent.time_investment, 1),
        "text_color": "white"
    }
    return portrayal

class StrategyTextElement(TextElement):
    def render(self, model):
        individual_learning = len([a for a in model.schedule.agents if a.strategy == "Individual Learning"])
        social_learning = len([a for a in model.schedule.agents if a.strategy != "Individual Learning"])
        return "Individual Learning Agents: {}<br>Social Learning Agents: {}".format(
            individual_learning, social_learning
        )

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

grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

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

server = ModularServer(
    ParentalLearningModel,
    [grid, strategy_text_element, average_score_chart],
    "Parental Learning Strategies Model",
    model_params
)

server.port = 8521  # The default
server.launch()