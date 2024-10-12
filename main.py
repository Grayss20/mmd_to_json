import re
import pprint
import json
from utils import read_file
from que_run import proceed_que


def parse_rms_file(file_path):
    # Read the content of the file
    content = read_file(file_path)

    # Debug print to check if content is correctly loaded
    #print("Loaded file content:\n", content[:500], "\n... [truncated]")

    # Define the delimiter pattern to find all occurrences of the delimiter
    delimiter = r'(\\begin\{tabular\}\{\|c\|c\|c\|c\|\})'

    # Find all matches of the delimiter
    matches = list(re.finditer(delimiter, content))

    # Debug print for matches
    #print(f"Found {len(matches)} tabular matches.")

    # Create the questions list of dictionaries
    questions = []
    for i in range(len(matches)):
        start_index = matches[i].start()
        end_index = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        leftovers = content[start_index:end_index].strip()

        # Debug print for question boundaries
        #print(f"Processing question {i + 1}, range: {start_index}-{end_index}")

        questions.append({
            "question_number": i + 1,
            "leftovers": leftovers
        })

    # Regex pattern to match \begin{tabular} blocks
    pattern = re.compile(r"(\\begin\{tabular\}.*?\\hline\n\\end\{tabular\})", re.DOTALL)

    # Extract all \begin{tabular} blocks from the text
    for question in questions:
        match = pattern.search(question["leftovers"])
        if match:
            question["tabular"] = match.group(1)
            # Debug print for extracted tabular
            #print(f"Extracted tabular for question {question['question_number']}:\n", question["tabular"])

            question['leftovers'] = question['leftovers'].replace(question["tabular"], "").strip()
        else:
            question["tabular"] = None

    return questions


def flatten_tabular_content(tabular_content):
    """Convert tabular content into a single line without LaTeX formatting."""
    # Flatten any nested tabulars by first removing nested `\begin{tabular}` environments
    tabular_content = re.sub(r'\\begin\{tabular\}{[^}]*}', '', tabular_content)
    tabular_content = re.sub(r'\\end{tabular}', '', tabular_content)

    # Replace LaTeX-specific characters and formatting
    tabular_content = tabular_content.replace('\\hline', '')  # Remove hline
    tabular_content = tabular_content.replace('\\\\', '\n')  # Replace row breaks with newline
    tabular_content = tabular_content.replace('&', '|')  # Column separator

    # Remove LaTeX math delimiters (\( \), \[ \], etc.)
    tabular_content = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', tabular_content)

    # Remove multirow and multicolumn commands
    tabular_content = re.sub(r'\\multi(row|column)\{[^}]*\}\{[^}]*\}', '', tabular_content)

    # Replace multiple spaces with single space for cleanliness
    tabular_content = re.sub(r'\s+', ' ', tabular_content).strip()

    return tabular_content


def parse_latex_tabular(latex_text):
    """Parse LaTeX tabular and return a structured list of rows."""
    # First, flatten any nested tabulars
    flattened_content = flatten_tabular_content(latex_text)

    # Split the content by rows
    rows = flattened_content.split('\n')

    structured_data = []

    # For each row, split it by column separator and add to structured data
    for row in rows:
        if row.strip():  # Avoid empty rows
            columns = row.split('|')  # Split by the pipe symbol used earlier
            structured_data.append([col.strip() for col in columns])  # Clean and strip spaces

    return structured_data



if __name__ == "__main__":
    # file_path = "to_proceed/rms/9ma0-01-rms-20220818.mmd"
    # questions = parse_rms_file(file_path)
    #
    # que, heading_info = proceed_que()
    #
    # # Update que list with mark_scheme from questions list
    # tabular_list = []
    # for question in questions:
    #     for q in que:
    #         if q["question_number"] == question["question_number"]:
    #             q["mark_scheme"] = question["tabular"]
    #             tabular_list.append(question["tabular"])
    #
    # for tab in tabular_list:
    #     tab = parse_latex_tabular(tab)
    #     for row in tab:
    #         print(row)

    # Example element (Element 15 in your case)
    element_15 = """
    \\begin{tabular}{|c|c|c|c|}
    \\hline Question & Scheme & Marks & AOs \\\\
    \\hline 15 (a) & \\begin{tabular}{l} Sets up an allowable equation using volume =240 \\\\ E.g. \\frac{1}{2} r^{2} \\times 0.8 h=240 \\Rightarrow h=\\frac{600}{r^{2}} o.e. \\end{tabular} & \\begin{tabular}{l} \\begin{tabular}{l} M1 \\\\ A1 \\end{tabular} \\end{tabular} & \\begin{tabular}{l} \\begin{tabular}{l} 3.4 \\\\ 1.1 b \\end{tabular} \\end{tabular} \\\\
    \\hline & \\begin{tabular}{l} Attempts to substitute their h=\\frac{600}{r^{2}} into \\\\ (S=) \\frac{1}{2} r^{2} \\times 0.8+\\frac{1}{2} r^{2} \\times 0.8+2 r h+0.8 r h \\end{tabular} & dM1 & 3.4 \\\\
    \\hline & \\begin{tabular}{l} S=0.8 r^{2}+2.8 r h=0.8 r^{2}+2.8 \\times \\frac{600}{r}=0.8 r^{2}+\\frac{1680}{r} * \\end{tabular} & A1* & 2.1 \\\\
    \\hline & & (4) & \\\\
    \\hline (b) & \\begin{tabular}{l} \\left(\\frac{\\mathrm{d} S}{\\mathrm{~d} r}\\right)=1.6 r-\\frac{1680}{r^{2}} \\end{tabular} & \\begin{tabular}{l} \\begin{tabular}{l} M1 \\\\ A1 \\end{tabular} \\end{tabular} & \\begin{tabular}{l} \\begin{tabular}{l} 3.1 a \\\\ 1.1 b \\end{tabular} \\end{tabular} \\\\
    \\hline & \\begin{tabular}{l} Sets \\frac{\\mathrm{d} S}{\\mathrm{~d} r}=0 \\Rightarrow r^{3}=1050 \\\\ r= awrt 10.2 \\end{tabular} & \\begin{tabular}{c} d 1 1 1 \\\\ A 1 \\end{tabular} & \\begin{tabular}{l} \\begin{tabular}{l} 2.1 \\\\ 1.1 b \\end{tabular} \\end{tabular} \\\\
    \\hline & & (4) & \\\\
    \\hline (c) & \\begin{tabular}{l} Attempts to substitute their positive r into \\left(\\frac{\\mathrm{d}^{2} S}{\\mathrm{~d} r^{2}}\\right)=1.6+\\frac{3360}{r^{3}} and considers its value or sign \\end{tabular} & M1 & 1.1 b \\\\
    \\hline & \\begin{tabular}{l} E.g. Correct \\frac{\\mathrm{d}^{2} S}{\\mathrm{~d} r^{2}}=1.6+\\frac{3360}{r^{3}} with \\frac{\\mathrm{d}^{2} S}{\\mathrm{~d} r^{2}}{ }_{r=10.2}=5>0 proving a minimum value of S \\end{tabular} & A1 & 1.1 b \\\\
    \\hline & & (2) & \\\\
    \\hline \\multicolumn{4}{|l|}{ (10 marks) } \\\\
    \\hline \\multicolumn{4}{|l|}{ Notes: } \\\\
    \\hline
    \\end{tabular}
    """

    parsed_content = parse_latex_tabular(element_15)

    # Pretty-printing the result for clarity
    pprint.pprint(parsed_content)