import os

def write_file(working_directory, file_path, content):
    """
    Writes content to a file in the specified directory.
    
    Args:
        working_directory (str): The base directory to work from.
        file_path (str): The path to the file to write.
        content (str): The content to write to the file.
    
    Returns:
        str: A string containing the result of the write operation.
    """

    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))

    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    
    if not valid_target_file:
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if os.path.isdir(target_file):
        return f'Error: Cannot write to "{file_path}" as it is a directory'
    
    temp_file_path = target_file
    while temp_file_path and temp_file_path != working_dir_abs:
        parent_dir = os.path.dirname(temp_file_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
            temp_file_path = parent_dir
        else:
            break
    
    try:
        with open(target_file, 'w') as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {str(e)}'
    