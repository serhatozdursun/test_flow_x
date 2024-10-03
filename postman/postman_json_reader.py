import json
import os
import re
from urllib.parse import urlparse, parse_qsl
from jsonschema import validate, ValidationError
from helper.file_utils import file_load  # Assuming this function exists and is imported correctly


def validate_postman_schema(data, schema_file_path='data/postman_schema.json'):
    try:
        # Load schema from the file using file_load
        schema = json.loads(file_load(schema_file_path))
        # Validate the data against the schema
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise Exception(f"Error: The provided file does not conform to the Postman Collection schema.")
    except Exception as e:
        raise Exception(f"Error loading or validating schema: {e}")


def read_postman_collection(file_path):
    # Check if the file exists
    if not os.path.isfile(file_path):
        raise Exception(f"Error: The file '{file_path}' does not exist.")

    # Open and read the JSON file
    data = {}
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
    except Exception as e:
        print(f"Error: {e}")

    #Validate the Postman collection against the schema
    validate_postman_schema(data)

    info = data.get("info", {})
    test_plan_name = info["name"]
    test_plan_comments = info.get("description", "No description found")

    generic_controllers = extract_generic_controllers(data.get("item", []))

    return {
        "test_plan_name": test_plan_name.replace("&", "and"),
        "test_plan_comments": test_plan_comments,
        "test_fragment_controller": {
            "name": "Test Fragment",
            "generic_controllers": generic_controllers
        }
    }


def extract_generic_controllers(items, parent_id=None):
    generic_controllers = []
    controller_id_counter = 1  # To assign unique IDs

    for item in items:
        controller_id = f"controller_{controller_id_counter}"
        controller_id_counter += 1

        if "item" in item:  # Indicates it's a folder-like structure (generic controller)
            controller = {
                "id": controller_id,
                "name": item.get("name", "Unnamed Controller").replace("&", "and"),
                "type": "generic_controller" if not parent_id else "child_generic_controller",
                "parent": parent_id if parent_id else None,
                "children": extract_generic_controllers(item.get("item", []), parent_id=controller_id)  # Recursively gather nested controllers
            }
            generic_controllers.append(controller)
        else:  # It's a request, so process it as such
            if "request" in item:
                raw_url = item["request"].get("url", {}).get("raw", "No URL")
                # Replacing {{ with ${ and }} with }
                raw_url = re.sub(r'{{', '${', raw_url)
                raw_url = re.sub(r'}}', '}', raw_url)
                raw_url = re.sub(r'\.', '_', raw_url)
                name = item.get("name", "Unnamed Request")
                name = re.sub(r'&', ' and ', name)
                request_data = {
                    "id": controller_id,
                    "name": name,
                    "type": "request",  # Marking it as a request
                    "parent": parent_id if parent_id else None,
                    "method": item["request"].get("method", "GET"),
                    "raw_url": raw_url,
                    "queryParams": extract_query_params(raw_url),
                    "body": extract_request_body(item["request"]),
                    "tests": extract_tests(item.get("event", []))
                }
                generic_controllers.append(request_data)

    return generic_controllers


def extract_query_params(raw_url):
    parsed_url = urlparse(raw_url)
    query_params = parse_qsl(parsed_url.query)  # Parse the query parameters as a list of tuples

    # Convert the list of tuples into a list of dictionaries for a structured format
    formatted_params = [{param: value} for param, value in query_params]

    return formatted_params if formatted_params else "No query parameters"


def extract_request_body(request):
    # Check if the body exists and get the relevant information
    if "body" in request and request["body"].get("mode"):
        mode = request["body"]["mode"]

        if mode == "raw":
            # Return the raw body content, defaulting to a message if not present
            return request["body"].get("raw", "No raw body content")

        elif mode == "formdata":
            # Return the form data as a list of dictionaries
            return [{"key": item["key"], "value": item["value"]} for item in request["body"].get("formdata", [])]

        elif mode == "x-www-form-urlencoded":
            # Return the URL-encoded data as a list of dictionaries
            return [{"key": item["key"], "value": item["value"]} for item in request["body"].get("urlencoded", [])]

        elif mode == "file":
            # Handling file uploads (if necessary)
            return "File upload not supported in JSON output"

    return "No body content"  # Default return if no body is provided


def extract_tests(events):
    test_scripts = []

    for event in events:
        if event.get("listen") == "test":
            script_content = event.get("script", {}).get("exec", [])
            test_cases = extract_pm_tests(script_content)
            test_scripts.extend(test_cases)

    # Trim the script content for each test case
    for test in test_scripts:
        test["script"] = test["script"].strip()

    return test_scripts


def extract_pm_tests(script_lines):
    tests = []
    pm_test_pattern = re.compile(r'pm\.test\(\"(.*?)\"')
    current_test = None

    for line in script_lines:
        match = pm_test_pattern.search(line)
        if match:
            # If we already have a current_test, save it first
            if current_test:
                tests.append(current_test)

            # Start a new test with name
            current_test = {"name": match.group(1), "script": ""}
        elif current_test:
            # Accumulate script lines for the current test
            current_test["script"] += line.strip() + " "

    # Append the last test
    if current_test:
        tests.append(current_test)

    return tests