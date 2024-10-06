import re
from pprint import pprint


# Step 1: Define a function to read the .mmd file
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Step 2: Define a function to extract questions from the content
def extract_questions(content):
    # Find all question blocks that start with a question number (optionally followed by spaces) and end where the next question begins
    question_blocks = re.findall(r'\n(\d+)\s*(\.)(.*?)(?=\n\d+\s*\.\s*|$)', content, re.DOTALL)
    questions = []
    for number, dot, body in question_blocks:
        leftovers = body.strip()
        if leftovers.startswith('.'):
            leftovers = leftovers[1:].lstrip()
        # Remove occurrences of '\nQuestion % continued'
        leftovers = re.sub(r'\nQuestion \d+ continued', '', leftovers).strip()
        questions.append({"question_number": int(number), "leftovers": leftovers})
    return questions


# Example usage
if __name__ == "__main__":
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    content = read_file(file_path)
    questions = extract_questions(content)

    question_counter = 1
    for question in questions:
        print(f"Question {question_counter}:")
        pprint(question)
        print("-" * 40)
        question_counter += 1