import pytest
from unittest import mock
from lxml import etree
from src.jmx.jmx_reader import (
    parse_jmx_file,
    extract_http_arguments,
    extract_http_request_details,
    extract_http_requests_from_test,
    extract_sub_controllers_from_test,
    extract_controller_item,
    extract_controllers,
    extract_test_plan_name,
    get_test_plan
)

# Mocked data for testing
mock_jmx_file = """
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Test Plan">
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
        <collectionProp name="Arguments.arguments"/>
      </elementProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
    </TestPlan>
    <hashTree>
      <TestFragmentController guiclass="TestFragmentControllerGui" testclass="TestFragmentController" testname="Test Fragment"/>
      <hashTree>
        <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Request 1">
          <stringProp name="HTTPSampler.path">/path1</stringProp>
          <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
          <stringProp name="HTTPSampler.method">GET</stringProp>
          <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
          <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
            <collectionProp name="Arguments.arguments">
              <elementProp name="status" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">value1</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name">arg1</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
        </HTTPSamplerProxy>
        <hashTree/>
        <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Controller 1" enabled="true"/>
        <hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Request 2" enabled="true">
            <stringProp name="HTTPSampler.path">${tests_url}/${tests_url}/v2/pet</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
            <collectionProp name="Arguments.arguments">
              <elementProp name="arg1" elementType="HTTPArgument">
                <boolProp name="HTTPArgument.always_encode">false</boolProp>
                <stringProp name="Argument.value">value1</stringProp>
                <stringProp name="Argument.metadata">=</stringProp>
                <boolProp name="HTTPArgument.use_equals">true</boolProp>
                <stringProp name="Argument.name">arg1</stringProp>
              </elementProp>
            </collectionProp>
          </elementProp>
          </HTTPSamplerProxy>
          <hashTree/>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
"""


@pytest.fixture
def mock_jmx_root():
    """Fixture to mock the JMX file root element."""
    return etree.fromstring(mock_jmx_file)


def test_parse_jmx_file_success(mocker, mock_jmx_root):
    """Test the parse_jmx_file function."""
    mocker.patch("lxml.etree.parse", return_value=mock.Mock(getroot=lambda: mock_jmx_root))

    root = parse_jmx_file("mock_file.jmx")
    assert root is not None


def test_parse_jmx_file_fail(mocker):
    """Test the parse_jmx_file function with a failing parse."""
    # Mock the etree.parse to raise an XMLSyntaxError
    mocker.patch("lxml.etree.parse", side_effect=etree.XMLSyntaxError("Syntax error", "", 0, 0, 0))

    with pytest.raises(etree.XMLSyntaxError):
        parse_jmx_file("invalid_path.jmx")


def test_extract_http_arguments(mock_jmx_root):
    """Test the extract_http_arguments function."""
    test_element = mock_jmx_root.xpath("//HTTPSamplerProxy")[0]

    args = extract_http_arguments(test_element)
    assert args == {"arg1": "value1"}


def test_extract_http_request_details(mock_jmx_root):
    """Test the extract_http_request_details function."""
    test_element = mock_jmx_root.xpath("//HTTPSamplerProxy")[0]

    details = extract_http_request_details(test_element)
    assert details["name"] == "Request 1"
    assert details["path"] == "/path1"
    assert details["method"] == "GET"
    assert details["arguments"] == {"arg1": "value1"}


def test_extract_http_requests_from_test(mock_jmx_root):
    """Test the extract_http_requests_from_test function."""
    test_element = mock_jmx_root.xpath("//HTTPSamplerProxy")[0]
    sub_controller_names = set()

    requests = extract_http_requests_from_test(test_element, sub_controller_names)

    assert len(requests) == 1
    assert requests[0]["name"] == "Request 1"


def test_extract_sub_controllers_from_test(mock_jmx_root):
    """Test the extract_sub_controllers_from_test function."""
    test_element = mock_jmx_root.xpath("//GenericController")[0]
    sub_controller_names = set()

    sub_controllers = extract_sub_controllers_from_test(test_element, sub_controller_names)

    assert len(sub_controllers) == 1
    assert sub_controllers[0]["item"]["name"] == "Controller 1"
    assert len(sub_controllers[0]["item"]["requests"]) == 2
    assert sub_controllers[0]["item"]["requests"][0]["name"] == "Request 2"


def test_extract_controller_item(mock_jmx_root):
    """Test the extract_controller_item function."""
    controller_element = mock_jmx_root.xpath("//GenericController")[0]
    sub_controller_names = set()

    controller_item = extract_controller_item(controller_element, sub_controller_names)

    assert controller_item["item"]["name"] == "Controller 1"
    assert len(controller_item["item"]["requests"]) == 1
    assert controller_item["item"]["requests"][0]["name"] == "Request 2"


def test_extract_controllers(mock_jmx_root):
    """Test the extract_controllers function."""
    root = mock_jmx_root
    controllers = extract_controllers(root)

    assert len(controllers) == 2  # One direct request, one controller with a request
    assert controllers[0]["item"]["name"] == "Controller 1"
    assert controllers[1]["item"]["name"] == "Request 1"


def test_extract_test_plan_name(mock_jmx_root):
    """Test the extract_test_plan_name function."""
    root = mock_jmx_root
    test_plan_name = extract_test_plan_name(root)

    assert test_plan_name == "Test Plan"


def test_get_test_plan(mock_jmx_root, mocker):
    """Test the get_test_plan function."""
    mocker.patch("src.jmx.jmx_reader.parse_jmx_file", return_value=mock_jmx_root)

    test_plan = get_test_plan("mock_file.jmx")

    assert test_plan["name"] == "Test Plan"
    assert len(test_plan["items"]) == 2