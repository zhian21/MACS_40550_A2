def portrayPDAgent(agent):
    """
    This function is registered with the visualization server to be called
    each tick to indicate how to draw the agent in its current state.
    
    Args:
        agent: the agent in the simulation

    Returns:
        A dictionary describing how to draw the agent.
    """
    if agent is None:
        raise AssertionError("Agent instance is None.")

    return {
        "Shape": "rect",
        "w": 1,
        "h": 1,
        "Filled": "true",
        "Layer": 0,
        "x": agent.pos[0],
        "y": agent.pos[1],
        "Color": "blue" if agent.is_cooperating else "red",
    }
