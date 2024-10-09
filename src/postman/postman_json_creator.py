import os
import json
from src.helper.file_utils import file_write
from src.helper.id_utils import generate_uuid, generate_id
from src.jmx.jmx_reader import get_test_plan
import logging

# Constants
BODY_KEY = "body"
URL_KEY = "url"
RAW_KEY = "raw"
QUERY_KEY = "query"

logging.basicConfig(level=logging.ERROR)


def create_postman_collection(source_file: str, output_path: str) -> None:
    """
    Create a Postman collection by converting a JMX file.

    Args:
        source_file (str): The name of the source JMX file.
        output_path (str): The path where the Postman collection will be saved.
    """
    current_file_dir = os.path.dirname(__file__)
    parent_folder_path = os.path.abspath(os.path.join(current_file_dir, os.pardir))
    jmeter_jmx_path_final = os.path.join(parent_folder_path, "file_to_convert",
                                         f"{source_file}.jmx") if not os.path.exists(source_file) else source_file

    if not output_path.endswith(".json"):
        output_path = os.path.join(parent_folder_path, f"out/{output_path}.json")

    collection = generate_postman_collection(jmeter_jmx_path_final)
    save_json(output_path, collection)


def generate_postman_collection(file_path: str) -> dict:
    """
    Generate a Postman collection from a JMX test plan.

    Args:
        file_path (str): The path to the JMX file.

    Returns:
        dict: A dictionary representing the Postman collection.
    """
    jmx_data = get_test_plan(file_path)
    postman_collection = generate_info(jmx_data)
    items = extract_items(jmx_data)

    # Adding items to the collection
    postman_collection['item'] = items
    return postman_collection


def generate_info(jmx_data: dict) -> dict:
    """
    Generate the info section of the Postman collection.

    Args:
        jmx_data (dict): The JMX data.

    Returns:
        dict: A dictionary containing the collection info.
    """
    return {
        "info": {
            "_postman_id": generate_uuid(),
            "name": jmx_data["name"],
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_exporter_id": generate_id()
        }
    }


def extract_items(jmx_data: dict) -> list:
    """
    Extract items from JMX data.

    Args:
        jmx_data (dict): The JMX data.

    Returns:
        list: A list of extracted items for the Postman collection.
    """
    items = []
    for jmx_item in jmx_data['items']:
        item_data = jmx_item["item"]
        postman_item = {
            "name": item_data["name"],
            "item": extract_sub_items(item_data)  # Recursively extract sub-controller items
        }
        items.append(postman_item)
    return items


def extract_sub_items(item_data: dict) -> list:
    """
    Extract sub-items (requests) from item data and check for duplicates.

    Args:
        item_data (dict): The item data containing requests.

    Returns:
        list: A list of sub-items (requests) for the Postman collection.
    """
    sub_items = []
    seen_requests = set()

    if "requests" in item_data:
        for request in item_data["requests"]:
            request_name = request["name"]

            if not add_unique_request_to_collection(request_name, seen_requests, sub_items, request, item_data["name"]):
                continue

    return sub_items


def add_unique_request_to_collection(request_name, seen_requests, sub_items, request, item_name):
    """
    Check for duplicates and add a unique request to the collection.

    Args:
        request_name (str): The name of the request.
        seen_requests (set): Set of already processed request names.
        sub_items (list): The list of current sub-items (requests) in the collection.
        request (dict): The request data.
        item_name (str): The name of the item the request belongs to.

    Returns:
        bool: True if the request is added, False if it is skipped (duplicate).
    """
    if request_name in seen_requests:
        logging.warning(f"Duplicate request '{request_name}' detected in '{item_name}'. Skipping.")
        return False

    body = generate_body(request) if request.get("arguments", {}).get(BODY_KEY) is not None else None
    postman_request = {
        "name": request_name,
        "request": {
            "auth": {"type": None},
            "method": request["method"],
            "header": [],  # No headers provided in the original structure
            "url": generate_url(request),
            "body": body
        },
        "response": [],
        "event": generate_events()
    }

    sub_items.append(postman_request)
    seen_requests.add(request_name)
    return True


def generate_events():
    """
    Generates events for the Postman request.
    This could include pre-request and test scripts, for example.
    """
    return [
        {
            "listen": "test",
            "script": {
                "exec": [
                    "pm.test('Response time is less than 200ms', function() { pm.response.to.have.responseTime.lessThan(200); });"],
                "type": "text/javascript"
            }
        }
    ]


def generate_url(request: dict) -> dict:
    """
    Generate the URL structure for a Postman request.

    Args:
        request (dict): The request data.

    Returns:
        dict: A dictionary representing the URL for the Postman request.
    """
    raw_url = request["path"]
    query_params = extract_query_params(request.get("arguments", {}))

    return {
        "raw": raw_url,
        "host": [],  # Host will be extracted from the JMX or Postman environment variables
        "path": raw_url.split('/'),
        QUERY_KEY: query_params
    }


def extract_query_params(arguments: dict) -> list:
    """
    Extract query parameters from request arguments.

    Args:
        arguments (dict): The arguments containing query parameters.

    Returns:
        list: A list of query parameter dictionaries.
    """
    query_params = []
    for key, value in arguments.items():
        if key != BODY_KEY and not is_special_argument(value):
            query_params.append({"key": key, "value": replace_placeholders(value)})
    return query_params


def is_special_argument(value: str) -> bool:
    """
    Check if the argument contains newline or quotes.

    Args:
        value (str): The argument value to check.

    Returns:
        bool: True if the argument is special; False otherwise.
    """
    return "\r\n" in value or "\"" in value


def generate_body(request: dict) -> dict:
    """
    Generate the body for POST requests.

    Args:
        request (dict): The request data.

    Returns:
        dict: A dictionary representing the body for the Postman request.
    """
    arguments = request.get("arguments", {})
    if BODY_KEY in arguments and isinstance(arguments[BODY_KEY], str):
        body = generate_raw_json(arguments[BODY_KEY])
        return {
            "mode": "raw",
            "raw": body,
            "options": {
                "raw": {
                    "language": "json"
                }
            }
        }

    body_data = {key: (json.dumps(value, indent=4) if isinstance(value, dict) else value) for key, value in
                 arguments.items() if key != URL_KEY}
    body_data[URL_KEY] = arguments.get(URL_KEY)

    return {
        "mode": "raw",
        "raw": generate_raw_json(body_data),
        "options": {
            "raw": {
                "language": "json"
            }
        }
    }


def generate_raw_json(body_data) -> str:
    """
    Convert the body data dictionary or list into a formatted JSON string.

    Args:
        body_data: The body data to convert.

    Returns:
        str: A formatted JSON string representation of the body data.

    Raises:
        ValueError: If body_data is neither a dict nor a list.
    """
    try:
        # If body_data is a string, attempt to convert it to a dictionary
        if isinstance(body_data, str):
            body_data = json.loads(body_data)

        # Determine if body_data is a list or a dictionary
        if isinstance(body_data, dict):
            # Process dictionary
            converted_body = {
                key: replace_placeholders(value) for key, value in body_data.items()
            }
        elif isinstance(body_data, list):
            # Process list
            converted_body = [
                {key: replace_placeholders(value) for key, value in item.items()} for item in body_data
            ]
        else:
            raise ValueError("Invalid data type: expected dict or list.")

        # Return formatted JSON string
        return json.dumps(converted_body, indent=4)

    except json.JSONDecodeError as e:
        logging.error(f"JSON Decode Error: Invalid JSON string provided. Error: {e}")
        raise
    except AttributeError as e:
        logging.error(f"Attribute Error building the raw json body, the body: {body_data}, \n error:{e}")
        raise
    except Exception as e:
        logging.error(f"Error building the raw json body, the body: {body_data}, \n error:{e}")
        raise


def replace_placeholders(value):
    """
    Recursively convert placeholders from ${key} to {{key}}.

    Args:
        value: The value to process (string, dict, or list).

    Returns:
        The processed value with placeholders replaced.
    """
    if isinstance(value, str):
        return value.replace("${", "{{").replace("}", "}}")
    elif isinstance(value, dict):
        return {k: replace_placeholders(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [replace_placeholders(item) for item in value]
    else:
        return value


def save_json(file_path: str, data: dict) -> None:
    """
    Save the generated JSON data to a file.

    Args:
        file_path (str): The path where the JSON file will be saved.
        data (dict): The data to save in JSON format.
    """
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    file_write(file_dir, file_name, data)
