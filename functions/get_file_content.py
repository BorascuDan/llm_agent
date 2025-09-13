from config import MAX_CHARS 
import os

def get_file_content(working_directory, file_path):
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(working_directory, file_path))
    inside = abs_target == abs_working or abs_target.startswith(abs_working + os.sep)

    if not inside: return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

    if not os.path.isfile(abs_target): return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(abs_target, "r") as f:
            file_content_string = f.read(MAX_CHARS)
            check_end = f.read(1)
    except Exception as e:
        return f"Error: {e}"
    
    if len(check_end): file_content_string += f'[...File "{file_path}" truncated at 10000 characters]'

    return file_content_string

