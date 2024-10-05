import re
import json

# Step 1: Define a function to read the .mmd file
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Step 2: Define a function to parse the exam details
def parse_exam_details(content):
    def safe_search(pattern, content):
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    exam_details = {
        "title": safe_search(r'\\title\{(.*?)\}', content),
        "paper_reference": safe_search(r'paper_reference\{(.*?)\}', content),
        "subject": safe_search(r'subject\{(.*?)\}', content),
        "paper": safe_search(r'paper\{(.*?)\}', content),
        "time": safe_search(r'time\{(.*?)\}', content),
        "total_marks": int(safe_search(r'total_marks\{(\d+)\}', content)) if re.search(r'total_marks\{(\d+)\}', content) else 0
    }
    return exam_details

# Step 3: Define a function to parse individual problems
def parse_problems(content):
    problems = []

    # Find the first problem starting with "1."
    first_problem_start = re.search(r'\b1\.', content)
    if first_problem_start:
        problems_content = content[first_problem_start.start():]

        # Split problems based on "\n(?=\s*\d+\s*\.)" pattern
        problem_blocks = re.split(r'\n(?=\s*\d+\s*\.)', problems_content)
        problem_number = 1

        for block in problem_blocks:
            block = block.strip()
            if block:
                print(f"Parsing problem block for problem {problem_number}:\n{block}\n{'-'*40}")  # Debug print
                problem_set = parse_problem_set(block)
                problem_set["number"] = problem_number
                problems.append(problem_set)
                problem_number += 1

    return problems

# Step 4: Define a function to parse each problem set
def parse_problem_set(block):
    # Extract figure URL if available and remove it from the text block
    figure_url_match = re.search(r'!\[.*?\]\((.*?)\)', block)
    figure_url = figure_url_match.group(1).strip() if figure_url_match else ""
    block = re.sub(r'!\[.*?\]\(.*?\)', '', block).strip()

    # Extract problem text excluding parts
    text_match = re.search(r'^(.*?)(?=(\n\s*\((a|b|c|d|e|f)\)|\n\d+\.|continued|$))', block, re.DOTALL)

    # Extract individual parts of the problem
    parts_block = re.findall(r'\n\s*(\((a|b|c|d|e|f)\))\s*(.*?)(?=(\n\s*\((a|b|c|d|e|f)\)|\n\d+\.|$))', block, re.DOTALL)

    # Extract total marks if available
    total_marks_match = re.search(r'\((\d+)\)\s*$', block)

    # Clean up continuation text if present
    problem_text = text_match.group(1).strip() if text_match else ""
    problem_text = re.sub(r'Question \d+ continued', '', problem_text, flags=re.IGNORECASE).strip()

    # Handle special case where text starts with part (a) immediately
    if re.match(r'^\(a\)', problem_text):
        problem_text = ""

    # If problem_text is too short (less than 5 characters) and parts exist, assign the first part to problem_text
    if len(problem_text) < 5 and parts_block:
        first_part = parts_block.pop(0)
        problem_text = f"{problem_text.strip()} {first_part[0].strip()}".strip()
        parts_block.insert(0, (first_part[0], first_part[1], first_part[2]))

    # If problem_text only contains the problem number, clear it
    if re.match(r'^\d+\.$', problem_text.strip()):
        problem_text = ""

    print(f"Extracted problem text:\n{problem_text}\n{'='*40}")  # Debug print

    problem_set = {
        "figure_url": figure_url,
        "text": problem_text,
        "total_marks": int(total_marks_match.group(1)) if total_marks_match else 0,
        "parts": parse_parts(parts_block)
    }
    return problem_set

# Step 5: Define a function to parse individual parts of a problem
def parse_parts(parts_content):
    parts = []
    for part in parts_content:
        label = part[0].strip()
        text = part[2].strip()
        marks_match = re.search(r'\((\d+)\)', text)
        part_text = re.sub(r'\((\d+)\)', '', text).strip()
        part_text = re.sub(r'Question \d+ continued', '', part_text, flags=re.IGNORECASE).strip()  # Remove continuation text
        part = {
            "text": part_text,
            "marks": int(marks_match.group(1)) if marks_match else 0
        }
        parts.append(part)

    return parts

# Step 6: Define the main function to parse the entire file and create JSON
def parse_mmd_to_json(file_path):
    content = read_file(file_path)
    exam_details = parse_exam_details(content)
    problems = parse_problems(content)

    exam_data = {
        "exam_details": exam_details,
        "problems": problems
    }
    return exam_data

# Step 7: Define a function to write the parsed data to a JSON file
def write_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Example usage
if __name__ == "__main__":
    file_path = "to_proceed/que/9ma0-01-que-20220608.mmd"
    output_file = "results/parsed_exam.json"
    parsed_data = parse_mmd_to_json(file_path)
    write_to_json(parsed_data, output_file)