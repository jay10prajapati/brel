import argparse
from brel import Filing
import brel.utils
import pandas as pd

def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?")
    parser.add_argument("--facts", default=None)
    parser.add_argument("--components", default=None)
    parser.add_argument("--pickle_folder", default="pickle_folder")
    parser.add_argument("--component", default=None, help="Component URI to display facts for")

    return parser.parse_args()

def main():
    """
    Main function to demonstrate the usage of FilingManager.
    """
    args = parse_arguments()
    args.file = "./examples/sample_data/ola.s.2019.xml"
    args.component = "StatementOfProfitAndLoss_210000"

    report = Filing.open(args.file)
    
    if args.component:
        component = next((c for c in report.get_all_components() if args.component in c.get_URI()), None)
        if component:
            print(f"Facts for component: {component.get_URI()}")

            # Get all facts from the report
            all_facts = report.get_all_facts()
            
            # Get the presentation network for the component
            presentation_network = component.get_presentation_network()
            
            # Get all concepts in the presentation network
            component_concepts = set()
            for node in presentation_network.get_all_nodes():
                concept = node.get_report_element()
                if concept:
                    component_concepts.add(concept.get_name())
            
            # Filter facts based on the component's concepts
            facts = [fact for fact in all_facts if fact.get_concept().get_value().get_name() in component_concepts]
            # brel.utils.pprint_df(facts)
            df = brel.utils.pprint_df(facts)
            df.to_clipboard()
        else:
            print(f"No component found with URI containing: {args.component}")
    else:
        print("Available components:")
        for component in report.get_all_components():
            print(component.get_URI())

if __name__ == "__main__":
    main()