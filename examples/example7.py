import argparse
from brel import Filing
import brel.utils
from brel.utils.print_networks import pprint_network_node

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="./examples/sample_data/ola.s.2019.xml")
    parser.add_argument("--component", default="StatementOfProfitAndLoss_210000", help="Component URI to display facts for")
    return parser.parse_args()

def print_facts_in_network_order(node, facts_by_concept, indent=""):
    concept = node.get_report_element()
    if concept:
        concept_name = concept.get_name()
        if concept_name in facts_by_concept:
            facts = facts_by_concept[concept_name]
            print(f"{indent}{concept_name}:")
            brel.utils.pprint(facts)            
        else:
            print(f"{indent}{concept_name}: None")
    
    for child in node.get_children():
        print_facts_in_network_order(child, facts_by_concept, indent + "  ")

def main():
    args = parse_arguments()
    args.component = "BalanceSheet_110000"
    args.component = "CashFlowStatement"
    args.component = "613300"

    report = Filing.open(args.file)
    
    component = next((c for c in report.get_all_components() if args.component in c.get_URI()), None)
    if component:
        print(f"Facts for component: {component.get_URI()}")

        # Get all facts from the report
        all_facts = report.get_all_facts()
        
        # Get the presentation network for the component
        presentation_network = component.get_presentation_network()
        
        # Create a dictionary to store facts by concept name
        facts_by_concept = {}
        for fact in all_facts:
            concept_name = fact.get_concept().get_value().get_name()
            if concept_name not in facts_by_concept:
                facts_by_concept[concept_name] = []
            facts_by_concept[concept_name].append(fact)
        
        
        # Traverse the presentation network and print facts in order
        # for node in presentation_network.get_all_nodes():
        #     concept = node.get_report_element()
        #     if concept:
        #         concept_name = concept.get_name()
        #         if concept_name in facts_by_concept:
        #             fact = facts_by_concept[concept_name]
        #             print(f"{concept_name}: {fact.get_value()}")
        #         else:
        #             print(f"{concept_name}: None")
        
        # Print facts in network order
        for root in presentation_network.get_roots():
            print_facts_in_network_order(root, facts_by_concept)

    else:
        print(f"No component found with URI containing: {args.component}")

if __name__ == "__main__":
    main()