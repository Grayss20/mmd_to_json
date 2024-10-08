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


def extract_heading_info(pdf_text):
    heading = {
        'exam_board': '',
        'level': '',
        'subject': '',
        'paper': '',
        'paper_reference': '',
        'total_mark': '',
        'total_questions': '',
        'time': '',
        'year': ''
    }

    # Extract the first page text
    first_page = pdf_text[0]

    # Extract exam board
    exam_board_match = re.search(r'Pearson Edexcel', first_page)
    if exam_board_match:
        heading['exam_board'] = 'Pearson Edexcel'

    # Extract level
    level_match = re.search(r'Level (\d+ \w+)', first_page)
    if level_match:
        heading['level'] = level_match.group(0)

    # Extract subject
    subject_match = re.search(r'Mathematics\nAdvanced', first_page)
    if subject_match:
        heading['subject'] = 'Mathematics\nAdvanced'

    # Extract paper reference
    paper_reference_match = re.search(r'\b9MA0/01\b', first_page)
    if paper_reference_match:
        heading['paper_reference'] = paper_reference_match.group(0)

    # Extract paper
    paper_match = re.search(r'PAPER 1: Pure Mathematics 1', first_page)
    if paper_match:
        heading['paper'] = paper_match.group(0)

    # Extract total mark
    total_mark_match = re.search(r'Total mark for this paper is (\d+)', first_page)
    if total_mark_match:
        heading['total_mark'] = int(total_mark_match.group(1))

    # Extract total questions
    total_questions_match = re.search(r'There are (\d+) questions in this question paper', first_page)
    if total_questions_match:
        heading['total_questions'] = int(total_questions_match.group(1))

    # Extract time
    time_match = re.search(r'Time (\d+ hours)', first_page)
    if time_match:
        heading['time'] = time_match.group(1)

    # Extract year
    year_match = re.search(r'©(\d{4}) Pearson Education Ltd\.', first_page)
    if year_match:
        heading['year'] = int(year_match.group(1))

    return heading


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

    # Extract heading information from the PDF text
    heading_info = extract_heading_info(pdf_text)
    pprint(heading_info)

    # Update the marks in the questions list using the PDF text
    update_marks_in_questions(pdf_text, questions)