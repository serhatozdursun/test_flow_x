import json
from lxml import etree


def parse_jmx_file(file_path):
    """Parses the JMX file and returns the root element."""
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except etree.XMLSyntaxError as e:
        print(f"Error parsing the JMX file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return None


def extract_http_arguments(test_element):
    """Extracts HTTP arguments from a test element."""
    return {
        arg.findtext(".//stringProp[@name='Argument.name']", "body"):
            arg.findtext(".//stringProp[@name='Argument.value']", "")
        for arg in test_element.xpath(".//elementProp[@elementType='HTTPArgument']")
    }


def extract_request(test_element):
    """Extracts request details from an HTTPSamplerProxy or LogicControllerGui."""
    return {
        "name": test_element.attrib.get("testname", "no requests"),
        "path": test_element.findtext(".//stringProp[@name='HTTPSampler.path']", ""),
        "method": test_element.findtext(".//stringProp[@name='HTTPSampler.method']", ""),
        "arguments": extract_http_arguments(test_element)
    }


def extract_controllers(root):
    """Extracts controllers and their associated requests from the JMX file."""
    controllers = []
    sub_controller_names = set()

    for controller in root.xpath('.//GenericController'):
        controller_name = controller.attrib.get("testname", "none")

        # Skip if this controller is already a sub-controller
        if controller_name in sub_controller_names:
            continue

        controller_item = {
            "item": {
                "name": controller_name,
                "requests": [],
                "sub_controller": []
            }
        }

        # Find the associated hashTree for the controller
        parent_hash_tree = controller.xpath("following-sibling::hashTree[1]")

        if parent_hash_tree:
            for test in parent_hash_tree[0]:
                if test.attrib.get("guiclass") == "HttpTestSampleGui":
                    controller_item["item"]["requests"].append(extract_request(test))
                elif test.attrib.get("guiclass") == "LogicControllerGui":
                    sub_controller = {
                        "item": {
                            "name": test.attrib.get("testname", "none"),
                            "requests": []
                        }
                    }
                    sub_hash_tree = test.xpath("following-sibling::hashTree[1]")
                    if sub_hash_tree:
                        for sub_test in sub_hash_tree[0]:
                            sub_controller["item"]["requests"].append(extract_request(sub_test))

                    controller_item["item"]["sub_controller"].append(sub_controller)
                    sub_controller_names.add(sub_controller["item"]["name"])

        controllers.append(controller_item)

    return controllers


def extract_test_plan_name(root):
    """Extracts the test name from the TestPlan element."""
    test_plan = root.find(".//TestPlan")
    if test_plan is not None:
        return test_plan.attrib.get("testname", "Unnamed Test Plan")
    return "Unnamed Test Plan"


def get_test_plan(file_path):
    root = parse_jmx_file(file_path)
    if root is not None:
        # Extract the name of the test plan
        test_plan_name = extract_test_plan_name(root)
        controllers = extract_controllers(root)
        return {
            "name": test_plan_name,
            "items": controllers
        }
    return None


if __name__ == '__main__':
    file_path = "/Users/sozdursun/PycharmProjects/test_flow_x/file_to_convert/hot_topic.jmx"
        # Output the result as JSON
    print(json.dumps(get_test_plan(file_path), indent=2))
