# MACS 40550 Assignment 2

### Project goal
The project aims to explore the dynamics of cooperation and defection within the context of an agent-based Prisoner's Dilemma model. By introducing diverse learning strategies and variable pay-off structures, it seeks to understand how these elements influence the emergence and sustainability of cooperative behavior in a simulated social environment.

### Github Navigation Steps  
* First clone the repository at your local machine.
* The structure of the repository is as follows:
   * model.py contains all the python script for the setup of the model
   * server.py contains all the python script for seting up and running a server.
   * requirement.text contains all the required libraries.
   * agent.py contains all the python script for the setup of the agent
   * batchrun.py contains all the python script for the batch run
   * analysis.ipynb contains all the python script for analyzing the data for the batch run results


## Installation

To install the dependencies use pip and the requirements.txt in this directory. e.g.

```
    $ pip install -r requirements.txt
```

## How to Run

To run the model interactively, run ``mesa runserver`` in this directory. e.g.

```
    $ mesa runserver
```
or

Directly run the file ``run.py`` in the terminal. e.g.

```
    $ python run.py
```

