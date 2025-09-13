import os

def describe_file(name, abs_target):
    file_path = os.path.join(abs_target, name)
    return f"- {name}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}"

def get_files_info(working_directory, directory="."):
    
    abs_working = os.path.abspath(working_directory)
    abs_target = os.path.abspath(os.path.join(working_directory, directory))
    inside = abs_target == abs_working or abs_target.startswith(abs_working + os.sep)

    if not inside: return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    if not os.path.isdir(abs_target): return f'Error: "{directory}" is not a directory'
    
    try:
        entries = os.listdir(abs_target)
        lines = map(lambda name: describe_file(name, abs_target), entries)
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"
 
