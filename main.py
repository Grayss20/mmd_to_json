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


if __name__ == "__main__":
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    content = read_file(file_path)
    content = remove_numeric_placeholders(content)  # Remove numeric placeholders before extracting questions
    questions = extract_questions(content)

    pdf_text = extract_text_from_pdf('to_proceed/que/9ma0-01-que-20220608.pdf')

    current_page = 33
    current_question = extract_current_question(pdf_text[current_page])

    print(f'Current Question: {current_question}')

    # Define the pattern to match all the target substrings
    pattern = r'\(a\)|\(b\)|\(c\)|\(d\)|\(e\)|\(f\)|\(g\)|\(h\)|\(i\)|\(ii\)|\(iii\)|\(iv\)|\(\d\)'

    # Use re.findall to extract all matching substrings
    matches = re.findall(pattern, pdf_text[current_page])

    # Merge them into a single string
    marks_str = ''.join(matches)

    print("Extracted marks string:", marks_str)

    print("--------------------")# Use re.split to split the string into a list of substrings
    print("Extracted questions:")
    pprint(questions[current_question - 1])
    print("--------------------")# Use re.split to split the string into a list of substrings

    print(pdf_text[current_page])


    # question_counter = 1
    # for question in questions:
    #     print(f"Question {question_counter}:")
    #     pprint(question)
    #     print("-" * 40)
    #     question_counter += 1
