"""Build proposal.pdf from proposal.html with an exact 11pt font size.

Chrome rounds font sizes to 0.01 CSS px, so 11pt (14.6667px) is written as 14.66px,
which is 10.995pt. This script prints the HTML with headless Chrome, rewrites
the font-size operators so that, after Chrome's page scaling, the text is
exactly 11pt, and rebuilds the PDF cross-reference table.

Usage: python build_pdf.py proposal.html proposal.pdf [--red]
"""

### CODE ASSISTED BY CLAUDE ###
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CHROME_SIZE = rb"14\.6599998"


def print_to_pdf(html: Path, pdf: Path) -> None:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf}", html.resolve().as_uri()],
        check=True, capture_output=True,
    )


def fix_font_size(data: bytes) -> bytes:
    """Rewrite Tf sizes in every Flate content stream and rebuild the xref table."""
    def patch_stream(match):
        header, body = match.group(1), match.group(2)
        if b"/FlateDecode" not in header:
            return match.group(0)
        try:
            content = zlib.decompress(body)
        except zlib.error:
            return match.group(0)
        if not re.search(CHROME_SIZE + rb"\s+Tf", content):
            return match.group(0)
        # Chrome's page transform (two "cm" scales) is not exactly 0.75, so derive
        # the font size that gives 11pt after the actual scaling
        scale = 1.0
        for a in re.findall(rb"([\d.]+) 0 0 -?[\d.]+ [\d.\-]+ [\d.\-]+ cm", content.split(b"Tf")[0]):
            scale *= float(a)
        exact = f"{11 / scale:.6f}".encode()
        content = re.sub(CHROME_SIZE + rb"(\s+Tf)", exact + rb"\1", content)
        new_body = zlib.compress(content)
        header = re.sub(rb"/Length\s+\d+", b"/Length " + str(len(new_body)).encode(), header)
        return header + b"stream\n" + new_body + b"\nendstream"

    data = re.sub(rb"(<<(?:(?!>>\s*stream).)*>>\s*)stream\r?\n(.*?)\r?\nendstream",
                  patch_stream, data, flags=re.S)

    # Rebuild the cross-reference table, because object offsets have changed
    body_end = data.rindex(b"xref")
    body = data[:body_end]
    offsets = {int(m.group(1)): m.start() for m in re.finditer(rb"(?m)^(\d+) 0 obj", body)}
    size = max(offsets) + 1
    xref = [b"xref", f"0 {size}".encode(), b"0000000000 65535 f "]
    for num in range(1, size):
        xref.append(f"{offsets[num]:010d} 00000 n ".encode() if num in offsets
                    else b"0000000000 65535 f ")
    trailer = re.search(rb"trailer\s*(<<.*?>>)\s*startxref", data, re.S).group(1)
    trailer = re.sub(rb"/Size\s+\d+", b"/Size " + str(size).encode(), trailer)
    return (body + b"\n".join(xref) + b"\ntrailer\n" + trailer
            + b"\nstartxref\n" + str(len(body)).encode() + b"\n%%EOF\n")


def build(html: Path, pdf: Path, red: bool = False) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        source = html
        if red:  # GenAI-marked copy: all text in red, as the course guidelines ask
            source = Path(tmp) / html.name
            source.write_text(html.read_text(encoding="utf-8").replace("<body>", '<body class="genai">'),
                              encoding="utf-8")
        raw = Path(tmp) / "raw.pdf"
        print_to_pdf(source, raw)
        pdf.write_bytes(fix_font_size(raw.read_bytes()))
####


if __name__ == "__main__":
    build(Path(sys.argv[1]), Path(sys.argv[2]), red="--red" in sys.argv)
