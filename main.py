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
        if leftovers.startswith('.'):  # Remove leading dot and spaces
            leftovers = leftovers[1:].lstrip()
        # Remove occurrences of '\nQuestion % continued'
        leftovers = re.sub(r'\nQuestion \d+ continued', '', leftovers).strip()
        # Extract all figure URLs if present
        figure_urls = re.findall(r'!\[.*?\]\((.*?)\)', leftovers)
        # Remove the figure URLs from leftovers
        leftovers = re.sub(r'!\[.*?\]\(.*?\)', '', leftovers).strip()
        # Extract the text until the first occurrence of '(a)' or '(i)'
        if '(a)' in leftovers or '(i)' in leftovers:
            split_point = min(leftovers.find('(a)') if '(a)' in leftovers else len(leftovers),
                              leftovers.find('(i)') if '(i)' in leftovers else len(leftovers))
            text = leftovers[:split_point].strip()
            leftovers = leftovers[split_point:].lstrip()
        else:
            text = leftovers
            leftovers = ''
        text = remove_trailing_marks(text)  # Apply the function to remove trailing marks
        parts = extract_parts(leftovers)  # Extract parts from leftovers
        questions.append({
            "question_number": int(number),
            "leftovers": leftovers,
            "figure_url": figure_urls,
            "text": text,
            "total_marks": 0,
            "parts": parts
        })
    return questions


# Step 3: Define a function to remove trailing marks
def remove_trailing_marks(text):
    return re.sub(r'\n\(\d\)$', '', text).rstrip()


# Step 4: Define a function to extract parts from leftovers
def extract_parts(leftovers):
    if not leftovers:
        return []
    elif leftovers.startswith('(a)') or leftovers.startswith('(i)'):
        parts = []
        part_blocks = re.split(r'(\([a-z]\)|\((i{1,3}|iv|v|vi{0,3}|ix|x)\))', leftovers)
        current_part = None
        expected_alphabet = 'a'
        expected_roman = 'i'
        is_alphabetic = leftovers.startswith('(a)')

        for block in part_blocks:
            if block and (re.match(r'^\([a-z]\)$', block) or re.match(r'^\((i{1,3}|iv|v|vi{0,3}|ix|x)\)$', block)):
                # Handle alphabetic parts
                if is_alphabetic:
                    if block == f'({expected_alphabet})':
                        expected_alphabet = chr(ord(expected_alphabet) + 1)
                    else:
                        raise Exception("Alphabetic parts are out of order.")
                else:
                    if block == f'({expected_roman})':
                        expected_roman = next_roman(expected_roman)
                    else:
                        raise Exception("Roman numeral parts are out of order.")
                if current_part:
                    parts.append(current_part)
                current_part = {
                    "part": block,
                    "text": "",
                    "marks": 0
                }
            elif current_part and block and block.strip():
                current_part["text"] += " " + block.strip()
        if current_part:
            parts.append(current_part)
        for part in parts:
            part["text"] = part["text"].strip()
        return parts
    else:
        raise Exception("There is a problem in splitting leftovers into parts after extraction of initial text.")


# Step 5: Define a function to get the next Roman numeral
def next_roman(roman):
    roman_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
    try:
        index = roman_numerals.index(roman)
        return roman_numerals[index + 1]
    except (ValueError, IndexError):
        raise Exception("Invalid or unsupported Roman numeral sequence.")


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
