import re
from pprint import pprint
from utils import read_file
from extractors import extract_questions, remove_numeric_placeholders
import fitz  # PyMuPDF


def extract_text_from_pdf(pdf_path):
    text = []
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text.append(page.get_text())
    return text


def extract_current_question(text):
    # Regular expression to match "X." pattern indicating the start of a new question
    match_new_question = re.search(r'(\d+)\.\s', text)
    if match_new_question:
        return int(match_new_question.group(1))

    # Regular expression to match "Question X continued" pattern indicating continued question
    match_continued = re.search(r'Question (\d+) continued', text)
    if match_continued:
        return int(match_continued.group(1))

    return None


def update_marks_in_questions(pdf_text, questions):
    # Define the pattern to match all the target substrings
    pattern = r'\(a\)|\(b\)|\(c\)|\(d\)|\(e\)|\(f\)|\(g\)|\(h\)|\(i\)|\(ii\)|\(iii\)|\(iv\)|\(\d\)'

    previous_question = None
    for current_page in range(len(pdf_text)):
        current_question = extract_current_question(pdf_text[current_page])

        if current_question is not None:
            previous_question = current_question
        else:
            # If we can't determine the current question, assume it's a continuation of the previous one
            current_question = previous_question

        # Use re.findall to extract all matching substrings
        matches = re.findall(pattern, pdf_text[current_page])

        # Merge them into a single string
        marks_str = ''.join(matches)

        # If marks_str is empty, skip this page
        if not marks_str:
            continue

        # Find the corresponding question in the questions list
        if current_question is not None and current_question <= len(questions):
            question = questions[current_question - 1]
            parts = question.get('parts', [])

            # Update marks values for each part
            marks_index = 0
            for part in parts:
                if 'subparts' in part:
                    part['marks'] = 0  # Set marks to 0 if there are subparts
                    for subpart in part['subparts']:
                        while marks_index < len(marks_str) and not marks_str[marks_index].isdigit():
                            marks_index += 1

                        if marks_index < len(marks_str):
                            subpart['marks'] = int(marks_str[marks_index])
                            marks_index += 1
                else:
                    while marks_index < len(marks_str) and not marks_str[marks_index].isdigit():
                        marks_index += 1

                    if marks_index < len(marks_str):
                        part['marks'] = int(marks_str[marks_index])
                        marks_index += 1

    # Extract total marks for each question
    total_marks_pattern = re.compile(r'\(Total for Question (\d+) is (\d+) marks\)')
    for page in pdf_text:
        for match in total_marks_pattern.finditer(page):
            question_number = int(match.group(1))
            total_marks = int(match.group(2))
            if question_number <= len(questions):
                questions[question_number - 1]['total_marks'] = total_marks


if __name__ == "__main__":
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    content = read_file(file_path)
    content = remove_numeric_placeholders(content)  # Remove numeric placeholders before extracting questions
    questions = extract_questions(content)

    pdf_text = extract_text_from_pdf('to_proceed/que/9ma0-01-que-20220608.pdf')
    print(pdf_text)

    # Update the marks in the questions list using the PDF text
    update_marks_in_questions(pdf_text, questions)

#    Print the updated questions list
    question_counter = 1
    for question in questions:
        print(f"Question {question_counter}:")
        pprint(question)
        print("-" * 40)
        question_counter += 1