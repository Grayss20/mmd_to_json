import re
from pprint import pprint
from utils import read_file
from extractors import extract_questions, remove_numeric_placeholders

# Example usage
if __name__ == "__main__":
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    content = read_file(file_path)
    content = remove_numeric_placeholders(content)  # Remove numeric placeholders before extracting questions
    questions = extract_questions(content)

    question_counter = 1
    for question in questions:
        print(f"Question {question_counter}:")
        pprint(question)
        print("-" * 40)
        question_counter += 1
