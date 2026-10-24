from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from xml.sax.saxutils import escape
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "submission" / "PRESENTATION_SCRIPT.docx"
markdown = (ROOT / "submission" / "PRESENTATION_SCRIPT.md").read_text(encoding="utf-8")


def run(text, bold=False, italic=False, size=22, color="1F2937"):
    props = f'<w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/><w:color w:val="{color}"/>'
    if bold: props += '<w:b/><w:bCs/>'
    if italic: props += '<w:i/><w:iCs/>'
    return f'<w:r><w:rPr>{props}</w:rPr><w:t xml:space="preserve">{escape(text)}</w:t></w:r>'


def rich(text, size=22):
    parts, pos = [], 0
    for match in re.finditer(r'(\*\*.*?\*\*|\*.*?\*)', text):
        if match.start() > pos: parts.append(run(text[pos:match.start()], size=size))
        token = match.group(0)
        parts.append(run(token[2:-2] if token.startswith("**") else token[1:-1], bold=token.startswith("**"), italic=token.startswith("*"), size=size, color="C95F19" if token.startswith("**") else "4B5563"))
        pos = match.end()
    if pos < len(text): parts.append(run(text[pos:], size=size))
    return ''.join(parts)


def paragraph(text, size=22, bold=False, italic=False, align=None, after=100):
    ppr = f'<w:spacing w:after="{after}"/>' + (f'<w:jc w:val="{align}"/>' if align else '')
    content = run(text, bold=bold, italic=italic, size=size) if bold or italic else rich(text, size)
    return f'<w:p><w:pPr>{ppr}</w:pPr>{content}</w:p>'


body = []
for line in markdown.splitlines():
    if not line.strip():
        continue
    if line.startswith("# "):
        body.append(paragraph(line[2:], 38, True, align="center", after=150))
    elif line.startswith("## "):
        body.append(paragraph(line[3:], 29, True, after=180))
    elif line.startswith("### "):
        body.append(paragraph(line[4:], 24, True, after=120))
    elif line.startswith("- "):
        body.append(paragraph("• " + line[2:], 21, after=65))
    else:
        body.append(paragraph(line, 21, after=95))

document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{"".join(body)}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="1000" w:bottom="900" w:left="1000"/></w:sectPr></w:body></w:document>'
styles = '<?xml version="1.0" encoding="UTF-8"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="22"/></w:rPr></w:rPrDefault></w:docDefaults></w:styles>'
content = '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
rels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
docrels = '<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
with ZipFile(OUT, "w", ZIP_DEFLATED) as archive:
    for name, data in {"[Content_Types].xml": content, "_rels/.rels": rels, "word/document.xml": document, "word/styles.xml": styles, "word/_rels/document.xml.rels": docrels}.items():
        archive.writestr(name, data)
print(f"Created {OUT}")
