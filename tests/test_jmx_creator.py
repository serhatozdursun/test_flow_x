import json
import os

import pytest

from src.jmx.jmx_creator import create_jmx_file, create_response_assertion, create_http_sampler, \
    create_generic_controller_xml

# Mock Postman data
mocked_postman_data = {'test_plan_name': 'Sample', 'test_plan_comments': 'No description found',
                       'test_fragment_controller': {'name': 'Test Fragment', 'generic_controllers': [
                           {'id': 'controller_1', 'name': 'Test', 'type': 'generic_controller', 'parent': None,
                            'children': [
                                {'id': 'controller_1', 'name': 'Pet Post', 'type': 'request', 'parent': 'controller_1',
                                 'method': 'POST', 'raw_url': '/${tests_url}/v2/pet',
                                 'queryParams': [{'No query parameters': ''}],
                                 'body': '{\n    "id": 0,\n    "category": {\n        "id": 0,\n        "name": "string"\n    },\n    "name": "doggie",\n    "photoUrls": [\n        "string"\n    ],\n    "tags": [\n        {\n            "id": 0,\n            "name": "string"\n        }\n    ],\n    "status": "available"\n}',
                                 'tests': []}]},
                           {'id': 'controller_2', 'name': 'Get Test', 'type': 'generic_controller', 'parent': None,
                            'children': [
                                {'id': 'controller_1', 'name': 'Get', 'type': 'request', 'parent': 'controller_2',
                                 'method': 'GET',
                                 'raw_url': 'https://petstore_swagger_io/v2/pet/findByStatus?status=pending',
                                 'queryParams': [{'status': 'pending'}], 'body': 'No body content', 'tests': []}]}]}}


def test_create_jmx_file_valid_input(mocker):
    # Mock the read_postman_collection to return mock_postman_data
    mock_read_postman_collection = mocker.patch('src.jmx.jmx_creator.read_postman_collection',
                                                return_value=mocked_postman_data)

    mock_file_write = mocker.patch('src.jmx.jmx_creator.file_write')

    # Mock os.path.isfile and os.path.exists to avoid file existence errors
    mock_file_exists = mocker.patch('os.path.exists', return_value=True)

    # Call the create_jmx_file function
    source_file = 'mock_postman_collection.json'
    jmx_file = 'mock_output.jmx'
    create_jmx_file(source_file, jmx_file)

    # Assert that read_postman_collection was called with the correct file path
    mock_read_postman_collection.assert_called_once_with(source_file)

    # Assert that file_write was called with the correct arguments
    # Get the arguments passed to file_write
    args, _ = mock_file_write.call_args

    # Assert that the output path is correct
    assert os.path.abspath(os.path.join(jmx_file, os.pardir)) == args[0]  # output_path
    assert os.path.basename(jmx_file) == args[1]  # file_name
    assert isinstance(args[2], str)  # jmx_content should be a string, but you can also validate its structure

    # Assert that the file_exists was called
    mock_file_exists.assert_called_once()


def test_create_generic_controller_xml_request(mocker):
    # Mock the controller dictionary with 'type' as 'request'
    controller = {
        'type': 'request',
        'name': 'Test Request Controller',
        'children': []  # No children for this test case
    }

    # Use mocker to mock create_http_sampler
    mock_create_http_sampler = mocker.patch('src.jmx.jmx_creator.create_http_sampler')

    # Set a mock return value for create_http_sampler
    mock_create_http_sampler.return_value = "<HttpSampler guiclass='HttpSamplerGui' testclass='HttpSampler' testname='Test Request Controller'/>"

    # Call the function
    result = create_generic_controller_xml(controller)

    # Assertions
    mock_create_http_sampler.assert_called_once_with(controller)  # Verify that create_http_sampler was called
    expected_xml = "<HttpSampler guiclass='HttpSamplerGui' testclass='HttpSampler' testname='Test Request Controller'/>"
    assert result == expected_xml  # Check that the returned XML matches the expected output


def test_create_jmx_file_with_nonexistent_source_file(mocker):
    # Mock the os.path.exists function to simulate that the source file does not exist
    mock_exists = mocker.patch('os.path.exists', return_value=False)

    # Mock other required functions
    mock_read_postman_collection = mocker.patch('src.jmx.jmx_creator.read_postman_collection')
    mock_file_write = mocker.patch('src.jmx.jmx_creator.file_write')

    # Set up mock data for read_postman_collection
    mock_read_postman_collection.return_value = {
        'test_plan_name': 'Test Plan',
        'test_fragment_controller': {
            'name': 'Test Fragment',
            'generic_controllers': []
        }
    }

    # Set the source file name that does not exist
    source_file = 'non_existent_file'
    jmx_file = 'test.jmx'

    # Fix the way to calculate the parent folder path
    current_file_dir = os.path.dirname(__file__)  # This will be the current directory of the test file
    parent_folder_path = os.path.abspath(os.path.join(current_file_dir, '..'))  # Go one directory up
    expected_postman_json_path_final = os.path.join(parent_folder_path, "file_to_convert", f"{source_file}.json")

    # Call the function
    create_jmx_file(source_file, jmx_file)

    # Assertions
    mock_exists.assert_called_once_with(source_file)  # Ensure os.path.exists was called with the correct source file
    assert expected_postman_json_path_final == os.path.join(parent_folder_path, "file_to_convert",
                                                            f"{source_file}.json")

    # Ensure that read_postman_collection and file_write were called
    mock_read_postman_collection.assert_called_once_with(expected_postman_json_path_final)
    mock_file_write.assert_called_once()


def test_create_jmx_file_file_not_found(mocker):
    # Arrange
    source_file = "non_existent_file"
    jmx_file = "output_jmx"

    # Mock read_postman_collection to raise FileNotFoundError
    mocker.patch("src.jmx.jmx_creator.read_postman_collection", side_effect=FileNotFoundError)

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        create_jmx_file(source_file, jmx_file)


def test_create_jmx_file_else_block(mocker):
    # Arrange
    source_file = "existing_file"
    jmx_file = "output_file"

    # Mock the existence of the file to return True (i.e., file exists)
    mocker.patch("os.path.exists", return_value=True)

    # Mock the reading of the Postman collection (since we're testing the else block)
    mocker.patch("src.jmx.jmx_creator.read_postman_collection",
                 return_value={"test_plan_name": "Test Plan", "test_fragment_controller": {}})

    # Mock the file_write function (to avoid actual file I/O)
    mock_file_write = mocker.patch("src.jmx.jmx_creator.file_write")

    mock_read_postman_collection = mocker.patch('src.jmx.jmx_creator.read_postman_collection',
                                                return_value=mocked_postman_data)
    # Act
    create_jmx_file(source_file, jmx_file)

    # Assert the output path and file name are correctly set
    expected_output_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)), "out")
    expected_file_name = f"{jmx_file}.jmx"

    mock_read_postman_collection.assert_called_once_with(source_file)

    # Verify that file_write was called with the correct parameters
    mock_file_write.assert_called_once_with(expected_output_path, expected_file_name, mocker.ANY)


def test_create_jmx_file_invalid_json(mocker):
    # Arrange
    source_file = "invalid_json_file"
    jmx_file = "output_jmx"

    # Mock read_postman_collection to raise JSONDecodeError
    mocker.patch("src.jmx.jmx_creator.read_postman_collection",
                 side_effect=json.JSONDecodeError("Invalid JSON", "doc", 0))

    # Act & Assert
    with pytest.raises(json.JSONDecodeError):
        create_jmx_file(source_file, jmx_file)


def test_create_generic_controller_xml_with_child(mocker):
    # Mock the controller dictionary with a child controller
    controller = {
        'type': 'generic_controller',
        'name': 'Parent Controller',
        'children': [
            {
                'type': 'request',
                'name': 'Child Request Controller',
                'children': []  # No further children
            }
        ]
    }

    # Mock create_http_sampler to simulate 'request' type child controller
    mock_create_http_sampler = mocker.patch('src.jmx.jmx_creator.create_http_sampler')
    mock_create_http_sampler.return_value = "<HttpSampler guiclass='HttpSamplerGui' testclass='HttpSampler' testname='Child Request Controller'/>"

    # Mock the recursive call to create_generic_controller_xml for child controllers
    mock_create_generic_controller_xml = mocker.patch('src.jmx.jmx_creator.create_generic_controller_xml')
    mock_create_generic_controller_xml.return_value = "<GenericController guiclass='LogicControllerGui' testclass='GenericController' testname='Child Request Controller'/>"

    # Call the function
    result = create_generic_controller_xml(controller)

    # Assertions
    # Check that create_http_sampler was called for the 'request' child controller
    mock_create_http_sampler.assert_called_once_with(controller['children'][0])

    # Ensure the result includes the expected XML
    expected_xml = """
    <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Parent Controller"/>
    <hashTree>
    <HttpSampler guiclass='HttpSamplerGui' testclass='HttpSampler' testname='Child Request Controller'/></hashTree>
    """
    assert result.strip() == expected_xml.strip()


def test_create_generic_controller_xml_without_child(mocker):
    # Mock the controller dictionary without children
    controller = {
        'type': 'generic_controller',
        'name': 'Parent Controller',
        'children': []  # No children to process
    }

    # Mock the create_http_sampler and create_generic_controller_xml functions
    mock_create_http_sampler = mocker.patch('src.jmx.jmx_creator.create_http_sampler')
    mock_create_generic_controller_xml = mocker.patch('src.jmx.jmx_creator.create_generic_controller_xml')

    # Call the function
    result = create_generic_controller_xml(controller)

    # Ensure that create_http_sampler and create_generic_controller_xml were not called
    mock_create_http_sampler.assert_not_called()
    mock_create_generic_controller_xml.assert_not_called()

    # Check that the result does not include any child XML and only the parent is returned
    expected_xml = """
    <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Parent Controller"/>
    <hashTree>
    </hashTree>
    """
    assert result.strip() == expected_xml.strip()


def test_create_response_assertion():
    # Test data
    test_name = 'Test Get Pet'
    expected_status = '200'

    # Expected XML output
    expected_xml = f"""
    <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion for {test_name} expected_status: {expected_status}">
        <collectionProp name="Asserion.test_strings">
            <stringProp name="49586">{expected_status}</stringProp>
        </collectionProp>
        <collectionProp name="Assertion.test_strings">
            <stringProp name="49586">{expected_status}</stringProp>
        </collectionProp>
        <stringProp name="Assertion.custom_message"></stringProp>
        <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
        <boolProp name="Assertion.assume_success">false</boolProp>
        <intProp name="Assertion.test_type">8</intProp>
    </ResponseAssertion>
    <hashTree/>
    """

    # Call the function
    result = create_response_assertion(test_name, expected_status)

    # Assert the result matches the expected output
    assert result.strip() == expected_xml.strip()


def test_create_http_sampler_with_non_200_status_assertion(mocker):
    # Mock the create_response_assertion function
    mock_create_response_assertion = mocker.patch('src.jmx.jmx_creator.create_response_assertion')
    mock_create_response_assertion.return_value = "<ResponseAssertion guiclass='ResponseAssertionGui' testclass='ResponseAssertion' testname='test_name'/>"

    # Mock the request dictionary with 'tests' containing the response assertion condition
    request = {
        'name': 'Test Request',
        'method': 'GET',
        'raw_url': 'https://example.com/api/v1/resource',
        'tests': [
            {
                'script': "pm.response.to.have.status(500)"  # This triggers a different status code
            }
        ]
    }

    # Call the function
    result = create_http_sampler(request)

    # Check that create_response_assertion was not called (since status is not 200)
    mock_create_response_assertion.assert_not_called()

    # Check that the generated XML does not contain a response assertion
    expected_xml = """  
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Test Request" enabled="true">
        <stringProp name="HTTPSampler.path">${tests_url}/api/v1/resource</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">GET</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    </hashTree>
    """
    assert result.strip() == expected_xml.strip()


def test_basic_http_sampler():
    """Test basic HTTP sampler generation without query params or assertions."""
    request = {
        'name': 'Test Get Request',
        'method': 'GET',
        'raw_url': 'https://example.com/pets',
    }

    # Call the function to generate the XML
    result_xml = create_http_sampler(request)

    expected_result = """
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Test Get Request" enabled="true">
        <stringProp name="HTTPSampler.path">${tests_url}/pets</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">GET</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    </hashTree>
    """

    assert expected_result.strip() == result_xml.strip()


def test_create_http_sampler_with_query_params():
    request = {
        'name': 'Test Get Request with Params',
        'method': 'GET',
        'raw_url': 'https://api.example.com/pets?status=available&limit=10'
    }

    expected_xml = """
    
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Test Get Request with Params" enabled="true">
        <stringProp name="HTTPSampler.path">${tests_url}/pets</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">GET</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            
                <elementProp name="status" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">available</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name">status</stringProp>
                </elementProp>
            
                <elementProp name="limit" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">10</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name">limit</stringProp>
                </elementProp>
            
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    </hashTree>
    """

    result = create_http_sampler(request)

    assert result.strip() == expected_xml.strip()


def test_create_http_sampler_with_response_assertion():
    request = {
        'name': 'Test Get Request with Assertion',
        'method': 'GET',
        'raw_url': 'https://api.example.com/pets',
        'tests': [{'script': 'pm.response.to.have.status(200)'}]
    }

    expected_xml = """
    
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Test Get Request with Assertion" enabled="true">
        <stringProp name="HTTPSampler.path">${tests_url}/pets</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">GET</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    
    <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Response Assertion for Test Get Request with Assertion expected_status: 200">
        <collectionProp name="Asserion.test_strings">
            <stringProp name="49586">200</stringProp>
        </collectionProp>
        <collectionProp name="Assertion.test_strings">
            <stringProp name="49586">200</stringProp>
        </collectionProp>
        <stringProp name="Assertion.custom_message"></stringProp>
        <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
        <boolProp name="Assertion.assume_success">false</boolProp>
        <intProp name="Assertion.test_type">8</intProp>
    </ResponseAssertion>
    <hashTree/>
    </hashTree>
    """

    result = create_http_sampler(request)

    assert result.strip() == expected_xml.strip()


def test_create_http_sampler_no_query_params_or_tests():
    request = {
        'name': 'Test Get Request No Params',
        'method': 'GET',
        'raw_url': 'https://api.example.com/pets'
    }

    expected_xml = """
    
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="Test Get Request No Params" enabled="true">
        <stringProp name="HTTPSampler.path">${tests_url}/pets</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">GET</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    </hashTree>
    """

    result = create_http_sampler(request)

    assert result.strip() == expected_xml.strip()
