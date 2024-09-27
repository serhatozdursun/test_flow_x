import os


def file_load(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as schema:
            return schema.read()
    else:
        raise FileNotFoundError('File not found')


def file_write(file_path, file_name, file_content):
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    file_path = os.path.join(file_path, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w') as jmx_file:
        jmx_file.write(file_content)
