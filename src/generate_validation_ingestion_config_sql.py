import os
import argparse
import glob


def generate_sql_for_tables(input_txt, output_file):
    with open(input_txt, "r", encoding="utf-8") as f:
        tables = [line.strip() for line in f if line.strip()]

    # Deduplicate and uppercase
    unique_objects = set()
    for t in tables:
        parts = t.split(".")
        if len(parts) == 2:
            unique_objects.add((parts[0].upper(), parts[1].upper()))

    sorted_objects = sorted(list(unique_objects))
    if not sorted_objects:
        print(f"No valid tables found in {input_txt}")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("WITH expected_objects AS (\n")

        for i, (owner, obj) in enumerate(sorted_objects):
            if i == 0:
                f.write(
                    f"    SELECT '{owner}' AS expected_owner, '{obj}' AS expected_object FROM dual\n"
                )
            else:
                f.write(f"    UNION ALL SELECT '{owner}', '{obj}' FROM dual\n")

        f.write("),\n")
        f.write("object_columns AS (\n")
        f.write("    SELECT owner, table_name,\n")
        f.write(
            "           COALESCE(MAX(CASE WHEN column_name = table_name || '_ACTIVITY_DATE' THEN column_name ELSE NULL END),\n"
        )
        f.write(
            "                    MAX(CASE WHEN column_name LIKE '%_ACTIVITY_DATE' THEN column_name ELSE NULL END)) AS activity_date_column,\n"
        )
        f.write(
            "           COALESCE(MAX(CASE WHEN column_name = table_name || '_SURROGATE_ID' THEN column_name ELSE NULL END),\n"
        )
        f.write(
            "                    MAX(CASE WHEN column_name LIKE '%_SURROGATE_ID' THEN column_name ELSE NULL END)) AS surrogate_id_column\n"
        )
        f.write("    FROM all_tab_columns\n")
        f.write("    GROUP BY owner, table_name\n")
        f.write("),\n")
        f.write("object_pks AS (\n")
        f.write("    SELECT \n")
        f.write("        c.owner,\n")
        f.write("        c.table_name,\n")
        f.write(
            "        LISTAGG(cc.column_name, ',') WITHIN GROUP (ORDER BY cc.position) AS pk_columns\n"
        )
        f.write("    FROM all_constraints c\n")
        f.write("    JOIN all_cons_columns cc \n")
        f.write("        ON c.owner = cc.owner \n")
        f.write("        AND c.constraint_name = cc.constraint_name\n")
        f.write("    WHERE c.constraint_type = 'P'\n")
        f.write("    GROUP BY c.owner, c.table_name\n")
        f.write("),\n")
        f.write("alt_date_cols AS (\n")
        f.write("    SELECT owner, table_name,\n")
        f.write(
            "           LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) AS alt_activity_date_cols\n"
        )
        f.write("    FROM all_tab_columns\n")
        f.write("    WHERE (data_type LIKE '%DATE%' OR data_type LIKE '%TIMESTAMP%')\n")
        f.write(
            "      AND (column_name LIKE '%UPDATED%' OR column_name LIKE '%MODIFIED%')\n"
        )
        f.write("    GROUP BY owner, table_name\n")
        f.write("),\n")
        f.write("partition_cols AS (\n")
        f.write("    SELECT owner, table_name,\n")
        f.write(
            "           LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) AS potential_partition_cols\n"
        )
        f.write("    FROM all_tab_columns\n")
        f.write("    WHERE column_name LIKE '%_TERM%'\n")
        f.write("       OR column_name LIKE '%ACAD%PER'\n")
        f.write("    GROUP BY owner, table_name\n")
        f.write("),\n")
        f.write("object_summary AS (\n")
        f.write("    SELECT \n")
        f.write("        e.expected_owner, \n")
        f.write("        e.expected_object, \n")
        f.write(
            "        CASE WHEN a.object_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END AS table_status,\n"
        )
        f.write("        c.activity_date_column,\n")
        f.write("        c.surrogate_id_column,\n")
        f.write("        pk.pk_columns,\n")
        f.write("        adc.alt_activity_date_cols,\n")
        f.write("        pc.potential_partition_cols,\n")
        f.write("        t.num_rows AS estimated_row_count\n")
        f.write("    FROM expected_objects e\n")
        f.write("    LEFT JOIN all_objects a \n")
        f.write("        ON e.expected_owner = a.owner \n")
        f.write("       AND e.expected_object = a.object_name\n")
        f.write("    LEFT JOIN object_columns c\n")
        f.write("        ON e.expected_owner = c.owner \n")
        f.write("       AND e.expected_object = c.table_name\n")
        f.write("    LEFT JOIN object_pks pk\n")
        f.write("        ON e.expected_owner = pk.owner \n")
        f.write("       AND e.expected_object = pk.table_name\n")
        f.write("    LEFT JOIN all_tables t\n")
        f.write("        ON e.expected_owner = t.owner \n")
        f.write("       AND e.expected_object = t.table_name\n")
        f.write("    LEFT JOIN alt_date_cols adc\n")
        f.write("        ON e.expected_owner = adc.owner \n")
        f.write("       AND e.expected_object = adc.table_name\n")
        f.write("    LEFT JOIN partition_cols pc\n")
        f.write("        ON e.expected_owner = pc.owner \n")
        f.write("       AND e.expected_object = pc.table_name\n")
        f.write(")\n")
        f.write("SELECT \n")
        f.write("    expected_owner AS owner,\n")
        f.write("    expected_object AS object_name,\n")
        f.write("    table_status,\n")
        f.write("    estimated_row_count,\n")
        f.write(
            "    COALESCE(surrogate_id_column, pk_columns) AS ingestion_pk_columns,\n"
        )
        f.write(
            "    COALESCE(activity_date_column, alt_activity_date_cols) AS ingestion_date_columns,\n"
        )
        f.write("    potential_partition_cols,\n")
        f.write("    CASE \n")
        f.write("        WHEN COALESCE(surrogate_id_column, pk_columns) IS NOT NULL \n")
        f.write(
            "         AND COALESCE(activity_date_column, alt_activity_date_cols) IS NOT NULL \n"
        )
        f.write("        THEN 'date_incremental'\n")
        f.write(
            "        WHEN potential_partition_cols IS NOT NULL AND (estimated_row_count > 100000 OR estimated_row_count IS NULL) \n"
        )
        f.write("        THEN 'column_incremental'\n")
        f.write("        ELSE 'full_load'\n")
        f.write("    END AS ingestion_type\n")
        f.write("FROM object_summary\n")
        f.write("ORDER BY table_status, owner, object_name;\n")

    print(f"  -> Created validation script: {output_file}")
    print(f"  -> Total unique objects to validate: {len(sorted_objects)}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate validation and ingestion config SQL."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=None,
        help="Path to the original XML file. Defaults to input/fm_model.xml in the project root.",
    )
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if args.input_file:
        file_path = args.input_file
    else:
        file_path = os.path.join(project_root, "input", "fm_model.xml")

    input_filename = os.path.splitext(os.path.basename(file_path))[0]
    output_dir = os.path.join(project_root, "output", input_filename)
    os.makedirs(output_dir, exist_ok=True)

    input_files = glob.glob(os.path.join(output_dir, "resolved_tables_*.txt"))

    if not input_files:
        old_txt = os.path.join(output_dir, "resolved_tables.txt")
        if os.path.exists(old_txt):
            input_files = [old_txt]
        else:
            print(f"Error: No resolved_tables*.txt found in {output_dir}.")
            return

    for input_txt in input_files:
        basename = os.path.basename(input_txt)
        if basename.startswith("resolved_tables_") and basename.endswith(".txt"):
            suffix = basename[len("resolved_tables_") : -4]
            output_file = os.path.join(
                output_dir, f"table_validation_ingestion_config_{suffix}.sql"
            )
        else:
            output_file = os.path.join(
                output_dir, "table_validation_ingestion_config.sql"
            )

        print(f"\nProcessing {basename}...")
        generate_sql_for_tables(input_txt, output_file)


if __name__ == "__main__":
    main()
