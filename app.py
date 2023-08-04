import gradio as gr
import subprocess
from PIL import Image
import re

def convert_and_compile(input_file):
    docx_file = input_file.name
    latex_file = "output.tex"
    pdf_file = "output.pdf"
    png_file = "output.png"

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
    content = re.search(r"\\begin\{document\}([\s\S]*)\\end\{document\}", content).group(1)

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

    # Convert PDF to PNG with pdftoppm
    subprocess.run(["pdftoppm", "-png", "-singlefile", pdf_file, "output"], check=True)

    # Load the PNG image and return it
    return Image.open(png_file)

iface = gr.Interface(
    fn=convert_and_compile, 
    inputs=gr.File(label="Upload .DocX"), 
    outputs=gr.Image(type="pil", label="Latex Output", show_label=False),
)

iface.launch(debug=True, share=True, server_name="tehran.emma-jewellery.ir", server_port=21401, ssl_certfile="/root/cert.crt",  ssl_keyfile="/root/private.key")
