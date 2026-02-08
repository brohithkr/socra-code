import re
from utils import *
import argparse
import pickle

PROJECT_PATH = "/home/XXXX-2"


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
    
    # line number
    try:
        seq = extracted_data['bug_fixes'][extracted_data['bug_fixes'].index('line ') + 5:]
        pattern = r"[0-9]+"
        extracted_data['line_no'] = int(re.search(pattern, seq, re.DOTALL)[0])
    except:
        extracted_data['line_no'] = 0

    return extracted_data

def get_param_file():
    """Take in the parameter filepath from terminal and parse it using argparse"""
    parser = argparse.ArgumentParser(description='Tokenize the data')
    parser.add_argument('--file_path', type=str, default= f"{PROJECT_PATH}/socratic-debugging-benchmark/socratic_debugging_benchmark/v2_sigcse/evaluation_dataset/0_0_fibonacci_conversational_thread_1.txt", help='Filepath of the parameter file')
    args = parser.parse_args()
    return args.file_path


if __name__ == "__main__":
    # Get the filepath of the parameter file
    filepaths = get_files_deep(f"{PROJECT_PATH}/socratic-debugging-benchmark/socratic_debugging_benchmark/", ".txt")

    complete_dataset = {}

    for filepath in filepaths:
        text = read_text_from_file(filepath)

        tags = ['problem', 'bug_code', 'bug_fixes', 'bug_desc', 'unit_tests', 'code']
        desired_tags = ['problem', 'buggy_code', 'bug_fixes', 'bug_desc', 'unit_tests', 'correct_code']
        try:
            temp_extracted_data = extract_info_from_text(text, tags) 
        except:
            continue

        extracted_data = {}
        for t, dt in zip(tags, desired_tags):
            extracted_data[dt] = temp_extracted_data[t]

        for key, value in extracted_data.items():
            extracted_data[key] = f"---\n{key}:\n{value}\n---\n"

        temp = filepath.split('/')[-1].split('.')[0]
        with open(f'../data_txts/{temp}.txt', 'w+') as f:
            f.write(f'{temp}\n')
            for k in extracted_data.keys():
                f.write(f'{k}: {extracted_data[k]}\n-----------------------------------------------------------------------\n')

        temp = filepath.split('/')[-1].split('.')[0]
        with open(f'../data_pkls/{temp}.pkl', 'wb+') as f:
            pickle.dump(extracted_data, f)
        print(temp)