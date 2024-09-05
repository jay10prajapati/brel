import pandas as pd
from brel import Fact
from brel.characteristics import Aspect

def pprint_facts_df(facts: list[Fact]):
    """
    Pretty print a list of Fact DataFrames.
    :param facts: the list of Fact DataFrames to pretty print
    """
    # Extract all the dimensions from the facts
    dimension_set = set()
    for fact in facts:
        context = fact.get_context()
        for aspect in context.get_aspects():
            dimension_set.add(aspect)

    dimensions = list(dimension_set)

    # Helper function for sorting dimensions
    def sort_dimensions(dimension: Aspect) -> str:
        if dimension == Aspect.CONCEPT:
            return "1"
        elif dimension == Aspect.PERIOD:
            return "2"
        elif dimension == Aspect.ENTITY:
            return "3"
        elif dimension == Aspect.UNIT:
            return "4"
        else:
            return "5" + dimension.get_name()

    dimensions.sort(key=sort_dimensions)

    # Initialize the DataFrame columns
    columns = ["id"] + [dimension.get_name() for dimension in dimensions] + ["value"]

    # Extract the rows from the facts
    rows = []
    for fact in facts:
        context = fact.get_context()
        row = (
            [fact._get_id()]  # pylint: disable=protected-access
            + [context.get_characteristic(dimension) for dimension in dimensions]
            + [fact.get_value_as_str()]
        )
        rows.append(row)

    # Sort rows alphabetically by the fact id
    rows.sort(key=lambda row: row[0] if isinstance(row[0], str) else "")

    # Create the DataFrame and print it
    df = pd.DataFrame(rows, columns=columns)
    print(df.iloc[1:])

def pprint_fact_df(fact: Fact):
    """
    Prints a single fact in a pandas DataFrame.
    :param fact: the Fact to pretty print
    """
    # Initialize the DataFrame columns
    columns = ["aspect", "value"]

    # Extract the rows from the fact
    rows = []
    context = fact.get_context()
    for aspect in context.get_aspects():
        rows.append([aspect.get_name(), context.get_characteristic(aspect)])

    rows.sort(key=lambda row: row[0] if isinstance(row[0], str) else "")

    # Add the fact value to the rows
    rows.append(["value", fact.get_value_as_str()])

    # Create the DataFrame and print it
    df = pd.DataFrame(rows, columns=columns)
    print(df)