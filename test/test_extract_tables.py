import pytest
import sys
import os

# Add the src directory to the path so we can import from it
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from extract_tables_from_project import extract_from_xml_string, extract_tables_from_sql

TEST_CASES = [
    (
        "cognos_sql_with_table_elements",
        """
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
        """,
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")},
    ),
    (
        "cognos_sql_with_table_elements_diff_names",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PREFIX.SUFFIX</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PREFIX.SUFFIX]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select * from <table>[PREFIX.SUFFIX].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PREFIX.SUFFIX": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")},
    ),
    (
        "native_sql_without_table_elements",
        """
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
        """,
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("NATIVE_TABLE", "PROD", "PAYROLL")},
    ),
    (
        "cognos_sql_without_table_elements",
        """
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
        """,
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("PAYROLL_TABLE", "PROD", "PAYROLL")},
    ),
    (
        "cognos_sql_without_table_elements_diff_names",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PREFIX.SUFFIX</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PREFIX.SUFFIX]</dataSourceRef>
                            </sources>
                            <sql type="cognos">Select A, B from [PREFIX.SUFFIX].PAYROLL_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PREFIX.SUFFIX": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("PAYROLL_TABLE", "PROD", "PAYROLL")},
    ),
    (
        "db_object_name",
        """
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
        """,
        {"PROD.GENERAL": {"cmDataSource": "PROD", "schema": "GENERAL"}},
        {("GENERAL_TABLE", "PROD", "GENERAL")},
    ),
    (
        "cognos_sql_unmatched_datasource",
        """
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
        """,
        {},
        {("MY_TABLE", "", "UNKNOWN_DS")},
    ),
    (
        "native_sql_with_brackets",
        """
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
        """,
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("AP_DEDUCTIONS_BENEFITS", "PROD", "BANINST1")},
    ),
    (
        "sql_without_schema_prefix",
        """
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
        """,
        {"PROD.HR": {"cmDataSource": "PROD", "schema": "HR"}},
        {("JUST_TABLE", "PROD", "HR")},
    ),
    (
        "casing_and_deduplication",
        """
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
        """,
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("TABLE1", "PROD", "BANINST1")},
    ),
    (
        "bracketed_table_name_cognos_match",
        """
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
        """,
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("BRACKETED_TABLE", "PROD", "BANINST1")},
    ),
    (
        "bracketed_table_name_native",
        """
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
        """,
        {"PROD.BANINST1": {"cmDataSource": "PROD", "schema": "BANINST1"}},
        {("BRACKETED_TABLE", "PROD", "BANINST1")},
    ),
    (
        "native_three_part_identifier",
        """
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
        """,
        {"SERVER.SCHEMA": {"cmDataSource": "SERVER", "schema": "SCHEMA"}},
        {("TABLE", "SERVER", "SCHEMA")},
    ),
    (
        "cognos_three_part_identifier_invalid",
        """
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
        """,
        {"PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"}},
        {("TABLE", "PROD", "PAYROLL")},
    ),
    (
        "three_part_in_table_tag",
        """
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
        """,
        {"SERVER.SCHEMA": {"cmDataSource": "SERVER", "schema": "SCHEMA"}},
        {("TABLE", "SERVER", "SCHEMA")},
    ),
    (
        "unqualified_deduplication",
        """
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
        """,
        {"GENERAL": {"cmDataSource": "PROD", "schema": "GENERAL"}},
        {("GOBTPAC", "PROD", "GENERAL")},
    ),
    (
        "skip_model_query",
        """
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
        """,
        {},
        {("SHOULD_BE_EXTRACTED", "", "SOME_DS")},
    ),
    (
        "multiple_refs_same_cm_ds",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
                <dataSource>
                    <name>PROD.SATURN</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>SATURN</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                                <dataSourceRef>[].[dataSources].[PROD.SATURN]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>PEBEMPL</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {
            "PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"},
            "PROD.SATURN": {"cmDataSource": "PROD", "schema": "SATURN"},
        },
        {("PEBEMPL", "PROD", "")},
    ),
    (
        "multiple_refs_diff_cm_ds",
        """
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
        """,
        {
            "PROD.HR": {"cmDataSource": "PROD", "schema": "HR"},
            "TEST.HR": {"cmDataSource": "TEST", "schema": "HR"},
        },
        {("EMPLOYEES", "MultipleOptions", "")},
    ),
    (
        "deduplicate_blank_schema_when_schema_exists",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>PAYROLL</schema>
                </dataSource>
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
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>SPRIDEN</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD.PAYROLL]</dataSourceRef>
                                <dataSourceRef>[].[dataSources].[PROD.GENERAL]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from <table>SPRIDEN</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {
            "PROD.PAYROLL": {"cmDataSource": "PROD", "schema": "PAYROLL"},
            "PROD.GENERAL": {"cmDataSource": "PROD", "schema": "GENERAL"},
        },
        {("SPRIDEN", "PROD", "PAYROLL")},
    ),
    (
        "explicit_schema_in_sql_overridden_by_datasource",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>BWRMGR</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sources>
                                <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                            </sources>
                            <sql type="native">Select * from SATURN.SPRIDEN</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD": {"cmDataSource": "PROD", "schema": "BWRMGR"}},
        {("SPRIDEN", "PROD", "SATURN")},
    ),
]


@pytest.mark.parametrize(
    "test_name, xml_string, expected_ds_map, expected_table_refs", TEST_CASES
)
def test_extract_tables(test_name, xml_string, expected_ds_map, expected_table_refs):
    # Arrange
    # (inputs are provided via test parameters)

    # Act
    ds_map, _, table_refs = extract_from_xml_string(xml_string)

    # Assert
    assert ds_map == expected_ds_map
    assert table_refs == expected_table_refs


@pytest.mark.parametrize(
    "sql_content, expected_deps",
    [
        ("SELECT * FROM MY_TABLE", {"MY_TABLE"}),
        (
            "SELECT * FROM FIRST_TABLE T1 JOIN SECOND_TABLE T2 ON T1.ID = T2.ID",
            {"FIRST_TABLE", "SECOND_TABLE"},
        ),
        ("WITH cte AS (SELECT * FROM source_tbl) SELECT * FROM cte", {"source_tbl"}),
        ("SELECT max(val), substr(text, 1, 5) FROM DUAL", {"DUAL"}),
        ("SELECT custom_func(id) FROM base_tbl", {"base_tbl"}),
        ("SELECT myschema.mytable.col FROM myschema.mytable", {"myschema.mytable"}),
        (
            "SELECT 'FROM NOT_A_TABLE' AS string_col FROM the_real_table",
            {"the_real_table"},
        ),
        (
            "-- FROM hidden_table\nSELECT * FROM visible_table /* FROM other_hidden */",
            {"visible_table"},
        ),
        (
            "SELECT a.col, b.col FROM table_a a, table_b b WHERE a.id = b.id",
            {"table_a", "table_b"},
        ),
        ("select * from my_funct()", set()),
        ("select * from table(my_pkg.my_funct())", set()),
        (
            "SELECT NVL(T2.COLUMN_A, 'DELETED') FROM TABLE_A T1, TABLE_B T2 WHERE T1.ID = T2.ID",
            {"TABLE_A", "TABLE_B"},
        ),
    ],
)
def test_extract_tables_from_sql_edge_cases(
    sql_content: str, expected_deps: set
) -> None:
    """Test that SQL parsing correctly identifies various dependency types."""
    # Act
    extracted = extract_tables_from_sql(sql_content)

    # Assert
    assert extracted == expected_deps
