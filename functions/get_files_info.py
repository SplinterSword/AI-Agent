import os
from google.genai import types

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)

def get_files_info(working_directory, directory="."):
    """
    Returns information about files in the specified directory.
    
    Args:
        working_directory (str): The base directory to work from.
        directory (str): The directory to get file information for. Defaults to the current directory.
    
    Returns:
        str: A string containing file information.
    """
    
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))

    valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
    
    if not valid_target_dir:
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    try:
        files = os.listdir(target_dir)
    except FileNotFoundError:
        return f'Error: Directory "{directory}" not found'
    except PermissionError:
        return f'Error: Permission denied to access "{directory}"'
    
    final_answer = ""
    for file in files:
        file_path = os.path.join(target_dir, file)
        stat = os.stat(file_path)
        
        name = file
        file_size = stat.st_size
        is_dir = os.path.isdir(file_path)
        
        file_string = f"{name}: file_size={file_size}, is_dir={is_dir}"
        final_answer += file_string + "\n"
    
    return final_answer