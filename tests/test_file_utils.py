import os
import json
import pytest
from src.helper.file_utils import file_load, file_write  # Replace with your module


# Test for file_load function

def test_file_load_success(mocker):
    """Test loading a file when it exists."""
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_open = mocker.mock_open(read_data='file content')
    mocker.patch('builtins.open', mock_open)

    file_path = 'some/file/path.txt'
    result = file_load(file_path)

    mock_exists.assert_called_once_with(file_path)
    mock_open.assert_called_once_with(file_path, 'r')
    assert result == 'file content'


def test_file_load_file_not_found(mocker):
    """Test loading a file when it does not exist."""
    mocker.patch('os.path.exists', return_value=False)
    file_path = 'non/existing/path.txt'

    with pytest.raises(FileNotFoundError, match='File not found'):
        file_load(file_path)


# Test for file_write function

def test_file_write_directory_creation(mocker):
    """Test file_write when directory does not exist and needs to be created."""
    mock_exists = mocker.patch('os.path.exists', side_effect=[False, False])
    mock_makedirs = mocker.patch('os.makedirs')
    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)

    file_path = 'new/directory'
    file_name = 'file.txt'
    file_content = 'content'

    file_write(file_path, file_name, file_content)

    assert mock_exists.call_args_list[0].args[0] == file_path
    assert mock_exists.call_args_list[1].args[0] == os.path.join(file_path, file_name)
    mock_exists.call_count = 2
    mock_makedirs.assert_called_once_with(file_path)
    mock_open.assert_called_once_with(os.path.join(file_path, file_name), 'w')
    mock_open().write.assert_called_once_with(file_content)


def test_file_write_load_existing_content(mocker):
    """Test file_write loading content when file_content is None and file exists."""
    # Mock os.path.exists to always return True
    mock_exists = mocker.patch('os.path.exists', return_value=True)
    mock_open = mocker.mock_open(read_data='existing content')
    mocker.patch('builtins.open', mock_open)

    file_path = 'some/path'
    file_name = 'file.txt'

    result = file_write(file_path, file_name, None)

    mock_exists.assert_called_with(os.path.join(file_path, file_name))
    mock_open.assert_called_once_with(os.path.join(file_path, file_name), 'r')
    assert result == 'existing content'


def test_file_write_file_not_found_on_load(mocker):
    """Test file_write raises FileNotFoundError when file_content is None but file doesn't exist."""
    with pytest.raises(FileNotFoundError, match='File not found'):
        file_write('some/path', 'file.txt', None)


def test_file_write_remove_existing_file(mocker):
    """Test file_write removing the file if it already exists and content is not None."""
    mock_exists = mocker.patch('os.path.exists', side_effect=[True, True])
    mock_remove = mocker.patch('os.remove')
    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)

    file_path = 'some/path'
    file_name = 'file.txt'
    file_content = 'new content'

    file_write(file_path, file_name, file_content)

    mock_remove.assert_called_once_with(os.path.join(file_path, file_name))
    mock_open.assert_called_once_with(os.path.join(file_path, file_name), 'w')
    mock_open().write.assert_called_once_with(file_content)
    assert mock_exists.call_count == 2


def test_file_write_json_serialization(mocker):
    """Test file_write when content is a dictionary (it should be JSON serialized)."""
    mock_exists = mocker.patch('os.path.exists', side_effect=[True, False])
    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)

    file_path = 'some/path'
    file_name = 'file.txt'
    full_path = os.path.join(file_path, file_name)
    file_content = {'key': 'value'}

    file_write(file_path, file_name, file_content)

    mock_open.assert_called_once_with(os.path.join(file_path, file_name), 'w')
    arguments = mock_open().write.call_args_list
    content = ""
    for item in arguments:
        content += str(item.args[0])
    assert content == json.dumps(file_content, indent=4)
    assert file_path == mock_exists.call_args_list[0].args[0]
    assert full_path == mock_exists.call_args_list[1].args[0]


def test_file_write_fallback_to_str(mocker):
    """Test file_write falling back to string serialization when JSON serialization fails."""
    mock_exists = mocker.patch('os.path.exists', side_effect=[True, False])
    mock_open = mocker.mock_open()
    mocker.patch('builtins.open', mock_open)

    file_path = 'some/path'
    file_name = 'file.txt'
    file_content = set([1, 2, 3])  # Set is not JSON serializable

    file_write(file_path, file_name, file_content)

    mock_open.assert_called_once_with(os.path.join(file_path, file_name), 'w')
    assert mock_exists.call_count == 2