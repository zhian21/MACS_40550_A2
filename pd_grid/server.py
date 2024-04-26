from mesa.visualization.ModularVisualization import ModularServer, TextElement
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import Choice, Slider
from pd_grid.model import PdGrid 

def agent_portrayal(agent):
    """
    Defines the portrayal of an agent in the Mesa visualization.
    
    Args:
        agent: The agent to be portrayed.

    Returns:
        A dictionary representing the portrayal properties.
    """
    portrayal = {
        "Shape": "rect",
        "w": 0.8,
        "h": 0.8,
        "Filled": "true",
        "Layer": 0,
        "Color": "blue" if agent.move == "C" else "red",
        "text": agent.move,
        "text_color": "white"
    }
    return portrayal


class StrategyTextElement(TextElement):
    """
    TextElement to display the strategy count for agents.
    """
    def render(self, model):
        """
        Renders the strategy counts as HTML text elements.

        Args:
            model: The model instance to gather data from.

        Returns:
            An HTML-formatted string of strategy counts.
        """
        majority = len([a for a in model.schedule.agents if a.strategy == "Majority Rule"])
        best_neighbor = len([a for a in model.schedule.agents if a.strategy == "Best Neighbor"])
        random_strategy = len([a for a in model.schedule.agents if a.strategy == "Random"])
        return "Majority Rule Agents: {}<br>Best Neighbor Agents: {}<br>Random Agents: {}".format(
            majority, best_neighbor, random_strategy
        )

# instantiate the StrategyTextElement.
strategy_text_element = StrategyTextElement()

# define a chart module for the average score by strategy.
average_score_chart = ChartModule(
    [
        {"Label": "Average_Score_Majority", "Color": "Blue"},
        {"Label": "Average_Score_Best_Neighbor", "Color": "Green"},
        {"Label": "Average_Score_Random", "Color": "Red"}
    ],
    data_collector_name='datacollector'
)

# define a chart module for the number of cooperating and defecting agents.
cooperation_chart = ChartModule(
    [
        {"Label": "Cooperating_Agents", "Color": "Blue"},
        {"Label": "Defecting_Agents", "Color": "Red"}
    ],
    data_collector_name='datacollector'
)

# define the visualization grid.
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

# define the model parameters that can be adjusted in the server interface.
model_params = {
    "ratio_choice": Choice(
        "Strategy Ratio Configuration",
        choices=["equal", "more_majority", "more_best", "more_random"],
        value="equal"
    ),
    "initial_cooperate_prob": Slider(
        "Initial Cooperation Probability", 0.5, 0.0, 1.0, 0.1
    ),
    "payoff_CC": Slider(
        "Payoff for both cooperating", 1, 0, 10, 1
    ),
    "payoff_CD": Slider(
        "Payoff for cooperating when the other defects", 0, 0, 10, 1
    ),
    "payoff_DC": Slider(
        "Payoff for defecting when the other cooperates", 2, 0, 10, 1
    ),
    "payoff_DD": Slider(
        "Payoff for both defecting", 0, 0, 10, 1
    )
}

# initialize model parameters on server launch.
def server_launch_handler(model):
    """
    Server launch handler function that sets initial model parameters.

    Args:
        model: The model instance being initialized.
    """
    ratio_choice = model.user_params["ratio_choice"]
    initial_cooperate_prob = model.user_params["initial_cooperate_prob"]
    model.set_ratios_by_choice(ratio_choice)
    model.initial_cooperate_prob = initial_cooperate_prob
    model.payoff_matrix = {
        ('C', 'C'): model.user_params["payoff_CC"],
        ('C', 'D'): model.user_params["payoff_CD"],
        ('D', 'C'): model.user_params["payoff_DC"],
        ('D', 'D'): model.user_params["payoff_DD"]
    }

# configure and launch the ModularServer.
server = ModularServer(
    PdGrid,
    [grid, strategy_text_element, average_score_chart, cooperation_chart],
    "Prisoner's Dilemma Model",
    model_params
)

server.on_server_launched = server_launch_handler
server.launch()