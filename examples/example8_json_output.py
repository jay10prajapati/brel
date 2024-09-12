import argparse
import json
from brel import Filing
import brel.utils
from brel import QName

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, QName):
            return str(obj)
        return super().default(obj)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="./examples/sample_data/ola.s.2019.xml")
    parser.add_argument("--component", default="StatementOfProfitAndLoss_210000", help="Component URI to display facts for")
    return parser.parse_args()

def facts_to_network_json(node, facts_by_concept):
    result = {
        "name": node.get_report_element().get_name() if node.get_report_element() else "Unknown",
        "children": []
    }
    
    concept = node.get_report_element()
    if concept:
        concept_name = concept.get_name()
        if concept_name in facts_by_concept:
            facts = facts_by_concept[concept_name]
            result["facts"] = [fact.get_value() for fact in facts]
    
    for child in node.get_children():
        result["children"].append(facts_to_network_json(child, facts_by_concept))
    
    return result

def create_facts_json(node, facts_by_concept):
    result = {
        "name": node.get_report_element().get_name() if node.get_report_element() else "Unknown",
        "children": []
    }
    
    concept = node.get_report_element()
    if concept:
        concept_name = concept.get_name()
        if concept_name in facts_by_concept:
            facts = facts_by_concept[concept_name]
            result["facts"] = [
                {
                    "value": fact.get_value(),
                    "unit": str(fact.get_unit()) if fact.get_unit() else None,
                    "period": str(fact.get_period()) if fact.get_period() else None
                }
                for fact in facts
            ]
        else:
            result["facts"] = []
    
    for child in node.get_children():
        child_result = create_facts_json(child, facts_by_concept)
        if child_result["facts"] or child_result["children"]:
            result["children"].append(child_result)
    
    return result

def save_json_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2, cls=CustomEncoder)

def main():
    args = parse_arguments()
    args.component = "BalanceSheet_110000"
    args.component = "CashFlowStatement"
    # args.component = "613300"

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
        
        # Create JSON structure
        json_data = []
        for root in presentation_network.get_roots():
            json_data.append(create_facts_json(root, facts_by_concept))
        
        # Save JSON to file
        output_filename = f"./examples/sample_results/{args.component}_facts1.json"
        save_json_to_file(json_data, output_filename)
        print(f"Facts saved to {output_filename}")

        # Print facts in network order (existing functionality)
        # print("\nFacts in network order:")
        # for root in presentation_network.get_roots():
        #     print_facts_in_network_order(root, facts_by_concept)

    else:
        print(f"No component found with URI containing: {args.component}")

if __name__ == "__main__":
    main()