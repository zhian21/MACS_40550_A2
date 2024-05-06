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
        frequency_dependent = len([a for a in model.schedule.agents if a.strategy == "Frequency Dependent Learning"])
        success_base = len([a for a in model.schedule.agents if a.strategy == "Success Base Learning"])
        random_copying = len([a for a in model.schedule.agents if a.strategy == "Random Copying"])
        return "Frequency Dependent Learning Agents: {}<br>Success Base Learning Agents: {}<br>Random Copying Agents: {}".format(
            frequency_dependent, success_base, random_copying
        )

# Instantiate the StrategyTextElement.
strategy_text_element = StrategyTextElement()

# Define a chart module for the average score by strategy.
average_score_chart = ChartModule(
    [
        {"Label": "Average Score(Frequency Dependent)", "Color": "Blue"},
        {"Label": "Average Score(Success Base)", "Color": "Green"},
        {"Label": "Average Score(Random Copying)", "Color": "Red"}
    ],
    data_collector_name='datacollector'
)

# Define a chart module for the number of cooperating and defecting agents.
cooperation_chart = ChartModule(
    [
        {"Label": "Cooperating Agents", "Color": "Blue"},
        {"Label": "Defecting Agents", "Color": "Red"}
    ],
    data_collector_name='datacollector'
)

# Define the visualization grid.
grid = CanvasGrid(agent_portrayal, 50, 50, 500, 500)

# Define the model parameters that can be adjusted in the server interface.
model_params = {
    "initial_cooperate_prob": Slider("Initial Cooperation Probability", 0.5, 0.0, 1.0, 0.1),
    "primary_strategy": Choice("Primary Strategy Type", 
                               choices=["Frequency Dependent Learning", 
                                        "Success Base Learning", "Random Copying"], 
                                        value="Frequency Dependent Learning"),
    "primary_ratio": Slider("The Distribution of Primary Strategy", 0.333, 0.333, 1.0, 0.1),
    "payoff_CC": Slider("Payoff for both cooperating(CC)", 1, 0, 10, 1),
    "payoff_CD": Slider("Payoff for cooperating when the other defects(CD)", 0, 0, 10, 1),
    "payoff_DC": Slider("Payoff for defecting when the other cooperates(DC)", 2, 0, 10, 1),
    "payoff_DD": Slider("Payoff for both defecting(DD)", 0, 0, 10, 1)
}

# Initialize model parameters on server launch.
def server_launch_handler(model):
    """
    Server launch handler function that sets initial model parameters.

    Args:
        model: The model instance being initialized.
    """
    initial_cooperate_prob = model.user_params["initial_cooperate_prob"]
    primary_ratio = model.user_params["primary_ratio"]
    primary_strategy = model.user_params["primary_strategy"]
    model.set_ratios_by_choice(primary_ratio, primary_strategy)
    model.initial_cooperate_prob = initial_cooperate_prob
    model.payoff_matrix = {
        ('C', 'C'): model.user_params["payoff_CC"],
        ('C', 'D'): model.user_params["payoff_CD"],
        ('D', 'C'): model.user_params["payoff_DC"],
        ('D', 'D'): model.user_params["payoff_DD"]
    }

# Configure and launch the ModularServer.
server = ModularServer(
    PdGrid,
    [grid, strategy_text_element, average_score_chart, cooperation_chart],
    "Prisoner's Dilemma Model",
    model_params
)

server.on_server_launched = server_launch_handler
server.launch()
