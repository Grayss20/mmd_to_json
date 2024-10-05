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
    problem_blocks = re.split(r'\n(?=\d+\.\s)', content)  # Split content by lines starting with a number followed by a period
    problem_number = 1

    for block in problem_blocks:
        if re.match(r'^\d+\.', block.strip()):  # Check if the block starts with a problem number
            problem_set = {
                "number": problem_number,
                "problem_set": parse_problem_set(block)
            }
            problems.append(problem_set)
            problem_number += 1

    return problems

# Step 4: Define a function to parse each problem set
def parse_problem_set(block):
    figure_url = re.search(r'!\[.*?\]\((.*?)\)', block)
    text_match = re.search(r'^\d+\.\s*(.*?)(?=(\n\s*\(|\n\s*-|$))', block, re.DOTALL)
    parts_block = re.findall(r'\n\s*\((\w)\)\s*(.*?)(?=(\n\s*\(|\n\s*-|$))', block, re.DOTALL)
    total_marks_match = re.search(r'\((\d+)\)\s*$', block)

    # Clean up continuation text if present
    problem_text = text_match.group(1).strip() if text_match else ""
    problem_text = re.sub(r'Question \d+ continued', '', problem_text, flags=re.IGNORECASE).strip()

    problem_set = {
        "figure_url": figure_url.group(1).strip() if figure_url else "",
        "text": problem_text,
        "total_marks": int(total_marks_match.group(1)) if total_marks_match else 0,
        "parts": parse_parts(parts_block)
    }
    return problem_set

# Step 5: Define a function to parse individual parts of a problem
def parse_parts(parts_content):
    parts = []
    for label, text, _ in parts_content:
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