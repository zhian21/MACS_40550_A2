from pd_grid.model import PdGrid
from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd

# define ranges for payoff values
payoff_CC_range = np.linspace(0, 3, 3)
payoff_CD_range = np.linspace(0, 3, 3)
payoff_DC_range = np.linspace(0, 3, 3)
payoff_DD_range = np.linspace(0, 3, 3)

# initial cooperation probabilities
initial_cooperate_prob_range = np.linspace(0, 1, 5)

# parameters to vary
parameters = {
    "initial_cooperate_prob": initial_cooperate_prob_range,
    "payoff_CC": payoff_CC_range,
    "payoff_CD": payoff_CD_range,
    "payoff_DC": payoff_DC_range,
    "payoff_DD": payoff_DD_range,
    "ratio_choice": ["equal", "more_majority", "more_best", "more_random"]
}

# run the batch simulation
results = batch_run(
    model_cls=PdGrid,
    parameters=parameters,
    iterations= 2,
    max_steps=50,
    data_collection_period= 1
)

# convert results to pandas DataFrame
df = pd.DataFrame(results)

# save the data to a CSV file
df.to_csv("batch_run_results.csv")
