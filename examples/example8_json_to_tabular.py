import json
from tabulate import tabulate
from collections import defaultdict
import pandas as pd

def format_value(value):
    try:
        return f"{int(value):,}"
    except ValueError:
        return value

def process_json(data):
    table_data = defaultdict(lambda: defaultdict(str))
    
    for item in data:
        process_item(item, table_data)
    
    return table_data

def process_item(item, table_data, prefix=""):
    name = item.get('name', '').split(':')[-1]
    full_name = f"{prefix}{name}"
    
    if 'facts' in item:
        for fact in item['facts']:
            period = fact['period']
            value = format_value(fact['value'])
            
            if period.startswith('from'):
                start_date, end_date = period.split(' to ')
                start_year = start_date.split('-')[0]
                end_year = end_date.split('-')[0]
                column = f"{start_date} to {end_date}"
            else:
                column = f"As on: {period}"
            
            table_data[full_name][column] = value
    
    if 'children' in item:
        for child in item['children']:
            process_item(child, table_data, f"{full_name} > ")

def create_table(table_data):
    all_columns = set()
    for values in table_data.values():
        all_columns.update(values.keys())
    
    headers = ["Statement of cash flows [Abstract]"] + sorted(all_columns)
    rows = []
    
    for key, values in table_data.items():
        row = [key] + [values.get(header, "") for header in headers[1:]]
        rows.append(row)
    
    return tabulate(rows, headers, tablefmt="grid"), headers, rows

def create_dataframe(headers, rows):
    df = pd.DataFrame(rows, columns=headers)
    df.set_index("Statement of cash flows [Abstract]", inplace=True)
    return df

# Load JSON data
with open('./examples/sample_results/CashFlowStatementIndirect_320000_facts_CashFlowStatementIndirect_320000.json', 'r') as f:
    json_data = json.load(f)

# Process JSON data
table_data = process_json(json_data)

# Create table and DataFrame
table, headers, rows = create_table(table_data)
df = create_dataframe(headers, rows)

# Print table
# print(table)

# Print DataFrame
# print("\nPandas DataFrame:")
# print(df)

# Optionally, save DataFrame to CSV
df.to_csv('./examples/sample_results/cash_flow_statement.csv')