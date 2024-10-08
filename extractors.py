import re
import fitz  # PyMuPDF


# Define a function to extract questions from the content
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
            # "leftovers": leftovers,
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


# Define a function to extract alphabetic parts
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


#  Define a function to extract Roman numeral parts
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


# Define a function to get the next Roman numeral
def next_roman(roman):
    roman_numerals = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"]
    try:
        index = roman_numerals.index(roman)
        return roman_numerals[index + 1]
    except (ValueError, IndexError):
        raise Exception("Invalid or unsupported Roman numeral sequence.")


#  Define a function to remove occurrences of "(%)" where % is a digit from 1 to 9
def remove_numeric_placeholders(text):
    return re.sub(r'\(\d\)', '', text)


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

    # Convert pdf_text list to a single string for easier searching
    content = ' '.join(pdf_text)

    # Extract exam board
    exam_board_match = re.search(r'Pearson Edexcel', content)
    if exam_board_match:
        heading['exam_board'] = 'Pearson Edexcel'

    # Extract level
    level_match = re.search(r'Level \d+ \w+', content)
    if level_match:
        heading['level'] = level_match.group(0)

    # Extract subject
    subject_match = re.search(r'Mathematics\s+Advanced', content)
    if subject_match:
        heading['subject'] = subject_match.group(0)

    # Extract paper reference
    paper_reference_match = re.search(r'\b\d+MA\d+/\d{2}\b', content)
    if paper_reference_match:
        heading['paper_reference'] = paper_reference_match.group(0)

    # Extract paper
    paper_match = re.search(r'PAPER \d+: Pure Mathematics \d+', content)
    if paper_match:
        heading['paper'] = paper_match.group(0)

    # Extract total mark
    total_mark_match = re.search(r'otal mark for this paper is (\d+)', content)
    if total_mark_match:
        heading['total_mark'] = int(total_mark_match.group(1))

    # Extract total questions
    total_questions_match = re.search(r'There are (\d+) questions in this question paper', content)
    if total_questions_match:
        heading['total_questions'] = int(total_questions_match.group(1))

    # Extract time
    time_match = re.search(r'Time (\d+ hours)', content)
    if time_match:
        heading['time'] = time_match.group(1)

    # Extract year
    year_match = re.search(r'©(\d{4}) Pearson Education Ltd\.', content)
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

