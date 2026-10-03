import subprocess, dataclasses, jinja2, os, time, pathlib, shutil

class Render:
    def __init__(self, text: str):
        self.env = jinja2.Environment(
            block_start_string=r'\BLOCK{',
            block_end_string='}',
            variable_start_string=r'\VAR{',
            variable_end_string='}',
            comment_start_string=r'\#{',
            comment_end_string='}',
            trim_blocks=True,
            autoescape=False,
            loader=jinja2.FileSystemLoader('.'),
        )
        self.env.filters['tex'] = self.latex_escape
        self.template = self.env.from_string(text)

    def latex_escape(self, s):
        repl = {
            '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
            '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}', '\\': r'\textbackslash{}',
        }
        return ''.join(repl.get(c, c) for c in str(s))

    def do(self, params):
        build = self.template.render(dataclasses.asdict(params))

        with open("temp.tex", 'w', encoding='utf-8') as file:
            file.write(build)

        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", ".", "temp.tex"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        subprocess.run(["pdflatex", "-interaction=nonstopmode", "-output-directory", ".", "temp.tex"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return "temp.pdf"