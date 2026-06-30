import os
import sys
import json
import argparse
from utils.db_utils import resolve_schema
from utils.config_loader import config

def resolve_cognos_table(table_name, schema, config_node):
    """
    Takes a table reference. If it already has a schema, it passes it.
    If it lacks a schema, it resolves the true Oracle schema via db lookup.
    """
    if schema:
        return f"{schema}.{table_name}", "ALREADY_RESOLVED"
    elif "." in table_name:
        return table_name, "ALREADY_RESOLVED"
    else:
        print(f"Resolving via Oracle DB ({config_node}): {table_name}")
        db_schema = resolve_schema(table_name, config_node)
        
        if db_schema:
            print(f"  -> Found schema: {db_schema}")
            return f"{db_schema}.{table_name}", "DATABASE"
        else:
            print(f"  !! WARNING: Could not resolve schema for {table_name}")
            return f"UNRESOLVED.{table_name}", "UNRESOLVED"

def main():
    parser = argparse.ArgumentParser(description="Resolve Cognos tables.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to the original XML file. Defaults to input/fm_model.xml in the project root.",
    )
    args = parser.parse_args()

    project_root = os.path.join(os.path.dirname(__file__), "..")
    
    if args.input_file:
        file_path = args.input_file
    else:
        file_path = os.path.join(project_root, "input", "fm_model.xml")

    input_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.join(project_root, "output", input_filename)
    os.makedirs(output_dir, exist_ok=True)

    input_json = os.path.join(output_dir, "extracted_tables.json")
    
    if not os.path.exists(input_json):
        print(f"Error: {input_json} not found. Please run extract_tables_from_project.py first.")
        sys.exit(1)
        
    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    tables = data.get("tables", [])
    
    datasource_mapping = config.get("datasource_mapping", {})
    if not datasource_mapping:
        print("Error: No 'datasource_mapping' found in config.yaml.")
        sys.exit(1)
        
    resolved_by_ds = {}
    stats = {}
    
    print(f"Processing {len(tables)} tables...")
    for t_info in tables:
        if not t_info or not isinstance(t_info, dict):
            continue
            
        t_name = t_info.get("table")
        cm_ds = t_info.get("cmDataSource")
        schema = t_info.get("schema")
        
        if not t_name:
            continue
            
        if cm_ds not in datasource_mapping:
            # Ignore data sources not in our mapping
            continue
            
        config_node = datasource_mapping[cm_ds]
        
        if cm_ds not in resolved_by_ds:
            resolved_by_ds[cm_ds] = []
            stats[cm_ds] = {"ALREADY_RESOLVED": 0, "DATABASE": 0, "UNRESOLVED": 0}
            
        resolved_name, method = resolve_cognos_table(t_name, schema, config_node)
        resolved_by_ds[cm_ds].append(resolved_name)
        stats[cm_ds][method] += 1
        
    print("\n--- Resolution Complete ---")
    for cm_ds, resolved_list in resolved_by_ds.items():
        # Sort and deduplicate
        resolved_list = sorted(list(set(resolved_list)))
        
        output_file = os.path.join(output_dir, f"resolved_tables_{cm_ds}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            for r in resolved_list:
                f.write(f"{r}\n")
                
        print(f"\n--- Data Source: {cm_ds} ({datasource_mapping[cm_ds]}) ---")
        print(f"Already Resolved (from XML or Native): {stats[cm_ds]['ALREADY_RESOLVED']}")
        print(f"Database Lookups: {stats[cm_ds]['DATABASE']}")
        print(f"Unresolved: {stats[cm_ds]['UNRESOLVED']}")
        print(f"Saved {len(resolved_list)} unique fully-qualified tables to {output_file}")

if __name__ == "__main__":
    main()
