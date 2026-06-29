import xml.etree.ElementTree as ET
import sqlglot
from sqlglot import exp
from collections import Counter
import re
import json
import os
import argparse


def extract_tables_from_sql(sql_text):
    try:
        # Pre-process Cognos macros to avoid parsing errors
        # Replace anything between '#' with a dummy string literal
        cleaned_sql = re.sub(r"#.*?#", "'dummy'", sql_text, flags=re.DOTALL)

        # Using tsql dialect because it natively supports the [Schema] bracket notation used by Cognos
        parsed = sqlglot.parse_one(cleaned_sql, read="tsql")

        # Identify all CTE aliases so we can ignore them
        ctes = {cte.alias for cte in parsed.find_all(exp.CTE)}

        tables = set()
        for table in parsed.find_all(exp.Table):
            if table.name and table.name not in ctes:
                db_node = table.args.get("db")
                name_node = table.args.get("this")
                
                parts = []
                
                if db_node:
                    db_str = db_node.name
                    if getattr(db_node, "quoted", False):
                        db_str = f"[{db_str}]"
                    parts.append(db_str)
                
                schema = ".".join(parts)
                
                name_str = name_node.name if name_node else table.name
                if name_node and getattr(name_node, "quoted", False):
                    name_str = f"[{name_str}]"
                
                if schema:
                    tables.add(f"{schema}.{name_str}")
                else:
                    tables.add(name_str)
        return tables
    except Exception as e:
        # Return empty set if parsing fails
        print(f"Failed to parse SQL: {e}")
        return set()


def extract_from_xml_root(root, namespaces):
    ds_map = {}
    for ds in root.findall(".//ns:dataSource", namespaces):
        name_node = ds.find("ns:name", namespaces)
        schema_node = ds.find("ns:schema", namespaces)
        if (
            name_node is not None
            and schema_node is not None
            and name_node.text
            and schema_node.text
        ):
            ds_map[name_node.text.strip().upper()] = schema_node.text.strip().upper()

    definition_types = Counter()
    unique_tables = set()

    def process_table(table_str, sql_type):
        t_upper = table_str.upper()
        if '.' in t_upper:
            parts = t_upper.rsplit('.', 1)
            raw_prefix = parts[0]
            raw_table = parts[1]
            
            if '.' in raw_prefix:
                if raw_prefix.startswith('[') and raw_prefix.endswith(']') and raw_prefix.count('[') == 1:
                    pass
                else:
                    raw_prefix = raw_prefix.rsplit('.', 1)[-1]
            
            prefix_no_brackets = raw_prefix.replace('[', '').replace(']', '')

            if sql_type == "cognos" and prefix_no_brackets in ds_map:
                return f"{ds_map[prefix_no_brackets]}.{raw_table}"
            else:
                return f"{raw_prefix}.{raw_table}"
        else:
            return t_upper

    for qs in root.findall(".//ns:querySubject", namespaces):
        definition = qs.find("ns:definition", namespaces)
        if definition is not None:
            for child in definition:
                definition_types[child.tag] += 1
                if child.tag.endswith("dbQuery"):
                    sql = child.find("ns:sql", namespaces)
                    if sql is not None:
                        sql_type = sql.get("type", "unknown")
                        tables = sql.findall(".//ns:table", namespaces)
                        if not tables:
                            # Parse raw SQL
                            sql_text = "".join(sql.itertext()).strip()
                            if sql_text:
                                parsed_tables = extract_tables_from_sql(sql_text)
                                for pt in parsed_tables:
                                    resolved_t = process_table(pt, sql_type)
                                    unique_tables.add(resolved_t)
                        else:
                            for t in tables:
                                if t.text:
                                    resolved_t = process_table(t.text.strip(), sql_type)
                                    unique_tables.add(resolved_t)

                    dbObj = child.find("ns:dbObjectName", namespaces)
                    if dbObj is not None and dbObj.text:
                        resolved_t = process_table(dbObj.text.strip(), "unknown")
                        unique_tables.add(resolved_t)

    unqualified_tables = {t for t in unique_tables if '.' not in t}
    qualified_table_names = {t.rsplit('.', 1)[-1] for t in unique_tables if '.' in t}
    tables_to_remove = unqualified_tables.intersection(qualified_table_names)
    unique_tables = unique_tables - tables_to_remove

    return ds_map, definition_types, unique_tables


def extract_from_xml_file(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    namespaces = {"ns": "http://www.developer.cognos.com/schemas/bmt/60/12"}
    return extract_from_xml_root(root, namespaces)


def extract_from_xml_string(xml_string):
    root = ET.fromstring(xml_string)
    namespaces = {"ns": "http://www.developer.cognos.com/schemas/bmt/60/12"}
    return extract_from_xml_root(root, namespaces)


def main():
    parser = argparse.ArgumentParser(description="Extract tables from Cognos FM model XML.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to the input XML file. Defaults to input/fm_model.xml in the project root.",
    )
    args = parser.parse_args()

    project_root = os.path.join(os.path.dirname(__file__), "..")
    
    if args.input_file:
        file_path = args.input_file
    else:
        file_path = os.path.join(project_root, "input", "fm_model.xml")

    try:
        ds_map, definition_types, table_refs = extract_from_xml_file(file_path)

        print("Definition types found in query subjects:", dict(definition_types))
        print(f"Total unique table references found: {len(table_refs)}")

        # Sort and print a few of them
        sorted_tables = sorted(list(table_refs))
        print("Sample table references:", sorted_tables[:15])

        # Get input filename without extension
        input_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(project_root, "output", input_filename)
        os.makedirs(output_dir, exist_ok=True)

        # Save to a file
        output_file = os.path.join(output_dir, "extracted_tables.json")
        output_data = {"tables": sorted_tables}

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=4)

        print(f"Saved the full list of {len(sorted_tables)} tables to {output_file}")

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    main()
