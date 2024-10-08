import json
import os
from src.helper.file_utils import file_write
from src.postman.postman_json_reader import read_postman_collection
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any


def create_generic_controller_xml(controller: Dict[str, Any]) -> str:
    """
    Recursively creates XML for a Generic Controller and its child controllers or requests.

    Args:
        controller (Dict[str, Any]): The controller containing information such as its type and children.

    Returns:
        str: XML string for the controller.
    """
    if controller['type'] == 'request':
        return create_http_sampler(controller)

    controller_xml = f"""
    <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="{controller['name']}"/>
    <hashTree>
    """

    # Recursively process child controllers or requests
    child_creators = {
        'generic_controller': create_generic_controller_xml,
        'child_generic_controller': create_generic_controller_xml,
        'request': create_http_sampler
    }

    for child in controller.get('children', []):
        create_child_xml = child_creators.get(child['type'])
        if create_child_xml:
            controller_xml += create_child_xml(child)

    controller_xml += "</hashTree>"
    return controller_xml


def create_http_sampler(request: Dict[str, Any]) -> str:
    """
    Creates XML for an HTTPSamplerProxy element, handling URL, method, and query parameters.

    Args:
        request (Dict[str, Any]): A dictionary representing the request information such as URL, method, and name.

    Returns:
        str: XML string representing the HTTPSamplerProxy element.
    """
    test_name = request['name']
    method = request['method']
    path = request['raw_url']

    # Parse the URL to separate the path and query parameters
    parsed_url = urlparse(path)
    base_path = parsed_url.path
    query_params = parse_qs(parsed_url.query)

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

    # Add response assertion for status code 200 if defined in tests
    if 'tests' in request:
        for test in request['tests']:
            if "pm.response.to.have.status(200)" in test['script']:
                sampler_xml += create_response_assertion(test_name, "200")

    sampler_xml += "</hashTree>"
    return sampler_xml


def create_response_assertion(test_name: str, expected_status: str) -> str:
    """
    Creates XML for a ResponseAssertion element based on the expected status code.

    Args:
        test_name (str): The name of the test associated with the assertion.
        expected_status (str): The expected HTTP response status code (e.g., "200").

    Returns:
        str: XML string representing the ResponseAssertion element.
    """
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


def create_jmx_file(source_file: str, jmx_file: str) -> None:
    """
    Creates a JMeter .jmx file based on a Postman collection by converting it into a test plan structure.

    Args:
        source_file (str): The source file (Postman collection) to read from.
        jmx_file (str): The file path where the JMX file should be saved.

    Returns:
        None
    """
    postman_json_path_final = ""
    current_file_dir = os.path.dirname(__file__)
    parent_folder_path = os.path.abspath(os.path.join(current_file_dir, os.pardir))

    # Determine the final path of the Postman collection
    if not os.path.exists(source_file):
        postman_json_path_final = os.path.join(parent_folder_path, "file_to_convert", f"{source_file}.json")
    else:
        postman_json_path_final = source_file

    try:
        # Read the Postman collection data
        data = read_postman_collection(postman_json_path_final)
    except FileNotFoundError:
        print(f"Error: File {postman_json_path_final} not found.")
        raise
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the Postman collection.")
        raise

    # Initialize the JMX file with the test plan and fragment controller
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

    # Determine output path and file name for the JMX file
    if 'jmx' in jmx_file:
        output_path = os.path.abspath(os.path.join(jmx_file, os.pardir))
        file_name = os.path.basename(jmx_file)
    else:
        file_name = f"{jmx_file}.jmx"
        output_path = os.path.join(parent_folder_path, "out")

    # Write the generated JMX content to the file
    file_write(output_path, file_name, jmx_content)