"""
Module for pretty printing the most common Brel DataFrame objects to the console.
Acts as a wrapper around the other pretty print functions and automatically selects the correct one based on the given object.

====================

- author: Robin Schmidiger
- version: 0.1
- date: 03 February 2024

====================
"""

from brel import Fact, Component
from brel.networks import INetwork, INetworkNode
from brel.utils import (
    pprint_fact_df,
    pprint_facts_df,
    pprint_network_df,
    pprint_component_df,
)
import pandas as pd


def pprint_df(to_print):
    """
    Pretty print the given DataFrame object.
    Supports the following objects:
    - Fact
    - list[Fact]
    - INetwork
    - INetworkNode
    - Component

    :param to_print: the DataFrame object to pretty print
    :raises ValueError: if the given object is not supported
    """
    if isinstance(to_print, Fact):
        pprint_fact_df(to_print)
    elif isinstance(to_print, list):
        if len(to_print) == 0:
            pprint_facts_df(to_print)
        elif isinstance(to_print[0], Fact):
            return pprint_facts_df(to_print)
        elif isinstance(to_print[0], Component):
            for component in to_print:
                pprint_component_df(component)
        else:
            raise TypeError("Can only pretty print lists of facts.")
    elif isinstance(to_print, INetwork):
        pprint_network_df(to_print)
    elif isinstance(to_print, Component):
        pprint_component_df(to_print)
    elif isinstance(to_print, pd.DataFrame):
        print(to_print)
    else:
        raise TypeError(
            f"Can only pretty print facts, lists of facts, components, networks, network nodes, and DataFrames. Got {type(to_print)}"
        )