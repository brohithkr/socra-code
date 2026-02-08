import os
def read_text_from_file(filepath: str) -> str:
    """
    Reads all text from a file given its filepath.

    Args:
    filepath (str): The path to the file.

    Returns:
    str: The content of the file as a string.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file at {filepath} was not found.")
        return None
    except IOError as e:
        print(f"An error occurred while reading the file: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def get_files_deep(root, string, str_in_name=True):
    matching_files = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if string in name:
                if str_in_name:
                    matching_files.append(os.path.join(path, name))
                else:
                    matching_files.append(name)
    return matching_files
