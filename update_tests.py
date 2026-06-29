import re

def update_file():
    with open('test/test_extract_tables.py', 'r') as f:
        content = f.read()

    # We need to replace the XML in combined_all_elements and other places to add cmDataSource
    content = content.replace('<name>PROD.BANINST1</name>', '<name>PROD.BANINST1</name>\n                    <cmDataSource>PROD</cmDataSource>')
    content = content.replace('<name>PROD.PAYROLL</name>', '<name>PROD.PAYROLL</name>\n                    <cmDataSource>PROD</cmDataSource>')

    # Update ds_maps
    content = content.replace('{"PROD.BANINST1": "BANINST1"}', '{"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}}')
    content = content.replace('{"PROD.PAYROLL": "PAYROLL"}', '{"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}}')
    content = content.replace('{"PROD.BANINST1": "BANINST1", "PROD.PAYROLL": "PAYROLL"}', '{"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}, "PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}}')

    # Update expected_table_refs logic
    replacements = {
        '{"BANINST1.AP_DEDUCTIONS_BENEFITS"}': '{("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")}',
        '{"PAYROLL.NATIVE_TABLE"}': '{("NATIVE_TABLE", "", "PAYROLL")}',
        '{"PAYROLL.PAYROLL_TABLE"}': '{("PAYROLL_TABLE", "PROD", "PAYROLL")}',
        '{"[PROD.GENERAL].GENERAL_TABLE"}': '{("GENERAL_TABLE", "", "PROD.GENERAL")}',
        '{"[UNKNOWN_DS].MY_TABLE"}': '{("MY_TABLE", "", "UNKNOWN_DS")}',
        '{"[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS"}': '{("AP_DEDUCTIONS_BENEFITS", "", "PROD.BANINST1")}',
        '{"JUST_TABLE"}': '{("JUST_TABLE", "", "")}',
        '{"BANINST1.TABLE1"}': '{("TABLE1", "PROD", "BANINST1")}',
        '{"BANINST1.[BRACKETED_TABLE]"}': '{("BRACKETED_TABLE", "PROD", "BANINST1")}',
        '{"[PROD.BANINST1].[BRACKETED_TABLE]"}': '{("BRACKETED_TABLE", "", "PROD.BANINST1")}',
        '{"SCHEMA.TABLE"}': '{("TABLE", "", "SCHEMA")}',
        '{"[PAYROLL].TABLE"}': '{("TABLE", "", "PAYROLL")}',
        '{"GENERAL.GOBTPAC"}': '{("GOBTPAC", "", "GENERAL")}',
        '{"SHOULD_BE_EXTRACTED"}': '{("SHOULD_BE_EXTRACTED", "", "")}',
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    combined_set = '''{
            ("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1"),
            ("NATIVE_TABLE", "", "PAYROLL"),
            ("PAYROLL_TABLE", "PROD", "PAYROLL"),
            ("GENERAL_TABLE", "", "PROD.GENERAL"),
            ("MY_TABLE", "", "UNKNOWN_DS"),
            ("AP_DEDUCTIONS_BENEFITS", "", "PROD.BANINST1"),
            ("JUST_TABLE", "", ""),
            ("TABLE1", "PROD", "BANINST1"),
            ("BRACKETED_TABLE", "PROD", "BANINST1"),
            ("BRACKETED_TABLE", "", "PROD.BANINST1"),
            ("TABLE", "", "SCHEMA"),
            ("TABLE", "", "PAYROLL"),
        }'''
    
    # We replace the large set manually
    # Find the block after {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}, "PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
    content = re.sub(
        r'\{\s*"BANINST1\.AP_DEDUCTIONS_BENEFITS",.*?\}\,',
        combined_set + ',',
        content,
        flags=re.DOTALL
    )

    # Insert new tests at the end of TEST_CASES
    new_tests = """
    (
        "fallback_to_datasource_ref",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.HR</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>HR</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.HR]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>EMPLOYEES</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.HR": {"cmDataSource": "PROD", "schema": "HR"}},
        {("EMPLOYEES", "PROD", "HR")},
    ),
    (
        "fallback_multiple_options",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.HR</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>HR</schema>
                </dataSource>
                <dataSource>
                    <name>TEST.HR</name>
                    <cmDataSource>TEST</cmDataSource>
                    <schema>HR</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.HR]</dataSourceRef>
                                <dataSourceRef>[].[dataSources].[TEST.HR]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>EMPLOYEES</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {
            "PROD.HR": {"cmDataSource": "PROD", "schema": "HR"},
            "TEST.HR": {"cmDataSource": "TEST", "schema": "HR"},
        },
        {("EMPLOYEES", "MultipleOptions", "MultipleOptions")},
    ),
]"""
    content = content.replace("    ),\n]", "    ),\n" + new_tests)

    with open('test/test_extract_tables.py', 'w') as f:
        f.write(content)

if __name__ == '__main__':
    update_file()
