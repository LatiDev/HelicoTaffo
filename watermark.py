import sys
import pymupdf

def print(src: str, dst: str, text: str, fontsize: int):
    doc = pymupdf.open(src)
    tw = pymupdf.get_text_length(text, fontname="helv", fontsize=fontsize)
    step_x, step_y = tw + 40, fontsize + 90

    for page in doc:
        r = page.rect
        dm = page.derotation_matrix

        row = 0
        y = -r.height
        while y < r.height * 2:
            x = -r.width + (step_x / 2 if row % 2 else 0)
            while x < r.width * 2:
                p = pymupdf.Point(x, y) * dm
                page.insert_text(
                    p, text,
                    fontsize=fontsize, fontname="helv",
                    color=(0.5, 0.5, 0.5), fill_opacity=0.2,
                    morph=(p, pymupdf.Matrix(0)),
                    overlay=True,
                )
                x += step_x
            y += step_y
            row += 1

    doc.save(dst)