import json
import pytest
from jsonschema import ValidationError
from pathlib import Path
from unittest.mock import patch, mock_open
from src.postman.postman_json_reader import (
    get_schema_path,
    validate_postman_schema,
    read_postman_collection,
    extract_generic_controllers,
    extract_request_data,
    extract_query_params,
    extract_request_body,
    extract_tests
)

MOCK_SCHEMA = {
    "id": "https://example.com/example.json",
    "type": "object",
    "required": ["key"],
    "properties": {
        "key": {
            "type": "string"
        }
    }
}


# Test get_schema_path
def test_get_schema_path():
    relative_path = "schemas/postman_schema.json"
    result = get_schema_path(relative_path)
    expected_path = Path(__file__).resolve().parent.parents[0] / relative_path
    assert result == expected_path


# Test validate_postman_schema for successful validation
@patch('src.postman.postman_json_reader.file_load')
@patch('src.postman.postman_json_reader.validate')
def test_validate_postman_schema_valid(m_validate, m_file_load):
    mock_data = {"key": "value"}
    m_file_load.return_value = json.dumps(MOCK_SCHEMA)

    # This should pass without exceptions
    validate_postman_schema(mock_data)

    schema_path = get_schema_path('data/postman_schema.json')
    m_file_load.assert_called_once_with(str(schema_path))
    assert m_validate.call_args_list[0].kwargs["instance"] == mock_data
    assert m_validate.call_args_list[0].kwargs["schema"] == MOCK_SCHEMA
    assert m_validate.call_count == 1


# Test validate_postman_schema for schema validation error
@patch('src.postman.postman_json_reader.file_load')
@patch('src.postman.postman_json_reader.validate', side_effect=ValidationError("Invalid schema"))
def test_validate_postman_schema_invalid(m_validate, m_file_load):
    mock_data = {"key": "value"}
    invalid_schema = {"schema_key": "schema_value"}
    m_file_load.return_value = json.dumps({"schema_key": "schema_value"})

    with pytest.raises(ValidationError, match="Schema validation error"):
        validate_postman_schema(mock_data)

    assert m_validate.call_args_list[0].kwargs["instance"] == mock_data
    assert m_validate.call_args_list[0].kwargs["schema"] == invalid_schema
    assert m_validate.call_count == 1

# Test read_postman_collection for file not found
def test_read_postman_collection_file_not_found():
    with pytest.raises(FileNotFoundError):
        read_postman_collection("invalid_path.json")


# Test read_postman_collection for successful reading and validation
@patch('src.postman.postman_json_reader.validate_postman_schema')
@patch('builtins.open', new_callable=mock_open,
       read_data='{"info": {"name": "Test Plan", "description": "Description"}, "item": []}')
@patch('os.path.isfile', return_value=True)
def test_read_postman_collection_valid(mock_open_file, mock_validate_postman_schema, mock_is_file, mocker):
    valid_path = "valid_path.json"
    result = read_postman_collection(valid_path)

    assert result["test_plan_name"] == "Test Plan"
    assert result["test_plan_comments"] == "Description"
    assert result["test_fragment_controller"]["name"] == "Test Fragment"

    mock_open_file.assert_called_once_with(valid_path)
    assert mock_validate_postman_schema.call_args.args[0] == valid_path
    assert mock_validate_postman_schema.call_args.args[1] == "r"
    mock_is_file.assert_called_once_with(mocker.ANY)

# Test extract_generic_controllers for folder structure
def test_extract_generic_controllers_folder_structure():
    items = [
        {"name": "Folder 1", "item": [{"name": "Subfolder 1", "item": []}]},
        {"name": "Folder 2", "item": []}
    ]

    result = extract_generic_controllers(items)

    assert len(result) == 2
    assert result[0]["name"] == "Folder 1"
    assert result[0]["type"] == "generic_controller"
    assert result[0]["children"][0]["name"] == "Subfolder 1"
    assert result[1]["name"] == "Folder 2"


# Test extract_request_data for request
def test_extract_request_data():
    item = {
        "name": "Request 1",
        "request": {
            "method": "POST",
            "url": {"raw": "https://example.com"},
            "body": {"mode": "raw", "raw": "some body content"}
        }
    }

    result = extract_request_data(item, "controller_1", None)

    assert result["name"] == "Request 1"
    assert result["method"] == "POST"
    assert result["raw_url"] == "https://example.com"


# Test extract_query_params
def test_extract_query_params():
    raw_url = "https://example.com?param1=value1&param2=value2"

    result = extract_query_params(raw_url)

    assert result == [{"param1": "value1"}, {"param2": "value2"}]


# Test extract_request_body with raw body
def test_extract_request_body_raw():
    request = {"body": {"mode": "raw", "raw": "sample body"}}

    result = extract_request_body(request)

    assert result == "sample body"


# Test extract_request_body with no body
def test_extract_request_body_no_body():
    request = {}

    result = extract_request_body(request)

    assert result == "No body content"


# Test extract_tests with valid tests
def test_extract_tests():
    events = [
        {"listen": "test",
         "script": {"exec": ['pm.test("Test 1", function () {});', 'pm.test("Test 2", function () {});']}}
    ]

    result = extract_tests(events)

    assert len(result) == 2
    assert result[0]["name"] == "Test 1"
    assert result[1]["name"] == "Test 2"