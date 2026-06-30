WITH expected_objects AS (
    SELECT 'BANINST1' AS expected_owner, 'WGVEDUC' AS expected_object FROM dual
    UNION ALL SELECT 'FIMSMGR', 'FTVACTV' FROM dual
    UNION ALL SELECT 'FIMSMGR', 'FTVORGN' FROM dual
    UNION ALL SELECT 'GENERAL', 'GOBEACC' FROM dual
    UNION ALL SELECT 'GENERAL', 'GOBINTL' FROM dual
    UNION ALL SELECT 'GENERAL', 'GOBTPAC' FROM dual
    UNION ALL SELECT 'GENERAL', 'GOREMAL' FROM dual
    UNION ALL SELECT 'GENERAL', 'GORPRAC' FROM dual
    UNION ALL SELECT 'GENERAL', 'GORRACE' FROM dual
    UNION ALL SELECT 'GENERAL', 'GORVISA' FROM dual
    UNION ALL SELECT 'GENERAL', 'GTVRRAC' FROM dual
    UNION ALL SELECT 'GENERAL', 'GXRDIRD' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PDRBCOV' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PDRBDED' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PDRBENE' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PDRDEDN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PDRXPID' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PEBEMPL' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERDAYH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERDAYS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERDHIS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERDIRD' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERDTOT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PEREARH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PEREARN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PEREHIS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERELBD' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERELBH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERETOT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERHOUH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERHOUR' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERJHIS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERJOBH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERJOBS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERJTOT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERLEAV' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERLHIS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERLVTK' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERROUH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERROUT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERTETH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERTITH' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PERTITO' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRACCR' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRBKTP' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRDEDN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRDOCM' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHREARN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRELBD' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRFLSA' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRHIST' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRHOUR' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PHRJOBS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PPRCCMT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PPRCMNT' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRBDCA' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRBDPL' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRCALN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTREARN' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRECLS' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTREMPR' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRERST' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRJCRE' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRLEAV' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRLVAC' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRTREA' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTRUSER' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTVCMTY' FROM dual
    UNION ALL SELECT 'PAYROLL', 'PTVLCAT' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBBFISC' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBBPOSN' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRBJOB' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBREARN' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRJFTE' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRJLBD' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRJOBS' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRPLBD' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NBRPTOT' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NOBTRAN' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NORROUT' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NORTRAN' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRACAT' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRALVL' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRAUBK' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRAUFM' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRPCLS' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRPRXY' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTRSALB' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTVACAT' FROM dual
    UNION ALL SELECT 'POSNCTL', 'NTVAPTY' FROM dual
    UNION ALL SELECT 'SATURN', 'SFRSTCR' FROM dual
    UNION ALL SELECT 'SATURN', 'SHRDGMR' FROM dual
    UNION ALL SELECT 'SATURN', 'SIBINST' FROM dual
    UNION ALL SELECT 'SATURN', 'SORDEGR' FROM dual
    UNION ALL SELECT 'SATURN', 'SPBPERS' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRADDR' FROM dual
    UNION ALL SELECT 'SATURN', 'SPREMRG' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRIDEN' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRINTL' FROM dual
    UNION ALL SELECT 'SATURN', 'SPRTELE' FROM dual
    UNION ALL SELECT 'SATURN', 'STVACYR' FROM dual
    UNION ALL SELECT 'SATURN', 'STVCOLL' FROM dual
    UNION ALL SELECT 'SATURN', 'STVETHN' FROM dual
    UNION ALL SELECT 'SATURN', 'STVNATN' FROM dual
    UNION ALL SELECT 'SATURN', 'STVRSTS' FROM dual
    UNION ALL SELECT 'SATURN', 'STVTERM' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'OEEMPLUS1' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'ORG_VP_SCH' FROM dual
    UNION ALL SELECT 'SCADLOCAL', 'WGBMSCAD' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_DEDUCTIONS_BENEFITS' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_EMPLOYEE_PROFILE' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_EMPLOYMENT_VERIFICATION' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_EMPLOY_RECRUITMENT_ACTIVITY' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_JOB_SUMMARY' FROM dual
    UNION ALL SELECT 'UNRESOLVED', 'AP_SALARY_BUDGET' FROM dual
),
object_columns AS (
    SELECT owner, table_name,
           MAX(CASE WHEN column_name = table_name || '_ACTIVITY_DATE' THEN 1 ELSE 0 END) AS has_activity_date,
           MAX(CASE WHEN column_name = table_name || '_SURROGATE_ID' THEN 1 ELSE 0 END) AS has_surrogate_id
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
    WHERE column_name LIKE '%TERM%'
    GROUP BY owner, table_name
),
object_summary AS (
    SELECT 
        e.expected_owner, 
        e.expected_object, 
        CASE WHEN a.object_name IS NOT NULL THEN 'EXISTS' ELSE 'MISSING' END AS table_status,
        CASE WHEN c.has_activity_date = 1 THEN e.expected_object || '_ACTIVITY_DATE' ELSE NULL END AS activity_date_column,
        CASE WHEN c.has_surrogate_id = 1 THEN e.expected_object || '_SURROGATE_ID' ELSE NULL END AS surrogate_id_column,
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
        WHEN potential_partition_cols IS NOT NULL AND estimated_row_count > 10000 
        THEN 'column_incremental'
        ELSE 'full_load'
    END AS ingestion_type
FROM object_summary
ORDER BY table_status, owner, object_name;
