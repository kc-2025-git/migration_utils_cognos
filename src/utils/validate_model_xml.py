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
                    # Check if it's a modelQuery and ignore it
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
                    
                    name = "Unknown"
                    for child in elem:
                        if child.tag.split('}')[-1] == 'name':
                            name = child.text
                            break
                            
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

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate Model XML files for multiple sources/dataSourceRefs.")
    parser.add_argument("--input-dir", default=r"C:\Users\kcleary\Dev\migration_utils_cognos\input", help="Path to the input directory containing XML files.")
    
    args = parser.parse_args()
    check_xml_files(args.input_dir)
