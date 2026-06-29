import pytest
import sys
import os

# Add the src directory to the path so we can import from it
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from extract_tables_from_project import extract_from_xml_string

TEST_CASES = [
    (
        "cognos_sql_with_table_elements",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD.BANINST1": "BANINST1"},
        {"BANINST1.AP_DEDUCTIONS_BENEFITS"},
    ),
    (
        "native_sql_without_table_elements",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from PAYROLL.NATIVE_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"PAYROLL.NATIVE_TABLE"},
    ),
    (
        "cognos_sql_without_table_elements",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select A, B from [PROD.PAYROLL].PAYROLL_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD.PAYROLL": "PAYROLL"},
        {"PAYROLL.PAYROLL_TABLE"},
    ),
    (
        "db_object_name",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <dbObjectName>[PROD.GENERAL].GENERAL_TABLE</dbObjectName>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"[PROD.GENERAL].GENERAL_TABLE"},
    ),
    (
        "cognos_sql_unmatched_datasource",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [UNKNOWN_DS].MY_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"[UNKNOWN_DS].MY_TABLE"},
    ),
    (
        "native_sql_with_brackets",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS"},
    ),
    (
        "sql_without_schema_prefix",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>JUST_TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"JUST_TABLE"},
    ),
    (
        "casing_and_deduplication",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[prod.baninst1].table1</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [PROD.BANINST1].TABLE1</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD.BANINST1": "BANINST1"},
        {"BANINST1.TABLE1"},
    ),
    (
        "bracketed_table_name_cognos_match",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <schema>BANINST1</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD.BANINST1": "BANINST1"},
        {"BANINST1.[BRACKETED_TABLE]"},
    ),
    (
        "bracketed_table_name_native",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"[PROD.BANINST1].[BRACKETED_TABLE]"},
    ),
    (
        "native_three_part_identifier",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from SERVER.SCHEMA.TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"SCHEMA.TABLE"},
    ),
    (
        "cognos_three_part_identifier_invalid",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [PROD].[PAYROLL].TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"[PAYROLL].TABLE"},
    ),
    (
        "three_part_in_table_tag",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>SERVER.SCHEMA.TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"SCHEMA.TABLE"},
    ),
    (
        "unqualified_deduplication",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from GENERAL.GOBTPAC</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from GOBTPAC</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {},
        {"GENERAL.GOBTPAC"},
    ),
    (
        "combined_all_elements",
        """
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.BANINST1</name>
                    <schema>BANINST1</schema>
                </dataSource>
                <dataSource>
                    <name>PROD.PAYROLL</name>
                    <schema>PAYROLL</schema>
                </dataSource>
            </dataSources>
            <namespace>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from PAYROLL.NATIVE_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select A, B from [PROD.PAYROLL].PAYROLL_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <dbObjectName>[PROD.GENERAL].GENERAL_TABLE</dbObjectName>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [UNKNOWN_DS].MY_TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>JUST_TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[prod.baninst1].table1</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [PROD.BANINST1].TABLE1</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>[PROD.BANINST1].[BRACKETED_TABLE]</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from SERVER.SCHEMA.TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="cognos">Select * from [PROD].[PAYROLL].TABLE</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from <table>SERVER.SCHEMA.TABLE</table></sql>
                        </dbQuery>
                    </definition>
                </querySubject>
                <querySubject status="valid">
                    <definition>
                        <dbQuery>
                            <sql type="native">Select * from TABLE1</sql>
                        </dbQuery>
                    </definition>
                </querySubject>
            </namespace>
        </project>
        """,
        {"PROD.BANINST1": "BANINST1", "PROD.PAYROLL": "PAYROLL"},
        {
            "BANINST1.AP_DEDUCTIONS_BENEFITS",
            "PAYROLL.NATIVE_TABLE",
            "PAYROLL.PAYROLL_TABLE",
            "[PROD.GENERAL].GENERAL_TABLE",
            "[UNKNOWN_DS].MY_TABLE",
            "[PROD.BANINST1].AP_DEDUCTIONS_BENEFITS",
            "JUST_TABLE",
            "BANINST1.TABLE1",
            "BANINST1.[BRACKETED_TABLE]",
            "[PROD.BANINST1].[BRACKETED_TABLE]",
            "SCHEMA.TABLE",
            "[PAYROLL].TABLE",
        },
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
