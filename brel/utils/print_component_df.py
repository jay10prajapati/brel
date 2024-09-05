import pandas as pd
from brel import Component

def pprint_component_df(component: Component):
    """
    Pretty print a Component DataFrame.
    :param component: the Component DataFrame to pretty print
    """
    # Initialize the DataFrame columns
    columns = ["attribute", "value"]

    # Extract the rows from the component
    rows = []
    for attribute, value in component.__dict__.items():
        rows.append([attribute, value])

    rows.sort(key=lambda row: row[0] if isinstance(row[0], str) else "")

    # Create the DataFrame and print it
    df = pd.DataFrame(rows, columns=columns)
    print(df)