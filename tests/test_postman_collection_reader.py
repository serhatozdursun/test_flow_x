import os
import pytest
from jsonschema import validate, ValidationError
from postman.postman_json_reader import (
    read_postman_collection,
    extract_generic_controllers,
    extract_query_params,
    extract_request_body,
    extract_tests,
    extract_pm_tests
)

# JSON Schema for validation
schema = {
    "type": "object",
    "properties": {
        "test_plan_name": {"type": "string"},
        "test_plan_comments": {"type": "string"},
        "test_fragment_controller": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "generic_controllers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "parent": {"type": ["string", "null"]},
                            "children": {"type": "array"},
                            "method": {"type": "string"},
                            "raw_url": {"type": "string"},
                            "queryParams": {"type": "array"},
                            "body": {"type": "string"},
                            "tests": {"type": "array"}
                        },
                        "required": ["id", "name", "type"]
                    }
                }
            },
            "required": ["name", "generic_controllers"]
        }
    },
    "required": ["test_plan_name", "test_plan_comments", "test_fragment_controller"]
}


@pytest.fixture
def sample_json_path():
    return os.path.join(os.path.dirname(__file__), '../file_to_convert/sample_collection.json')


def test_read_postman_collection(sample_json_path):
    result = read_postman_collection(sample_json_path)
    assert result is not None
    try:
        validate(instance=result, schema=schema)
    except ValidationError as e:
        pytest.fail(f"Validation error: {e.message}")

def test_extract_query_params():
    url = "https://api.example.com/data?param1=value1&param2=value2"
    expected_params = [{"param1": "value1"}, {"param2": "value2"}]
    result = extract_query_params(url)
    assert result == expected_params


def test_extract_request_body():
    request_body = {
        "body": {
            "mode": "raw",
            "raw": "sample body content"
        }
    }
    result = extract_request_body(request_body)  # Pass the full request_body, not just request_body["body"]
    assert result == "sample body content"


def test_extract_tests():
    events = [
        {
            "listen": "test",
            "script": {
                "exec": [
                    "pm.test(\"Test 1\", function() {",
                    "    pm.expect(true).to.be.true;",
                    "});"
                ]
            }
        }
    ]
    result = extract_tests(events)
    assert len(result) == 1
    assert result[0]["name"] == "Test 1"


def test_extract_pm_tests():
    script_lines = [
        "pm.test(\"Test 1\", function() {",
        "    pm.expect(true).to.be.true;",
        "});",
        "pm.test(\"Test 2\", function() {",
        "    pm.expect(false).to.be.false;",
        "});"
    ]
    result = extract_pm_tests(script_lines)
    assert len(result) == 2
    assert result[0]["name"] == "Test 1"
    assert result[1]["name"] == "Test 2"


def test_extract_generic_controllers_empty():
    """Test with empty input."""
    result = extract_generic_controllers({})
    assert result == []


def test_extract_generic_controllers_no_controllers():
    """Test with data that does not have a controllers key."""
    data = {
        "settings": {
            "theme": "dark"
        }
    }
    result = extract_generic_controllers(data)
    assert result == []

