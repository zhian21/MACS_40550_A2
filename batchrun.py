from pd_grid.model import PdGrid
from mesa.batchrunner import batch_run
import numpy as np
import pandas as pd

# Define ranges for payoff values
payoff_CC_range = np.arange(0, 6, 1)  # From 0 to 5 inclusive, spaced by 1
payoff_CD_range = np.array([0, 1])  # Only 0 and 1
payoff_DC_range = np.arange(0, 6, 1)  # From 0 to 5 inclusive, spaced by 1
payoff_DD_range = np.array([0])  # Constant value of 0

# Define range for initial cooperation probabilities
initial_cooperate_prob_range = np.arange(0.25, 0.76, 0.25)  # From 0.25 to 0.75 inclusive, spaced by 0.25

# Define strategy distribution variations
primary_strategy_range = np.array([1/3, 0.53, 0.73])

# Parameters to vary
parameters = {
    "initial_cooperate_prob": initial_cooperate_prob_range,
    "payoff_CC": payoff_CC_range,
    "payoff_CD": payoff_CD_range,
    "payoff_DC": payoff_DC_range,
    "payoff_DD": payoff_DD_range,
    "primary_ratio": primary_strategy_range,
    "primary_strategy": ["Frequency Dependent Learning", "Success Base Learning", "Random Copying"]
}

# The main block to avoid multiprocessing issues
if __name__ == '__main__':
    # Run the batch simulation
    results = batch_run(
        model_cls=PdGrid,
        parameters=parameters,
        iterations=30,
        max_steps=50,
        data_collection_period=5,
        number_processes=4
    )

    # Convert results to pandas DataFrame
    df = pd.DataFrame(results)

    # Save the data to a CSV file
    df.to_csv("batch_run_results_2.csv")
