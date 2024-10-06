import re
from pprint import pprint


# Step 1: Define a function to read the .mmd file
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


# Step 2: Define a function to extract questions from the content
def extract_questions(content):
    content = remove_numeric_placeholders(content)  # Remove numeric placeholders before processing
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


# Step 3: Define a function to extract parts from leftovers
def extract_parts(leftovers):
    if not leftovers:
        return []
    elif leftovers.startswith('(a)'):
        return extract_alphabetic_parts(leftovers)
    elif leftovers.startswith('(i)'):
        return extract_roman_parts(leftovers)
    else:
        raise Exception("There is a problem in splitting leftovers into parts after extraction of initial text.")


# Step 4: Define a function to extract alphabetic parts
def extract_alphabetic_parts(leftovers):
    parts = []
    current_part = {
        "part": "a",
        "text": "",
        "marks": 0
    }
    expected_alphabet = 'b'
    while True:
        next_delim = f'({expected_alphabet})'
        split_index = leftovers.find(next_delim)
        if split_index == -1:
            current_part["text"] = leftovers.strip()
            parts.append(current_part)
            break
        current_part["text"] = leftovers[:split_index].strip()
        parts.append(current_part)
        leftovers = leftovers[split_index:]
        current_part = {
            "part": expected_alphabet,
            "text": "",
            "marks": 0
        }
        expected_alphabet = chr(ord(expected_alphabet) + 1)
    return parts


# Step 5: Define a function to extract Roman numeral parts
def extract_roman_parts(leftovers):
    parts = []
    current_part = {
        "part": "i",
        "text": "",
        "marks": 0
    }
    expected_roman = 'ii'
    while True:
        next_delim = f'({expected_roman})'
        split_index = leftovers.find(next_delim)
        if split_index == -1:
            current_part["text"] = leftovers.strip()
            parts.append(current_part)
            break
        current_part["text"] = leftovers[:split_index].strip()
        parts.append(current_part)
        leftovers = leftovers[split_index:]
        current_part = {
            "part": expected_roman,
            "text": "",
            "marks": 0
        }
        expected_roman = next_roman(expected_roman)

    # Extra logic to add subparts if "(a)" is found in any part
    for part in parts:
        if "(a)" in part["text"]:
            split_index = part["text"].find("(a)")
            subparts_text = part["text"][split_index:]
            part["text"] = part["text"][:split_index].strip()
            part["subparts"] = extract_alphabetic_parts(subparts_text)

    return parts


# Step 6: Define a function to get the next Roman numeral
def next_roman(roman):
    roman_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
    try:
        index = roman_numerals.index(roman)
        return roman_numerals[index + 1]
    except (ValueError, IndexError):
        raise Exception("Invalid or unsupported Roman numeral sequence.")


# Step 7: Define a function to remove occurrences of "(%)" where % is a digit from 1 to 9
def remove_numeric_placeholders(text):
    return re.sub(r'\(\d\)', '', text)


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