import gradio as gr
import subprocess
from PIL import Image
import re

def convert_and_compile(input_file):
    docx_file = input_file.name
    latex_file = "output.tex"
    pdf_file = "output.pdf"
    png_file = "output.png"

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
        f.write("\\documentclass[12pt]{article}\n")
        f.write("\\input{etc/cmd}\n")
        f.write("\\begin{document}\n")
        f.write(content)
        f.write("\n\\end{document}")

    # Compile LaTeX to PDF with XeLaTeX
    subprocess.run(["xelatex", "-interaction=nonstopmode", latex_file], check=True)

    # Convert PDF to PNG with pdftoppm
    subprocess.run(["pdftoppm", "-png", "-singlefile", pdf_file, "output"], check=True)

    # Load the PNG image and return it
    return Image.open(png_file)

iface = gr.Interface(
    fn=convert_and_compile, 
    inputs=gr.File(label="Upload .docx"), 
    outputs=gr.Image(type="pil", label="Output PDF as PNG"),
)
iface.launch(debug=True)
