from pprint import pprint
from utils import read_file
from que_extractors import (extract_questions, remove_numeric_placeholders, extract_text_from_pdf, extract_current_question,
                            extract_heading_info, update_marks_in_questions)


def proceed_que():
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    content = read_file(file_path)
    content = remove_numeric_placeholders(content)  # Remove numeric placeholders before extracting questions
    questions = extract_questions(content)

    pdf_text = extract_text_from_pdf('to_proceed/que/9ma0-01-que-20220608.pdf')
    #print(pdf_text)

    # Extract heading information from the PDF text
    heading_info = extract_heading_info(pdf_text)
    #pprint(heading_info)

    # Update the marks in the questions list using the PDF text
    update_marks_in_questions(pdf_text, questions)
    return questions, heading_info
