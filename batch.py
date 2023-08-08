import os
import glob
import subprocess
from PIL import Image
import re
import shutil

def replace_persian_numbers(text):
    persian_numbers = '۰۱۲۳۴۵۶۷۸۹'
    english_numbers = '0123456789'
    translation_table = str.maketrans(persian_numbers, english_numbers)
    return text.translate(translation_table)

def wrap_numbers_in_math_mode(text):
    in_math_mode = False
    result = []
    current_chunk = ""

    i = 0
    while i < len(text):
        current_char = text[i]
        next_char = text[i + 1] if i + 1 < len(text) else None

        if current_char == '\\' and next_char in ['(', ')']:
            result.append(current_chunk)
            current_chunk = current_char + next_char
            in_math_mode = not in_math_mode
            i += 2
            continue

        if current_char == '$':
            result.append(current_chunk)
            current_chunk = current_char
            in_math_mode = not in_math_mode
            i += 1
            continue

        if not in_math_mode and current_char.isdigit() and not (text[i - 1].isdigit() or (next_char and next_char.isdigit())):
            result.append(current_chunk)
            current_chunk = f"${current_char}$"
            i += 1
            continue

        current_chunk += current_char
        i += 1

    result.append(current_chunk)

    return ''.join(result)



def convert_and_compile(input_file, output_file):
    docx_file = input_file
    latex_file = "output.tex"
    pdf_file = "output.pdf"


    # Define the helper functions
    def separate_text_equations(text):
        text = re.sub(r"\\\(", "\n\\(", text)
        text = re.sub(r"\\\)", "\\)\n", text)
        return text

    def remove_unnecessary_latex_commands(text):
        lines = text.split("\n")
        for i in range(len(lines)):
            line = lines[i]
            if "\\RL" in line:
                line = re.sub(r"\\RL\{([^}]*)\}", r"\1", line)
            if "\\text" in line:
                line = re.sub(r"\\text\{([^}]*)\}", r"\1", line)
            lines[i] = line
        return "\n".join(lines).strip()


    # Convert .docx to .md
    subprocess.run(["pandoc", "-s", docx_file, "-t", "markdown", "-o", "intermediate.md"], check=True)

    # Convert .md to .tex
    subprocess.run(["pandoc", "-s", "intermediate.md", "-t", "latex", "-o", "intermediate.tex"], check=True)

    # Extract content between \begin{document} and \end{document}
    with open("intermediate.tex", "r") as f:
        content = f.read()
    content = re.search(
        r"\\begin\{document\}([\s\S]*)\\end\{document\}", content
    ).group(1)
    
    # Replace Persian numbers with English numbers
    content = replace_persian_numbers(content)
    
    # Wrap numbers in math mode
    content = wrap_numbers_in_math_mode(content)

    # Separate text and equations, and remove unnecessary LaTeX commands
    content = separate_text_equations(content)
    content = remove_unnecessary_latex_commands(content)

    # Generate a new .tex file
    with open(latex_file, "w") as f:
        f.write("\\documentclass[12pt]{standalone}\n")
        f.write("\\input{etc/cmd}\n")
        f.write("\\usepackage[utf8]{inputenc}\n")
        f.write("\\usepackage{amsmath}\n")
        f.write("\\usepackage{amssymb}\n")
        f.write("\\usepackage{hyperref}\n")
        f.write("\\usepackage{varwidth}\n")
        f.write("\\usepackage{adjustbox}\n")
        f.write("\\begin{document}\n")
        f.write("\\begin{adjustbox}{margin=5mm}\n")
        f.write("\\begin{varwidth}{\\linewidth}\n")
        f.write(content)
        f.write("\n\\end{varwidth}\n")
        f.write("\\end{adjustbox}\n")
        f.write("\\end{document}")

    # Compile LaTeX to PDF with XeLaTeX
    subprocess.run(["xelatex", "-interaction=nonstopmode", latex_file], check=True)

    # Convert PDF to JPEG with pdftoppm
    subprocess.run(["pdftoppm", "-jpeg", "-singlefile", pdf_file, "temp"], check=True)

    # copy ouput.jpeg to output_file path
    shutil.move("temp.jpg", output_file)


def convert_all_files(input_directory, output_directory):
    # Get all .docx files in the input directory
    docx_files = glob.glob(os.path.join(input_directory, "*.docx"))

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for docx_file in docx_files:
        try:
            # Generate output file name based on the input file name
            base_name = os.path.basename(docx_file)
            output_name = os.path.splitext(base_name)[0]
            jpeg_file = os.path.join(output_directory, output_name + ".jpeg")

            # Convert and compile the document
            convert_and_compile(docx_file, jpeg_file)

            print(f"Successfully converted {docx_file} to {jpeg_file}")

        except Exception as e:
            print(f"Failed to convert {docx_file}. Error: {e}")


# Call the function with the appropriate directories
convert_all_files("./files", "./jpegoutputs")
