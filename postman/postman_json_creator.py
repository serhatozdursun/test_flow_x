import os

from helper.id_utils import generate_uuid, generate_id
from jmx.jmx_reader import get_test_plan
import json


def generate_postman_collection(file_path):
    jmx_data = get_test_plan(file_path)
    postman_collection = generate_info(jmx_data)
    items = extract_items(jmx_data)

    # Adding items to the collection
    postman_collection['item'] = items

    return postman_collection


def generate_info(jmx_data: dict):
    collection_name = jmx_data["name"]
    return {
        "info": {
            "_postman_id": generate_uuid(),
            "name": collection_name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "_exporter_id": generate_id()
        }
    }


def extract_items(jmx_data: dict):
    items = []
    jmx_items = jmx_data['items']

    for jmx_item in jmx_items:
        item_data = jmx_item["item"]
        item_name = item_data["name"]

        # Prepare the structure for the Postman item
        postman_item = {
            "name": item_name,
            "item": extract_sub_items(item_data)  # Recursively extract sub-controller items
        }
        items.append(postman_item)

    return items


def extract_sub_items(item_data: dict):
    sub_items = []
    if "requests" in item_data:
        requests = item_data["requests"]
        for request in requests:
            postman_request = {
                "name": request["name"],
                "request": {
                    "auth": {"type": None},  # No auth type specified in the provided JMX
                    "method": request["method"],
                    "header": [],  # No headers provided in the original structure
                    "url": generate_url(request),  # Generate URL including query parameters
                    "body": generate_body(request) if request["method"] in ["POST", "PUT"] else None
                    # Handle POST/PUT body
                },
                "response": []
            }
            # Add event handling for "test" and "prerequest" if needed
            postman_request["event"] = generate_events()
            sub_items.append(postman_request)

    # Handle sub-controllers recursively
    if "sub_controller" in item_data:
        for sub_controller in item_data["sub_controller"]:
            sub_item = sub_controller["item"]
            sub_items.append({
                "name": sub_item["name"],
                "item": extract_sub_items(sub_item)
            })

    return sub_items


def is_special_argument(value: str) -> bool:
    """Check if the argument contains newline or quotes, and thus should be moved to the body."""
    return "\r\n" in value or "\"" in value


def generate_url(request: dict):
    """Generate the URL structure for a request based on path and arguments."""
    raw_url = request["path"]
    query_params = []

    # Assuming request["arguments"] contains only query parameters, not body data
    for key, value in request.get("arguments", {}).items():
        if key == "body":  # Move the 'body' argument to the query instead of body
            query_params.append({
                "key": key,
                "value": value
            })
        elif not is_special_argument(value) and key != "url":  # Only add to query if not special
            query_params.append({
                "key": key,
                "value": value
            })

    return {
        "raw": raw_url,  # Assuming path is always raw in the JMX
        "host": [],  # Host will be extracted from the JMX or Postman environment variables
        "path": raw_url.split('/'),  # Split the path into an array
        "query": query_params  # Attach the query parameters
    }


def generate_body(request: dict):
    """Generate the body for POST requests."""
    if request.get("arguments"):
        body_data = {}

        # Check if "body" exists in arguments and if it's a string (raw JSON).
        if "body" in request["arguments"] and isinstance(request["arguments"]["body"], str):
            # Directly use the "body" value as raw JSON.
            return {
                "mode": "raw",
                "raw": request["arguments"]["body"],
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }
        else:
            # Otherwise, process arguments normally as JSON.
            for key, value in request["arguments"].items():
                if key == "url":
                    # If the argument is 'url', it should be in the body and not in the query.
                    body_data[key] = value
                elif isinstance(value, dict):  # If the argument is already JSON, format it as raw
                    body_data[key] = json.dumps(value, indent=4)
                else:
                    body_data[key] = value

            # Formatting the body as raw JSON
            return {
                "mode": "raw",
                "raw": generate_raw_json(body_data),
                "options": {
                    "raw": {
                        "language": "json"
                    }
                }
            }

    return None


def generate_events():
    """Generate the events for pre-request and test scripts."""
    return [
        {
            "listen": "test",
            "script": {
                "type": "text/javascript",
                "exec": []  # You can add Postman script logic here
            }
        },
        {
            "listen": "prerequest",
            "script": {
                "type": "text/javascript",
                "exec": []  # You can add pre-request script logic here
            }
        }
    ]


def save_json(file_path, data):
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    GREEN_TEXT = '\033[92m'
    print(f'{GREEN_TEXT}Postman collection JSON file created at: {file_path}')


def create_postman_collection(source_file, output_path):
    current_file_dir = os.path.dirname(__file__)
    parent_folder_path = os.path.abspath(os.path.join(current_file_dir, os.pardir))
    if not os.path.exists(source_file):
        # Get the parent directory
        jmeter_jmx_path_final = os.path.join(parent_folder_path, "file_to_convert", f"{source_file}.jmx")
    else:
        jmeter_jmx_path_final = source_file

    if ".json" not in output_path:
        output_path = os.path.join(parent_folder_path, f"out/{output_path}.json")

    postman_collection = generate_postman_collection(jmeter_jmx_path_final)
    save_json(output_path, postman_collection)


if __name__ == '__main__':
    file_path = "/Users/sozdursun/PycharmProjects/test_flow_x/file_to_convert/hot_topic.jmx"
    postman_collection = generate_postman_collection(file_path)

    # Define the output path and file name
    output_path = os.path.abspath(os.path.join(file_path, os.pardir))
    file_name = os.path.basename(file_path).replace('.jmx', '_postman_collection.json')

    # Save the Postman collection as a JSON file
    save_json(output_path, postman_collection)
