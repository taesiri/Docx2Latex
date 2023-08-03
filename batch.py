import os
import glob
import subprocess
from PIL import Image
import re
import shutil

def convert_and_compile(input_file, output_file):
    docx_file = input_file
    latex_file = "output.tex"
    pdf_file = "output.pdf"

    # Convert .docx to .md
    subprocess.run(["pandoc", "-s", docx_file, "-t", "markdown", "-o", "intermediate.md"], check=True)

    # Convert .md to .tex
    subprocess.run(["pandoc", "-s", "intermediate.md", "-t", "latex", "-o", "intermediate.tex"], check=True)

    # Extract content between \begin{document} and \end{document}
    with open("intermediate.tex", "r") as f:
        content = f.read()
    content = re.search(r"\\begin\{document\}([\s\S]*)\\end\{document\}", content).group(1)

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
    docx_files = glob.glob(os.path.join(input_directory, '*.docx'))

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    for docx_file in docx_files:
        try:
            # Generate output file name based on the input file name
            base_name = os.path.basename(docx_file)
            output_name = os.path.splitext(base_name)[0]
            jpeg_file = os.path.join(output_directory, output_name + '.jpeg')
            

            # Convert and compile the document
            convert_and_compile(docx_file, jpeg_file)

            print(f'Successfully converted {docx_file} to {jpeg_file}')

        except Exception as e:
            print(f'Failed to convert {docx_file}. Error: {e}')

# Call the function with the appropriate directories
convert_all_files('./files', './jpegoutputs')
