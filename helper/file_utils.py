import os
import json


def file_load(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as schema:
            return schema.read()
    else:
        raise FileNotFoundError('File not found')


def file_write(file_path, file_name, file_content=None):
    """
    Writes the provided content to a file at the specified path.
    If file_content is None, it loads the content from the existing file.

    This function ensures that the directory exists and removes the file if it
    already exists (unless loading). If the content is not a string, it attempts
    to convert it to a string using JSON serialization. If serialization fails,
    it uses the built-in `str()` function as a fallback.

    Parameters:
        file_path (str): The directory path where the file will be created.
        file_name (str): The name of the file to be created or overwritten.
        file_content (any, optional): The content to be written to the file.
                                      If None, it will load the content from
                                      the existing file.

    Raises:
        FileNotFoundError: If loading from an existing file and the file does not exist.

    Example:
        file_write('path/to/directory', 'example.txt', {'key': 'value'})
        file_write('path/to/directory', 'example.txt')  # To load the content
    """
    # Construct the full file path
    full_file_path = os.path.join(file_path, file_name)

    # Ensure the directory exists
    if not os.path.exists(file_path):
        os.makedirs(file_path)

    # If file_content is None, attempt to load the content from the file
    if file_content is None:
        if os.path.exists(full_file_path):
            return file_load(full_file_path)
        else:
            raise FileNotFoundError('File not found')

    # Remove the file if it already exists and content is not None
    if os.path.exists(full_file_path):
        os.remove(full_file_path)

    # Check if the content is a string, if not, convert it to string
    if not isinstance(file_content, str):
        try:
            # Attempt to convert to JSON string if the content is a list or dict
            with open(full_file_path, 'w') as json_file:
                json.dump(file_content, json_file, indent=4)
        except (TypeError, ValueError):
            # Fallback to using str() for other types
            file_content = str(file_content)
    else:
        # Write the content to the file
        with open(full_file_path, 'w') as jmx_file:
            jmx_file.write(file_content)


