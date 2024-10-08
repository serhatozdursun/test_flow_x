import logging
from lxml import etree
from typing import Optional, Dict, List

# Set up logging
logging.basicConfig(level=logging.ERROR)


def parse_jmx_file(file_path: str) -> Optional[etree._Element]:
    """
    Parses the JMX file and returns the root element.

    Args:
        file_path (str): Path to the JMX file.

    Returns:
        Optional[etree._Element]: Root element of the parsed JMX file or None if parsing fails.
    """
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except etree.XMLSyntaxError as e:
        logging.error(f"Error parsing the JMX file: {e}")
        raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        raise
    return None


def extract_http_arguments(test_element: etree._Element) -> Dict[str, str]:
    """
    Extracts HTTP arguments from a test element.

    Args:
        test_element (etree._Element): XML element representing a test (e.g., HTTPSamplerProxy).

    Returns:
        Dict[str, str]: A dictionary of argument names and values.
    """
    return {
        arg.findtext(".//stringProp[@name='Argument.name']", "body"):
            arg.findtext(".//stringProp[@name='Argument.value']", "")
        for arg in test_element.xpath(".//elementProp[@elementType='HTTPArgument']")
    }


def extract_http_request_details(test_element: etree._Element) -> Dict[str, object]:
    """
    Extracts HTTP request details from an HTTPSamplerProxy or LogicControllerGui element.

    Args:
        test_element (etree._Element): XML element representing an HTTP request or logic controller.

    Returns:
        Dict[str, object]: A dictionary containing request details such as name, path, method, and arguments.
    """
    return {
        "name": test_element.attrib.get("testname", "Unnamed Request"),
        "path": test_element.findtext(".//stringProp[@name='HTTPSampler.path']", ""),
        "method": test_element.findtext(".//stringProp[@name='HTTPSampler.method']", "GET"),
        "arguments": extract_http_arguments(test_element) or {}
    }


def extract_http_requests_from_test(test: etree._Element, sub_controller_names: set) -> List[Dict[str, object]]:
    """
    Extracts HTTP request details from a given test element and updates the sub_controller_names set.

    Args:
        test (etree._Element): The XML element representing the test.
        sub_controller_names (set): The set of sub-controller names to be updated.

    Returns:
        List[Dict[str, object]]: A list of HTTP request details.
    """
    requests = []
    if test.attrib.get("guiclass") == "HttpTestSampleGui":
        http_request_details = extract_http_request_details(test)
        requests.append(http_request_details)
        sub_controller_names.add(http_request_details["name"])
    return requests


def extract_sub_controllers_from_test(test: etree._Element, sub_controller_names: set) -> List[Dict[str, object]]:
    """
    Extracts sub-controller details from a given LogicController element.

    Args:
        test (etree._Element): The XML element representing the LogicController.
        sub_controller_names (set): The set of sub-controller names to be updated.

    Returns:
        List[Dict[str, object]]: A list of sub-controllers and their associated requests.
    """
    sub_controllers = []
    sub_controller_name = test.attrib.get("testname", "none")
    sub_controller = {
        "item": {
            "name": sub_controller_name,
            "requests": []
        }
    }
    sub_hash_tree = test.getnext()
    if sub_hash_tree.tag == 'hashTree':
        for sub_test in sub_hash_tree:
            http_request_details = extract_http_request_details(sub_test)
            sub_controller["item"]["requests"].append(http_request_details)
            sub_controller_names.add(http_request_details["name"])
    sub_controllers.append(sub_controller)
    return sub_controllers


def extract_controller_item(controller: etree._Element, sub_controller_names: set) -> Dict[str, object]:
    """
    Extracts a controller item, including its requests and sub-controllers.

    Args:
        controller (etree._Element): The XML element representing the controller.
        sub_controller_names (set): The set of sub-controller names to be updated.

    Returns:
        Dict[str, object]: The controller item with its requests and sub-controllers.
    """
    controller_name = controller.attrib.get("testname", "none")
    controller_item = {
        "item": {
            "name": controller_name,
            "requests": [],
            "sub_controller": []
        }
    }

    parent_hash_tree = controller.getnext()
    if parent_hash_tree.tag == 'hashTree':
        for test in parent_hash_tree:
            # Extract HTTP requests or sub-controllers
            if test.attrib.get("guiclass") == "HttpTestSampleGui":
                controller_item["item"]["requests"].extend(extract_http_requests_from_test(test, sub_controller_names))
            elif test.attrib.get("guiclass") == "LogicControllerGui":
                controller_item["item"]["sub_controller"].extend(
                    extract_sub_controllers_from_test(test, sub_controller_names))

    return controller_item


def extract_controllers(root: etree._Element) -> List[Dict[str, object]]:
    """
    Extracts controllers and their associated requests from the JMX file.

    Args:
        root (etree._Element): Root element of the JMX file.

    Returns:
        List[Dict[str, object]]: A list of controllers and their associated requests and sub-controllers.
    """
    controllers = []
    sub_controller_names = set()

    # Extract controllers and their sub-controllers
    for controller in root.iter('GenericController'):
        controllers.append(extract_controller_item(controller, sub_controller_names))

    # Handle direct requests (i.e., HTTPSamplerProxy elements)
    for sampler in root.xpath('.//HTTPSamplerProxy'):
        request_name = sampler.attrib.get("testname", "Unnamed Request")
        if request_name not in sub_controller_names:
            controller_item = {
                "item": {
                    "name": request_name,
                    "requests": [extract_http_request_details(sampler)],
                    "sub_controller": []
                }
            }
            controllers.append(controller_item)

    return controllers


def extract_test_plan_name(root: etree._Element) -> str:
    """
    Extracts the test plan name from the TestPlan element.

    Args:
        root (etree._Element): Root element of the JMX file.

    Returns:
        str: The name of the test plan, or "Unnamed Test Plan" if not found.
    """
    test_plan = root.find(".//TestPlan")
    if test_plan is not None:
        return test_plan.attrib.get("testname", "Unnamed Test Plan")
    return "Unnamed Test Plan"


def get_test_plan(file_path: str) -> Optional[Dict[str, object]]:
    """
    Retrieves the test plan structure, including the test plan name and controllers with requests.

    Args:
        file_path (str): Path to the JMX file.

    Returns:
        Optional[Dict[str, object]]: A dictionary containing the test plan name and a list of items (controllers and requests),
                                     or None if the JMX file cannot be parsed.
    """
    root = parse_jmx_file(file_path)
    if root is not None:
        # Extract the name of the test plan
        test_plan_name = extract_test_plan_name(root)
        controllers = extract_controllers(root)
        return {
            "name": test_plan_name,
            "items": controllers
        }
    return {
        "error": "Failed to parse JMX file"
    }
