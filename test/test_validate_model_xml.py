import pytest
import sys
import os

# Add the src directory to the path so we can import from it
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from utils.validate_model_xml import check_xml_files

@pytest.fixture
def temp_xml_dir(tmp_path):
    return tmp_path

@pytest.mark.parametrize("xml_content, expected_issues", [
    (
        # Valid case: 1 querySubject, 1 sources, 1 dataSourceRef
        """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>ValidSubject</name>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
        []
    ),
    (
        # Valid case: 1 querySubject, 0 sources
        """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>NoSourcesSubject</name>
            </querySubject>
        </project>""",
        []
    ),
    (
        # Invalid case: 1 querySubject, 2 sources
        """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MultipleSourcesSubject</name>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                </sources>
                <sources>
                    <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
        [
            {"querySubject": "MultipleSourcesSubject", "type": "multiple_sources", "count": 2}
        ]
    ),
    (
        # Invalid case: 1 querySubject, 1 sources, 2 dataSourceRef
        """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>MultipleRefsSubject</name>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                    <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
        [
            {"querySubject": "MultipleRefsSubject", "type": "multiple_dataSourceRefs", "count": 2}
        ]
    ),
    (
        # Invalid case: Both issues in one querySubject
        """<?xml version="1.0" encoding="UTF-8" ?>
        <project xmlns="http://www.developer.cognos.com/schemas/bmt/60/12">
            <querySubject>
                <name>DoubleTroubleSubject</name>
                <sources>
                    <dataSourceRef>[].[dataSources].[PROD]</dataSourceRef>
                    <dataSourceRef>[].[dataSources].[TEST]</dataSourceRef>
                </sources>
                <sources>
                    <dataSourceRef>[].[dataSources].[DEV]</dataSourceRef>
                </sources>
            </querySubject>
        </project>""",
        [
            {"querySubject": "DoubleTroubleSubject", "type": "multiple_sources", "count": 2},
            {"querySubject": "DoubleTroubleSubject", "type": "multiple_dataSourceRefs", "count": 2}
        ]
    )
])
def test_check_xml_files(temp_xml_dir, xml_content, expected_issues):
    # Create the xml file in the temporary directory
    test_file = temp_xml_dir / "test_model.xml"
    test_file.write_text(xml_content, encoding='utf-8')
    
    # Run the function
    issues = check_xml_files(str(temp_xml_dir))
    
    # Assert number of issues matches
    assert len(issues) == len(expected_issues)
    
    # Sort issues to compare reliably
    issues.sort(key=lambda x: x['type'])
    expected_issues.sort(key=lambda x: x['type'])
    
    # Assert exact issue properties
    for actual, expected in zip(issues, expected_issues):
        assert actual['querySubject'] == expected['querySubject']
        assert actual['type'] == expected['type']
        assert actual['count'] == expected['count']
        assert actual['file'] == "test_model.xml"
