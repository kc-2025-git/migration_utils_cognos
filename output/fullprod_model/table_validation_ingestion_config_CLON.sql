WITH expected_objects AS (
    SELECT 'ALUMNI' AS expected_owner, 'ADBDESG' AS expected_object FROM dual
    UNION ALL SELECT 'ALUMNI', 'AGBPLDG' FROM dual
    UNION ALL SELECT 'ALUMNI', 'AGRPDES' FROM dual
    UNION ALL SELECT 'FIMSMGR', 'FTVVEND' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRADDR' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRIDEN' FROM dual
),
object_columns AS (
    SELECT owner, table_name,
           COALESCE(MAX(CASE WHEN column_name = table_name || '_ACTIVITY_DATE' THEN column_name ELSE NULL END),
                    MAX(CASE WHEN column_name LIKE '%_ACTIVITY_DATE' THEN column_name ELSE NULL END)) AS activity_date_column,
           COALESCE(MAX(CASE WHEN column_name = table_name || '_SURROGATE_ID' THEN column_name ELSE NULL END),
                    MAX(CASE WHEN column_name LIKE '%_SURROGATE_ID' THEN column_name ELSE NULL END)) AS surrogate_id_column
    FROM all_tab_columns
    GROUP BY owner, table_name
),
object_pks AS (
    SELECT 
        c.owner,
        c.table_name,
        LISTAGG(cc.column_name, ',') WITHIN GROUP (ORDER BY cc.position) AS pk_columns
    FROM all_constraints c
    JOIN all_cons_columns cc 
        ON c.owner = cc.owner 
        AND c.constraint_name = cc.constraint_name
    WHERE c.constraint_type = 'P'
    GROUP BY c.owner, c.table_name
),
alt_date_cols AS (
    SELECT owner, table_name,
           LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) AS alt_activity_date_cols
    FROM all_tab_columns
    WHERE (data_type LIKE '%DATE%' OR data_type LIKE '%TIMESTAMP%')
      AND (column_name LIKE '%UPDATED%' OR column_name LIKE '%MODIFIED%')
    GROUP BY owner, table_name
),
partition_cols AS (
    SELECT owner, table_name,
           LISTAGG(column_name, ',') WITHIN GROUP (ORDER BY column_name) AS potential_partition_cols
    FROM all_tab_columns
    WHERE column_name LIKE '%_TERM%'
       OR column_name LIKE '%ACAD%PER'
    GROUP BY owner, table_name
),
object_summary AS (
    SELECT 
        e.expected_owner, 
        e.expected_object, 
        CASE WHEN a.object_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END AS table_status,
        c.activity_date_column,
        c.surrogate_id_column,
        pk.pk_columns,
        adc.alt_activity_date_cols,
        pc.potential_partition_cols,
        t.num_rows AS estimated_row_count
    FROM expected_objects e
    LEFT JOIN all_objects a 
        ON e.expected_owner = a.owner 
       AND e.expected_object = a.object_name
    LEFT JOIN object_columns c
        ON e.expected_owner = c.owner 
       AND e.expected_object = c.table_name
    LEFT JOIN object_pks pk
        ON e.expected_owner = pk.owner 
       AND e.expected_object = pk.table_name
    LEFT JOIN all_tables t
        ON e.expected_owner = t.owner 
       AND e.expected_object = t.table_name
    LEFT JOIN alt_date_cols adc
        ON e.expected_owner = adc.owner 
       AND e.expected_object = adc.table_name
    LEFT JOIN partition_cols pc
        ON e.expected_owner = pc.owner 
       AND e.expected_object = pc.table_name
)
SELECT 
    expected_owner AS owner,
    expected_object AS object_name,
    table_status,
    estimated_row_count,
    COALESCE(surrogate_id_column, pk_columns) AS ingestion_pk_columns,
    COALESCE(activity_date_column, alt_activity_date_cols) AS ingestion_date_columns,
    potential_partition_cols,
    CASE 
        WHEN COALESCE(surrogate_id_column, pk_columns) IS NOT NULL 
         AND COALESCE(activity_date_column, alt_activity_date_cols) IS NOT NULL 
        THEN 'date_incremental'
        WHEN potential_partition_cols IS NOT NULL AND (estimated_row_count > 100000 OR estimated_row_count IS NULL) 
        THEN 'column_incremental'
        ELSE 'full_load'
    END AS ingestion_type
FROM object_summary
ORDER BY table_status, owner, object_name;
