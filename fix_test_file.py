import os
import re

TEST_CASES = """TEST_CASES = [
    (
        "cognos_sql_with_table_elements",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")},
    ),
    (
        "native_sql_without_table_elements",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from PAYROLL.NATIVE_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("NATIVE_TABLE", "PROD", "PAYROLL")},
    ),
    (
        "cognos_sql_without_table_elements",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select A, B from [PROD.PAYROLL].PAYROLL_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("PAYROLL_TABLE", "PROD", "PAYROLL")},
    ),
    (
        "db_object_name",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.GENERAL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>GENERAL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.GENERAL]</dataSourceRef>
                            </sources>
                            <dbObjectName>[PROD.GENERAL].GENERAL_TABLE</dbObjectName>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.GENERAL": {"cmDataSource": "PROD", "schema": "GENERAL"}},
        {("GENERAL_TABLE", "PROD", "GENERAL")},
    ),
    (
        "cognos_sql_unmatched_datasource",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[UNKNOWN_DS]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from [UNKNOWN_DS].MY_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {},
        {("MY_TABLE", "", "UNKNOWN_DS")},
    ),
    (
        "native_sql_with_brackets",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")},
    ),
    (
        "sql_without_schema_prefix",
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
                            <sql type="cognos">Select * from <table>JUST_TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.HR": {"cmDataSource": "PROD", "schema": "HR"}},
        {("JUST_TABLE", "PROD", "HR")},
    ),
    (
        "casing_and_deduplication",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from <table>[prod.baninst1].table1</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from [PROD.BANINST1].TABLE1</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("TABLE1", "PROD", "BANINST1")},
    ),
    (
        "bracketed_table_name_cognos_match",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("BRACKETED_TABLE", "PROD", "BANINST1")},
    ),
    (
        "bracketed_table_name_native",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.BANINST1]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("BRACKETED_TABLE", "PROD", "BANINST1")},
    ),
    (
        "native_three_part_identifier",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>SERVER.SCHEMA</name>
                    <cmDataSource>SERVER</cmDataSource>
                    <schema>SCHEMA</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[SERVER.SCHEMA]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from SERVER.SCHEMA.TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"SERVER.SCHEMA": {"cmDataSource": "SERVER", "schema": "SCHEMA"}},
        {("TABLE", "SERVER", "SCHEMA")},
    ),
    (
        "cognos_three_part_identifier_invalid",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from [PROD].[PAYROLL].TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("TABLE", "PROD", "PAYROLL")},
    ),
    (
        "three_part_in_table_tag",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>SERVER.SCHEMA</name>
                    <cmDataSource>SERVER</cmDataSource>
                    <schema>SCHEMA</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[SERVER.SCHEMA]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>SERVER.SCHEMA.TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"SERVER.SCHEMA": {"cmDataSource": "SERVER", "schema": "SCHEMA"}},
        {("TABLE", "SERVER", "SCHEMA")},
    ),
    (
        "unqualified_deduplication",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>GENERAL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>GENERAL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[GENERAL]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from GENERAL.GOBTPAC</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[GENERAL]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from GOBTPAC</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {"GENERAL": {"cmDataSource": "PROD", "schema": "GENERAL"}},
        {("GOBTPAC", "PROD", "GENERAL")},
    ),
    (
        "skip_model_query",
        \"\"\"
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <modelQuery>
                            <sql type="cognos">Select * from <table>SHOULD_NOT_BE_EXTRACTED</table></sql>
                        </modelQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[SOME_DS]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from <table>SHOULD_BE_EXTRACTED</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        \"\"\",
        {},
        {("SHOULD_BE_EXTRACTED", "", "SOME_DS")},
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
]
"""

def apply():
    with open('test/test_extract_tables.py', 'r') as f:
        content = f.read()

    # Find the bounds of TEST_CASES
    start = content.find("TEST_CASES = [")
    
    # Find the first @pytest.mark.parametrize line
    end = content.find("@pytest.mark.parametrize(", start)
    
    # Replace
    new_content = content[:start] + TEST_CASES + "\n\n" + content[end:]
    
    with open('test/test_extract_tables.py', 'w') as f:
        f.write(new_content)

if __name__ == '__main__':
    apply()
