import re
from utils import *
import argparse
import pickle

PROJECT_PATH = "/home/XXXX-3"


def extract_info_from_text(text: str, tags: list) -> dict:
    """
    Extracts information from a given text based on specified tags.

    Args:
    text (str): The input text containing structured tags.
    tags (list): A list of tags to extract information for.

    Returns:
    dict: A dictionary where keys are the tags and values are the extracted information.
    """
    extracted_data = {}

    for tag in tags:
        # Create a regex pattern dynamically for each tag
        pattern = fr"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            # Clean up the extracted text
            extracted_data[tag] = match.group(1).strip()
        else:
            0/0
            extracted_data[tag] = None  # If no match found, return None for that tag
    
    extracted_data['problem'] = "\n".join(extracted_data['problem'].split('\n')[1:])

    # line number
    try:
        seq = extracted_data['bug_fixes'][extracted_data['bug_fixes'].index('line ') + 5:]
        pattern = r"[0-9]+"
        extracted_data['line_no'] = int(re.search(pattern, seq, re.DOTALL)[0])
    except:
        extracted_data['line_no'] = 0

    return extracted_data

def extract_code(py_file):
    with open(py_file, 'r') as file:
        file_content = file.read()

    idx = file_content.index("class Solution") 
    code = file_content[idx:].split('\n')
    for i in range(len(code)):
        code[i] = str(i+1) + ". " + code[i]

    return "\n".join(code)

def get_param_file():
    """Take in the parameter filepath from terminal and parse it using argparse"""
    parser = argparse.ArgumentParser(description='Tokenize the data')
    parser.add_argument('--file_path', type=str, default= f"{PROJECT_PATH}/socratic-debugging-benchmark/socratic_debugging_benchmark/v2_sigcse/evaluation_dataset/0_0_fibonacci_conversational_thread_1.txt", help='Filepath of the parameter file')
    args = parser.parse_args()
    return args.file_path


if __name__ == "__main__":
    # Get the filepath of the parameter file
    bug_dir = './BUG-leetcode-master/'
    clean_dir = './leetcode/'

    os.mkdir(f'{bug_dir}/data_pkls')
    os.mkdir(f'{bug_dir}/data_txts')

    filepaths = get_files_deep(bug_dir, ".py", str_in_name=False)

    complete_dataset = {}

    desired_tags = {'problem':'problem', 'bug_code': 'buggy_code', 'bug_fixes': 'bug_fixes', 'bug_desc': 'bug_desc', 'code': 'correct_code', 'line_no': 'line_no'}

    bug_tags = ['problem', 'bug_fixes', 'bug_desc']

    for filepath in filepaths:
        bug_path = os.path.join(bug_dir, filepath)
        clean_path = os.path.join(clean_dir, filepath)
        text = read_text_from_file(bug_path)
       
        temp_extracted_data = extract_info_from_text(text, bug_tags)
        temp_extracted_data['bug_code'] = extract_code(bug_path)
        temp_extracted_data['code'] = extract_code(clean_path)
       
        extracted_data = {}
        for t in temp_extracted_data.keys():
            extracted_data[desired_tags[t]] = temp_extracted_data[t]

        for key, value in extracted_data.items():
            extracted_data[key] = f"---\n{key}:\n{value}\n---\n"

        with open(f'{bug_dir}data_txts/{filepath}.txt', 'w+') as f:
            f.write(f'{filepath}\n')
            for k in extracted_data.keys():
                f.write(f'{k}: {extracted_data[k]}\n-----------------------------------------------------------------------\n')

        with open(f'{bug_dir}data_pkls/{filepath}.pkl', 'wb+') as f:
            pickle.dump(extracted_data, f)
        print(filepath)