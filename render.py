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

    def do(self, params, tex="temp.tex", pdf="tempd.pdf"):
        build = self.template.render(dataclasses.asdict(params))

        with open(tex, 'w', encoding='utf-8') as file:
            file.write(build)

        tex_path = pathlib.Path(tex)

        for _ in range(2):
            subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    tex_path.name
                ],
                cwd=tex_path.parent,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        return pdf
