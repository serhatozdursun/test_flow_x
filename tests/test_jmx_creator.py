import os
from lxml import etree

from jmx.jmx_creator import create_jmx_file, create_response_assertion, create_http_sampler

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
    mock_read_postman_collection = mocker.patch('jmx.jmx_creator.read_postman_collection',
                                                return_value=mocked_postman_data)

    mock_file_write = mocker.patch('jmx.jmx_creator.file_write')

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
    args, kwargs = mock_file_write.call_args

    # Assert that the output path is correct
    assert os.path.abspath(os.path.join(jmx_file, os.pardir)) == args[0]  # output_path
    assert os.path.basename(jmx_file) == args[1]  # file_name
    assert isinstance(args[2], str)  # jmx_content should be a string, but you can also validate its structure

    # Assert that the file_exists was called
    mock_file_exists.assert_called_once()


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
