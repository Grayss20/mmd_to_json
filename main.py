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


def parse_tabular(text):
    # Remove the beginning substring using raw string
    text = text.replace(r"\begin{tabular}{|c|c|c|c|}", "", 1)

    # Remove any leading/trailing whitespace
    text = text.strip()
    parts = text.split('&')

    parsed_rows = []

    for i in range((len(parts)-1)//3):
        row = []
        if i == 0:
            row.append(parts[3*i].strip())
        else:
            row.append(str_to_split[last_newline_index + 1:].strip())
        row.append(parts[3*i+1].strip())
        row.append(parts[3*i+2].strip())
        # 4th element
        str_to_split = parts[3*i+3].strip()
        last_newline_index = str_to_split.rfind('\n')
        row.append(str_to_split[:last_newline_index].strip())
        parsed_rows.append(row)

    # Clear LaTeX junk
    for row in parsed_rows:
        for i in range(len(row)):
            row[i] = row[i].replace(r"\begin{tabular}{l}", "")
            row[i] = row[i].replace(r"\end{tabular}", " ")
            row[i] = row[i].replace(r"\begin{tabular}{c}", "")
            row[i] = row[i].replace(r"\hline", "")

    return parsed_rows


if __name__ == "__main__":
    file_path = "to_proceed/rms/9ma0-01-rms-20220818.mmd"
    questions = parse_rms_file(file_path)

    que, heading_info = proceed_que()

    # Update que list with mark_scheme from questions list
    for question in questions:
        for q in que:
            if q["question_number"] == question["question_number"]:
                q["mark_scheme"] = question["tabular"]

    pprint.pprint(que[0])
    print("--" * 30)
    for question in questions:
        question['tabular'] = question['tabular'].strip('\\begin{tabular}{|c|c|c|c|}\n').strip('\n\\end{tabular}')
        question['tabular'] = parse_tabular(question['tabular'])

    print(questions[0])
    print("--" * 30)

    # for question in questions:
    #     rows = question['tabular'].replace('\\hline', '').replace('\\multirow', '').replace('\\\\', '').replace('\\(', '$').replace('\\)', '$').split('\n')
    #     print(f'tabular: {question["tabular"]}')
    #     print(f'rows: {rows}')
    #     for q in que:
    #         if q["question_number"] == question["question_number"]:
    #             if len(q["parts"]) == 0:        #No parts in the question
    #                 print(rows)
    #                 steps = []
    #                 for row in rows[1:]:
    #                     if "&" in row:
    #                         chunks = row.split('&')
    #                         if chunks[1].strip() != '':
    #                             steps.append({
    #                                 "scheme": chunks[1].strip(),
    #                                 "marks": "",
    #                                 "AOs": ""
    #                             })
    #                 q["mark_scheme"] = {
    #                     "steps": steps,
    #                     "alternative": question["leftovers"]
    #                 }
    #             else:       # parts in the question
    #                 print(rows)
    #                 steps = []
    #                 part_count = -1
    #                 for row in rows[2:]:
    #                     if "&" in row:
    #                         chunks = row.split('&')
    #                         if chunks[0].strip() != '':
    #                             if part_count != -1:
    #                                 print(f'part_count: {part_count}, question number: {question["question_number"]}')
    #                                 q["parts"][part_count]["mark_scheme"] = {
    #                                     "steps": steps,
    #                                     "alternative": question["leftovers"]
    #                                 }
    #                             steps = []
    #                             part_count += 1
    #                         if chunks[1].strip() != '':
    #                             steps.append({
    #                                 "scheme": chunks[1].strip(),
    #                                 "marks": "",
    #                                 "AOs": ""
    #                             })
    #
    #
    #
    # print("-"*30)
    # print(que[1])
