import os
import xml.etree.ElementTree as ET

def check_xml_files(directory):
    files_to_check = [f for f in os.listdir(directory) if f.endswith('.xml')]
    
    if not files_to_check:
        print(f"No XML files found in directory: {directory}")
        return

    issues = []

    for filename in files_to_check:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue
            
        print(f"Processing {filename}...")
        
        try:
            # We use iterparse to handle large files efficiently
            context = ET.iterparse(filepath, events=('end',))
            
            for event, elem in context:
                # Remove namespace for easier matching
                tag = elem.tag.split('}')[-1]
                
                if tag == 'querySubject':
                    name = "Unknown"
                    for child in elem:
                        if child.tag.split('}')[-1] == 'name':
                            name = child.text
                            break

                    definitions = [child for child in elem.iter() if child.tag.split('}')[-1] == 'definition']
                    if len(definitions) == 0:
                        print(f"  [!] querySubject '{name}' has no <definition> element.")
                        issues.append({
                            "file": filename,
                            "querySubject": name,
                            "type": "missing_definition"
                        })
                    else:
                        for definition in definitions:
                            db_queries = [child for child in definition.iter() if child.tag.split('}')[-1] == 'dbQuery']
                            model_queries = [child for child in definition.iter() if child.tag.split('}')[-1] == 'modelQuery']
                            
                            if not db_queries and not model_queries:
                                print(f"  [!] querySubject '{name}' <definition> has no <dbQuery> or <modelQuery> element.")
                                issues.append({
                                    "file": filename,
                                    "querySubject": name,
                                    "type": "missing_query_element"
                                })
                                
                            for db_query in db_queries:
                                sqls = [child for child in db_query.iter() if child.tag.split('}')[-1] == 'sql']
                                if not sqls:
                                    print(f"  [!] querySubject '{name}' <dbQuery> has no <sql> element.")
                                    issues.append({
                                        "file": filename,
                                        "querySubject": name,
                                        "type": "missing_sql"
                                    })

                    # Check if it's a modelQuery and ignore it for the sources validation
                    is_model_query = False
                    for child in elem.iter():
                        if child.tag.split('}')[-1] == 'modelQuery':
                            is_model_query = True
                            break
                            
                    if is_model_query:
                        elem.clear()
                        continue

                    # Find all 'sources' elements (handle namespace)
                    sources_elements = [child for child in elem.iter() if child.tag.split('}')[-1] == 'sources']
                    
                    if len(sources_elements) != 1:
                        print(f"  [!] querySubject '{name}' has {len(sources_elements)} <sources> elements (expected exactly 1).")
                        issues.append({
                            "file": filename,
                            "querySubject": name,
                            "type": "invalid_sources_count",
                            "count": len(sources_elements)
                        })
                        
                    for sources_elem in sources_elements:
                        datasource_refs = [child for child in sources_elem.iter() if child.tag.split('}')[-1] == 'dataSourceRef']
                        if len(datasource_refs) == 0:
                            print(f"  [!] querySubject '{name}' has a <sources> element with 0 <dataSourceRef> elements (expected at least 1).")
                            issues.append({
                                "file": filename,
                                "querySubject": name,
                                "type": "invalid_dataSourceRefs_count",
                                "count": 0
                            })
                        elif len(datasource_refs) > 1:
                            print(f"  [i] querySubject '{name}' has a <sources> element with {len(datasource_refs)} <dataSourceRef> elements. This is considered valid.")
                            
                    # Clear the querySubject element from memory after processing its contents
                    elem.clear()
                
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    if not issues:
        print("\nNo issues found! All querySubjects have exactly 1 <sources> element, which has at least 1 <dataSourceRef>.")
        
    return issues

def validate_data_sources(directory):
    files_to_check = [f for f in os.listdir(directory) if f.endswith('.xml')]
    
    if not files_to_check:
        print(f"No XML files found in directory: {directory}")
        return

    issues = []

    for filename in files_to_check:
        filepath = os.path.join(directory, filename)
        if not os.path.exists(filepath):
            continue
            
        print(f"Validating data sources in {filename}...")
        
        try:
            context = ET.iterparse(filepath, events=('end',))
            
            for event, elem in context:
                tag = elem.tag.split('}')[-1]
                
                if tag == 'dataSource':
                    name = "Unknown"
                    for child in elem:
                        if child.tag.split('}')[-1] == 'name':
                            name = child.text
                            break

                    if name == "Unknown":
                        print(f"  [!] dataSource has no <name> element.")
                        issues.append({
                            "file": filename,
                            "dataSource": name,
                            "type": "invalid_missing_name",
                            "count": 0
                        })
                        elem.clear()
                        continue

                    cm_data_sources = [child for child in elem.iter() if child.tag.split('}')[-1] == 'cmDataSource']
                    schemas = [child for child in elem.iter() if child.tag.split('}')[-1] == 'schema']
                    
                    if len(cm_data_sources) != 1:
                        print(f"  [!] dataSource '{name}' has {len(cm_data_sources)} <cmDataSource> elements (expected 1).")
                        issues.append({
                            "file": filename,
                            "dataSource": name,
                            "type": "invalid_cmDataSource_count",
                            "count": len(cm_data_sources)
                        })
                        
                    if len(schemas) == 0:
                        print(f"  [i] dataSource '{name}' has 0 <schema> elements. This is considered valid.")
                    elif len(schemas) > 1:
                        print(f"  [!] dataSource '{name}' has {len(schemas)} <schema> elements (expected 0 or 1).")
                        issues.append({
                            "file": filename,
                            "dataSource": name,
                            "type": "invalid_schema_count",
                            "count": len(schemas)
                        })
                        
                    elem.clear()
                
        except Exception as e:
            print(f"Error parsing {filename}: {e}")
            
    if not issues:
        print("\nNo issues found! All dataSources have exactly 1 <cmDataSource> and 1 <schema>.")
        
    return issues


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate Model XML files.")
    parser.add_argument("--input-dir", default=r"C:\Users\kcleary\Dev\migration_utils_cognos\input", help="Path to the input directory containing XML files.")
    parser.add_argument("--check-datasources", action="store_true", help="Validate dataSources elements.")
    parser.add_argument("--check-querysubjects", action="store_true", help="Validate querySubject elements.")
    
    args = parser.parse_args()
    if args.check_datasources:
        validate_data_sources(args.input_dir)
    if args.check_querysubjects:
        check_xml_files(args.input_dir)
    if not args.check_datasources and not args.check_querysubjects:
        validate_data_sources(args.input_dir)
        check_xml_files(args.input_dir)
