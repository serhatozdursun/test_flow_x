import json
import os
from helper.file_utils import file_write
from postman.postman_json_reader import read_postman_collection
from urllib.parse import urlparse, parse_qs


def create_generic_controller_xml(controller):
    """Recursively create XML for GenericController and its children."""
    controller_xml = f"""
    <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="{controller['name']}"/>
    <hashTree>
    """

    # Recursively add children controllers or requests
    for child in controller.get('children', []):
        if child['type'] in ['generic_controller', 'child_generic_controller']:
            controller_xml += create_generic_controller_xml(child)
        elif child['type'] == 'request':
            controller_xml += create_http_sampler(child)

    controller_xml += "</hashTree>"
    return controller_xml


def create_http_sampler(request):
    """Create XML for HTTPSamplerProxy, including assertions if defined in tests."""
    test_name = request['name']
    method = request['method']
    path = request['raw_url']

    # Parse the URL to separate the path and query parameters
    parsed_url = urlparse(path)
    base_path = parsed_url.path
    query_params = parse_qs(parsed_url.query)  # Returns a dictionary of query parameters

    # Create the XML for query parameters
    arguments_xml = ""
    for key, values in query_params.items():
        for value in values:
            arguments_xml += f"""
                <elementProp name="{key}" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{value}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                  <boolProp name="HTTPArgument.use_equals">true</boolProp>
                  <stringProp name="Argument.name">{key}</stringProp>
                </elementProp>
            """

    # Create the final XML output
    sampler_xml = f"""
    <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="{test_name}" enabled="true">
        <stringProp name="HTTPSampler.path">${{tests_url}}{base_path}</stringProp>
        <boolProp name="HTTPSampler.follow_redirects">true</boolProp>
        <stringProp name="HTTPSampler.method">{method}</stringProp>
        <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
        <boolProp name="HTTPSampler.postBodyRaw">false</boolProp>
        <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
          <collectionProp name="Arguments.arguments">
            {arguments_xml}
          </collectionProp>
        </elementProp>
    </HTTPSamplerProxy>
    <hashTree>
    """

    # Check for assertions in the request's tests
    if 'tests' in request:
        for test in request['tests']:
            if "pm.response.to.have.status(200)" in test['script']:  # Check for the specific assertion
                sampler_xml += create_response_assertion(test_name, "200")

    sampler_xml += "</hashTree>"
    return sampler_xml


def create_response_assertion(test_name, expected_status):
    """Create XML for a response assertion based on the expected status code."""
    return f"""
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


def create_jmx_file(source_file, jmx_file):
    postman_json_path_final = ""
    current_file_dir = os.path.dirname(__file__)
    parent_folder_path = os.path.abspath(os.path.join(current_file_dir, os.pardir))
    if not os.path.exists(source_file):
        # Get the parent directory
        postman_json_path_final = os.path.join(parent_folder_path, "file_to_convert", f"{source_file}.json")
    else:
        postman_json_path_final = source_file

    """Create a JMeter .jmx file based on the Postman collection."""
    try:
        data = read_postman_collection(postman_json_path_final)
    except FileNotFoundError:
        print(f"Error: File {postman_json_path_final} not found.")
        return
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the Postman collection.")
        return

    # Initialize the JMX file with the test plan and test fragment controller
    jmx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
    <jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
      <hashTree>
        <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="{data['test_plan_name']}">
          <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables">
            <collectionProp name="Arguments.arguments"/>
          </elementProp>
          <boolProp name="TestPlan.functional_mode">false</boolProp>
          <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
        </TestPlan>
        <hashTree>
          <TestFragmentController guiclass="TestFragmentControllerGui" testclass="TestFragmentController" testname="{data['test_fragment_controller']['name']}" enabled="true"/>
          <hashTree>
    """

    # Generate the XML for all controllers
    for controller in data['test_fragment_controller'].get('generic_controllers', []):
        jmx_content += create_generic_controller_xml(controller)

    # Close the XML tags
    jmx_content += """
          </hashTree>
        </hashTree>
      </hashTree>
    </jmeterTestPlan>
    """

    if 'jmx' in jmx_file:
        output_path = os.path.abspath(os.path.join(jmx_file, os.pardir))
        file_name = os.path.basename(jmx_file)
    # Write the JMX file
    else:
        file_name = f"{jmx_file}.jmx"
        output_path = os.path.join(parent_folder_path, "out")
    file_write(output_path, file_name, jmx_content)
    GREEN_TEXT = '\033[92m'
    print(f'{GREEN_TEXT}JMeter .jmx file created at: {output_path}')
