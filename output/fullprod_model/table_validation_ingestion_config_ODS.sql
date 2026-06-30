WITH expected_objects AS (
    SELECT 'ODSMGR' AS expected_owner, 'ACADEMIC_STUDY' AS expected_object FROM dual
    UNION ALL SELECT 'ODSMGR', 'EMPLOYEE' FROM dual
    UNION ALL SELECT 'ODSMGR', 'EMPLOYEE_POSITION' FROM dual
    UNION ALL SELECT 'ODSMGR', 'MEETING_TIME' FROM dual
    UNION ALL SELECT 'ODSMGR', 'PERSON_DETAIL' FROM dual
    UNION ALL SELECT 'ODSMGR', 'ROOM_ASSIGNMENT' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_HR_EMPLOYEE' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_HR_EMP_POSITION' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_LENEL_CUSTOM' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_MST_SFRSTCA' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_MST_SORRTRM' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_MST_SPRADDR' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_MST_STVNATN' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_SCADLOC_CONTRACT_FACULTY' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_SCADLOC_CONTRACT_TYPE' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_SCADLOC_CONTRACT_YEAR' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCAD_SF_CONTACT' FROM dual
    UNION ALL SELECT 'ODSMGR', 'SCHEDULE_OFFERING' FROM dual
    UNION ALL SELECT 'ODSMGR', 'STUDENT_COURSE' FROM dual
    UNION ALL SELECT 'SATURN', 'STVSTAT' FROM dual
    UNION ALL SELECT 'SATURN', 'STVTERM' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'FACULTY_SPECIAL_CONTRACTS' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'FACULTY_SPECIAL_REDUCED_NEW' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'FSC_CAPTAIN_STEP3' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'HR_FAC_MANUAL_UPDATES_CY' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'HR_FAC_YRS_RED_FORMAT' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'HR_GRADE_FAC_CY' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'HR_GRADE_FAC_DEPT_CY' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'HR_GRADE_STAFF' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'EDU' FROM dual
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
