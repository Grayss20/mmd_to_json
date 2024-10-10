import re
import pprint
import json
from utils import read_file
from que_run import proceed_que


def parse_rms_file(file_path):
    # Read the content of the file
    content = read_file(file_path)

    # Define the delimiter pattern to find all occurrences of the delimiter
    delimiter = r'(\\begin\{tabular\}\{\|c\|c\|c\|c\|\})'

    # Find all matches of the delimiter
    matches = list(re.finditer(delimiter, content))

    # Create the questions list of dictionaries
    questions = []
    for i in range(len(matches)):
        start_index = matches[i].start()
        end_index = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        leftovers = content[start_index:end_index].strip()
        questions.append({
            "question_number": i + 1,
            "leftovers": leftovers
        })

    # Regex pattern to match \begin{tabular} blocks
    pattern = re.compile(r"(\\begin\{tabular\}.*?\\hline\n\\end\{tabular\})", re.DOTALL)

    # Extract all \begin{tabular} blocks from the text
    for question in questions:
        question["tabular"] = pattern.search(question["leftovers"]).group(1)
        question['leftovers'] = question['leftovers'].replace(question["tabular"], "").strip()

    return questions


if __name__ == "__main__":
    file_path = "to_proceed/rms/9ma0-01-rms-20220818.mmd"
    questions = parse_rms_file(file_path)

    # Print the questions list to verify the result
    # for question in questions:
    #     print("-" * 40)
    #     print(f"Question {question['question_number']}:\n{question['tabular']}\n{'-' * 40}")

    # lines = questions[0]['tabular'].split('\n')
    #
    # for line in lines:
    #     print(line)
    #
    # for line in lines:
    #     chunks = line.split('&')
    #
    #     for chunk in chunks:
    #         print(chunk)

    que, heading_info = proceed_que()

    combined_que = { "heading_info": heading_info, "questions": que}

    pprint.pprint(combined_que)

# Convert heading_info and que to single JSON
with open('results/info.json', 'w') as f:
    json.dump(combined_que, f)
