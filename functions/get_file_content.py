import os
from config import MAX_CHARS

def get_file_content(working_directory, file_path):
    """
    Returns the content of a file in the specified directory.
    
    Args:
        working_directory (str): The base directory to work from.
        file_path (str): The path to the file to read.
    
    Returns:
        str: A string containing the content of the file.
    """

    working_dir_abs = os.path.abspath(working_directory)
    target_file = os.path.normpath(os.path.join(working_dir_abs, file_path))
    
    valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
    
    if not valid_target_file:
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(target_file):
        return f'Error: File not found or is not a regular file: "{file_path}"'
    
    try:
        with open(target_file, 'r') as f:
            content = f.read(MAX_CHARS)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
            return content
    except FileNotFoundError:
        return f'Error: File not found: "{file_path}"'
    except PermissionError:
        return f'Error: Permission denied to read: "{file_path}"'
    except Exception as e:
        return f'Error: {str(e)}'