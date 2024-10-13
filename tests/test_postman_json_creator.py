import pytest
from src.postman.postman_json_creator import (
    create_postman_collection,
    generate_postman_collection,
    save_json,
    generate_info,
    extract_items,
    replace_placeholders
)


# Mocking dependencies
@pytest.fixture
def mock_os_path(mocker):
    return mocker.patch("os.path")


@pytest.fixture
def mock_get_test_plan(mocker):
    return mocker.patch('src.postman.postman_json_creator.get_test_plan')


@pytest.fixture
def mock_generate_uuid(mocker):
    return mocker.patch('src.postman.postman_json_creator.generate_uuid')


@pytest.fixture
def mock_generate_id(mocker):
    return mocker.patch('src.postman.postman_json_creator.generate_id')


@pytest.fixture
def mock_file_write(mocker):
    return mocker.patch('src.postman.postman_json_creator.file_write')


@pytest.fixture
def mock_save_json(mocker):
    return mocker.patch('src.postman.postman_json_creator.save_json')


# Test for create_postman_collection
def test_create_postman_collection(mock_os_path, mock_get_test_plan, mock_file_write, mock_save_json, mocker):
    # Arrange
    source_file = 'test'
    output_path = 'test_output'
    mock_os_path.exists.return_value = False
    mock_generate_postman_collection = mocker.patch('src.postman.postman_json_creator.generate_postman_collection')
    # Act
    create_postman_collection(source_file, output_path)

    # Assert
    mock_generate_postman_collection.assert_called_once_with(mocker.ANY)
    mock_save_json.assert_called_once()


# Test for generate_postman_collection
def test_generate_postman_collection(mock_get_test_plan, mock_generate_uuid, mock_generate_id, mocker):
    # Arrange
    file_path = 'test.jmx'
    mock_jmx_data = {'name': 'Test', 'items': [
        {'item': {'name': 'item1', 'requests': [{'name': 'req1', 'method': 'GET', 'path': 'example.com'}]}}]}
    mock_get_test_plan.return_value = mock_jmx_data
    mock_generate_uuid.return_value = 'mock_uuid'
    mock_generate_id.return_value = 'mock_id'

    # Act
    collection = generate_postman_collection(file_path)

    # Assert
    assert collection['info']['_postman_id'] == 'mock_uuid'
    assert collection['info']['_exporter_id'] == 'mock_id'
    assert collection['item'][0]['name'] == 'item1'


# Test for save_json
def test_save_json(mock_file_write, mock_os_path):
    # Arrange
    file_path = 'test_output.json'
    data = {'key': 'value'}
    mock_os_path.dirname.return_value = "dirname"
    mock_os_path.basename.return_value = "basename"
    # Act
    save_json(file_path, data)

    # Assert
    assert mock_os_path.dirname.call_args_list[0].args[0] == file_path
    assert mock_os_path.dirname.call_count == 1
    mock_os_path.basename.assert_called_once_with(file_path)
    mock_file_write.assert_called_once_with('dirname', 'basename', data)


# Test for generate_info
def test_generate_info(mock_generate_uuid, mock_generate_id):
    # Arrange
    jmx_data = {'name': 'test_jmx'}
    mock_generate_uuid.return_value = 'mock_uuid'
    mock_generate_id.return_value = 'mock_id'

    # Act
    info = generate_info(jmx_data)

    # Assert
    assert info['info']['_postman_id'] == 'mock_uuid'
    assert info['info']['_exporter_id'] == 'mock_id'
    assert info['info']['name'] == 'test_jmx'


# Test for extract_items
def test_extract_items():
    # Arrange
    jmx_data = {
        'items': [
            {
                'item': {
                    'name': 'item1',
                    'requests': [{'name': 'req1', 'method': 'GET', 'path': 'example.com'}]
                }
            }
        ]
    }

    # Act
    items = extract_items(jmx_data)

    # Assert
    assert items[0]['name'] == 'item1'


# Test for replace_placeholders
def test_replace_placeholders():
    # Arrange
    value = '${example}'

    # Act
    replaced = replace_placeholders(value)

    # Assert
    assert replaced == '{{example}}'
