import pytest
import sys
import os

# Add the src directory to the path so we can import from it
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from utils.validate_model_xml import check_xml_files, validate_data_sources


@pytest.fixture
def temp_xml_dir(tmp_path):
    return tmp_path


@pytest.mark.parametrize(
    "xml_content, expected_issues",
    [
        (
            # Valid case: 1 querySubject, 1 sources, 1 dataSourceRef, has definition
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>ValidSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>

            </querySubject>
        </project>""",
            [],
        ),
        (
            # Invalid case: 1 querySubject, 0 sources
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>NoSourcesSubject</name>
                <definition>
                    <dbQuery>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "NoSourcesSubject",
                    "type": "invalid_sources_count",
                    "count": 0,
                }
            ],
        ),
        (
            # Invalid case: 1 querySubject, 1 sources, 0 dataSourceRef
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>NoRefSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "NoRefSubject",
                    "type": "invalid_dataSourceRefs_count",
                    "count": 0,
                }
            ],
        ),
        (
            # Invalid case: 1 querySubject, 2 sources
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MultipleSourcesSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                        </sources>
                        <sources>
                            <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "MultipleSourcesSubject",
                    "type": "invalid_sources_count",
                    "count": 2,
                }
            ],
        ),
        (
            # Valid case: 1 querySubject, 1 sources, 2 dataSourceRef
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MultipleRefsSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                            <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [],
        ),
        (
            # Invalid case: 1 querySubject, 2 sources (multiple dataSourceRefs is valid)
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>DoubleTroubleSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                            <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                        </sources>
                        <sources>
                            <dataSourceRef>[].[dataSources].[DEV]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "DoubleTroubleSubject",
                    "type": "invalid_sources_count",
                    "count": 2,
                },
            ],
        ),
        (
            # Valid case: 1 querySubject with dbQuery and nested sources
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>NestedSourcesSubject</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [],
        ),
        (
            # Valid case: modelQuery is ignored for sources validation
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>ModelQuerySubject</name>
                <definition>
                    <modelQuery>
                        <sql type="cognos"/>
                    </modelQuery>
                </definition>
            </querySubject>
        </project>""",
            [],
        ),
        (
            # Invalid case: missing definition
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MissingDefinitionSubject</name>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "MissingDefinitionSubject",
                    "type": "missing_definition",
                }
            ],
        ),
        (
            # Invalid case: missing dbQuery or modelQuery
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MissingQueryElementSubject</name>
                <definition>
                </definition>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "MissingQueryElementSubject",
                    "type": "missing_query_element",
                }
            ],
        ),
        (
            # Invalid case: missing sql inside dbQuery
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MissingSqlSubject</name>
                <definition>
                    <dbQuery>
                    </dbQuery>
                </definition>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "MissingSqlSubject",
                    "type": "missing_sql",
                }
            ],
        ),
        (
            # Invalid case: definition includes something other than dbQuery or modelQuery
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>OtherQuerySubject</name>
                <definition>
                    <someOtherQuery>
                        <sql>SELECT 1</sql>
                    </someOtherQuery>
                </definition>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "OtherQuerySubject",
                    "type": "missing_query_element",
                }
            ],
        ),
        (
            # Invalid case: querySubject without a name element (defaults to Unknown)
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <definition>
                    <dbQuery>
                    </dbQuery>
                </definition>
                <sources>
                </sources>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "Unknown",
                    "type": "missing_sql",
                },
                {
                    "querySubject": "Unknown",
                    "type": "invalid_dataSourceRefs_count",
                    "count": 0,
                },
            ],
        ),
        (
            # Valid and Invalid cases: Multiple querySubjects in the same file
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>ValidSubjectOne</name>
                <definition>
                    <dbQuery>
                        <sources>
                            <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                        </sources>
                        <sql>SELECT 1</sql>
                    </dbQuery>
                </definition>
            </querySubject>
            <querySubject>
                <name>InvalidSubjectTwo</name>
                <definition>
                    <dbQuery>
                        <sql>SELECT 2</sql>
                    </dbQuery>
                </definition>
            </querySubject>
        </project>""",
            [
                {
                    "querySubject": "InvalidSubjectTwo",
                    "type": "invalid_sources_count",
                    "count": 0,
                }
            ],
        ),
    ],
)
def test_check_xml_files(temp_xml_dir, xml_content, expected_issues):
    # Create the xml file in the temporary directory
    test_file = temp_xml_dir / "test_model.xml"
    test_file.write_text(xml_content, encoding="utf-8")

    # Run the function
    issues = check_xml_files(str(temp_xml_dir))

    # Assert number of issues matches
    assert len(issues) == len(expected_issues)

    # Sort issues to compare reliably
    issues.sort(key=lambda x: x["type"])
    expected_issues.sort(key=lambda x: x["type"])

    # Assert exact issue properties
    for actual, expected in zip(issues, expected_issues):
        assert actual["querySubject"] == expected["querySubject"]
        assert actual["type"] == expected["type"]
        assert actual.get("count") == expected.get("count")
        assert actual["file"] == "test_model.xml"


@pytest.mark.parametrize(
    "xml_content, expected_issues",
    [
        (
            # Valid case: 1 cmDataSource, 1 schema
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.ALUMNI</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>ALUMNI</schema>
                </dataSource>
            </dataSources>
        </project>""",
            [],
        ),
        (
            # Invalid case: 0 cmDataSource
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.ALUMNI</name>
                    <schema>ALUMNI</schema>
                </dataSource>
            </dataSources>
        </project>""",
            [
                {
                    "dataSource": "PROD.ALUMNI",
                    "type": "invalid_cmDataSource_count",
                    "count": 0,
                }
            ],
        ),
        (
            # Invalid case: 2 cmDataSource
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.ALUMNI</name>
                    <cmDataSource>PROD</cmDataSource>
                    <cmDataSource>TEST</cmDataSource>
                    <schema>ALUMNI</schema>
                </dataSource>
            </dataSources>
        </project>""",
            [
                {
                    "dataSource": "PROD.ALUMNI",
                    "type": "invalid_cmDataSource_count",
                    "count": 2,
                }
            ],
        ),
        (
            # Valid case: 0 schema
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.ALUMNI</name>
                    <cmDataSource>PROD</cmDataSource>
                </dataSource>
            </dataSources>
        </project>""",
            [],
        ),
        (
            # Invalid case: 2 schema
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <name>PROD.ALUMNI</name>
                    <cmDataSource>PROD</cmDataSource>
                    <schema>ALUMNI</schema>
                    <schema>OTHER</schema>
                </dataSource>
            </dataSources>
        </project>""",
            [
                {
                    "dataSource": "PROD.ALUMNI",
                    "type": "invalid_schema_count",
                    "count": 2,
                }
            ],
        ),
        (
            # Invalid case: missing name (Unknown)
            """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <dataSources>
                <dataSource>
                    <cmDataSource>PROD</cmDataSource>
                </dataSource>
            </dataSources>
        </project>""",
            [
                {
                    "dataSource": "Unknown",
                    "type": "invalid_missing_name",
                    "count": 0,
                }
            ],
        ),
    ],
)
def test_validate_data_sources(temp_xml_dir, xml_content, expected_issues):
    # Create the xml file in the temporary directory
    test_file = temp_xml_dir / "test_model.xml"
    test_file.write_text(xml_content, encoding="utf-8")

    # Run the function
    issues = validate_data_sources(str(temp_xml_dir))

    # Assert number of issues matches
    assert len(issues) == len(expected_issues)

    # Sort issues to compare reliably
    issues.sort(key=lambda x: x["type"])
    expected_issues.sort(key=lambda x: x["type"])

    # Assert exact issue properties
    for actual, expected in zip(issues, expected_issues):
        assert actual["dataSource"] == expected["dataSource"]
        assert actual["type"] == expected["type"]
        assert actual.get("count") == expected.get("count")
        assert actual["file"] == "test_model.xml"
