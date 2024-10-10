import json
import os
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, parse_qsl
from jsonschema import validate, ValidationError
from src.helper.file_utils import file_load  # Assuming this function exists and is imported correctly


def validate_postman_schema(data: Dict[str, Any], schema_file_path: str = 'data/postman_schema.json') -> None:
    """
    Validates a Postman collection against a JSON schema.
    """
    try:
        schema = json.loads(file_load(schema_file_path))
        validate(instance=data, schema=schema)
    except ValidationError as e:
        raise ValidationError(f"Error: The provided file does not conform to the Postman Collection schema. \n {e}")


def read_postman_collection(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Reads a Postman collection from a JSON file and validates it against the schema.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Error: The file '{file_path}' does not exist.")

    data: Dict[str, Any] = {}
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON - {e}")
        return None

    validate_postman_schema(data)

    info = data.get("info", {})
    test_plan_name = info.get("name", "Unnamed Test Plan").replace("&", "and")
    test_plan_comments = info.get("description", "No description found")

    generic_controllers = extract_generic_controllers(data.get("item", []))

    return {
        "test_plan_name": test_plan_name,
        "test_plan_comments": test_plan_comments,
        "test_fragment_controller": {
            "name": "Test Fragment",
            "generic_controllers": generic_controllers
        }
    }


def extract_generic_controllers(items: List[Dict[str, Any]], parent_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Extracts generic controllers and requests from the Postman collection items.
    """
    generic_controllers: List[Dict[str, Any]] = []
    controller_id_counter = 1

    for item in items:
        controller_id = f"controller_{controller_id_counter}"
        controller_id_counter += 1

        if "item" in item:  # Indicates it's a folder-like structure
            controller = {
                "id": controller_id,
                "name": item.get("name", "Unnamed Controller").replace("&", "and"),
                "type": "generic_controller" if not parent_id else "child_generic_controller",
                "parent": parent_id,
                "children": extract_generic_controllers(item.get("item", []), parent_id=controller_id)
            }
            generic_controllers.append(controller)
        else:  # It's a request
            if "request" in item:
                request_data = extract_request_data(item, controller_id, parent_id)
                generic_controllers.append(request_data)

    return generic_controllers


def extract_request_data(item: Dict[str, Any], controller_id: str, parent_id: Optional[str]) -> Dict[str, Any]:
    """
    Extracts the relevant data from a request item.
    """
    raw_url = item["request"].get("url", {}).get("raw", "No URL")
    raw_url = re.sub(r'{{', '${', raw_url)
    raw_url = re.sub(r'}}', '}', raw_url)
    raw_url = re.sub(r'\.', '_', raw_url)
    name = item.get("name", "Unnamed Request").replace("&", "and")

    return {
        "id": controller_id,
        "name": name,
        "type": "request",
        "parent": parent_id,
        "method": item["request"].get("method", "GET"),
        "raw_url": raw_url,
        "queryParams": extract_query_params(raw_url),
        "body": extract_request_body(item["request"]),
        "tests": extract_tests(item.get("event", []))
    }


def extract_query_params(raw_url: str) -> List[Dict[str, str]]:
    """
    Extracts query parameters from a raw URL.
    """
    parsed_url = urlparse(raw_url)
    query_params = parse_qsl(parsed_url.query)
    return [{param: value} for param, value in query_params] if query_params else [{"No query parameters": ""}]


def extract_request_body(request: Dict[str, Any]) -> Any:
    """
    Extracts the body content from a request.
    """
    if "body" in request and request["body"] is not None and request["body"].get("mode"):
        mode = request["body"]["mode"]
        body_data = request["body"].get(mode, None)
        return process_body_data(mode, body_data)

    return "No body content"


def process_body_data(mode: str, body_data: Any) -> Any:
    """
    Processes the body data based on its mode.
    """
    if mode == "raw":
        return body_data  # Return raw body directly
    elif mode == "formdata":
        return [{"key": item["key"], "value": item["value"]} for item in body_data] if body_data else []
    elif mode == "urlencoded":
        return [{"key": item["key"], "value": item["value"]} for item in body_data] if body_data else []
    elif mode == "file":
        return "File upload not supported in JSON output"
    return "No body content"


def extract_tests(events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Extracts test scripts from Postman events.
    """
    test_scripts: List[Dict[str, str]] = []

    for event in events:
        if event.get("listen") == "test":
            script_content = event.get("script", {}).get("exec", [])
            test_cases = extract_pm_tests(script_content)
            test_scripts.extend(test_cases)

    for test in test_scripts:
        test["script"] = test["script"].strip()

    return test_scripts


def extract_pm_tests(script_lines: List[str]) -> List[Dict[str, str]]:
    """
    Extracts individual tests from Postman test scripts.
    """
    tests: List[Dict[str, str]] = []
    pm_test_pattern = re.compile(r'pm\.test\(\"(.*?)\"')
    current_test: Optional[Dict[str, str]] = None

    for line in script_lines:
        match = pm_test_pattern.search(line)
        if match:
            if current_test:
                tests.append(current_test)

            current_test = {"name": match.group(1), "script": ""}
        elif current_test:
            current_test["script"] += line.strip() + " "

    if current_test:
        tests.append(current_test)

    return tests