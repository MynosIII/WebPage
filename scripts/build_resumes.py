"""Generate printable Spanish and English recruiter resumes from verified repository facts."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageTemplate, Paragraph, Spacer, Table, TableStyle

from resume_content import COPY


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf"
ACCENT = colors.HexColor("#0798AA")
INK = colors.HexColor("#11181C")
MUTED = colors.HexColor("#526168")
LINE = colors.HexColor("#D7E0E3")
PALE = colors.HexColor("#EEF8F9")


def fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and bold.exists():
        pdfmetrics.registerFont(TTFont("CVRegular", str(regular)))
        pdfmetrics.registerFont(TTFont("CVBold", str(bold)))
        return "CVRegular", "CVBold"
    return "Helvetica", "Helvetica-Bold"


REGULAR, BOLD = fonts()


def page(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(ACCENT)
    canvas.rect(0, height - 8 * mm, width, 8 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 13 * mm, width - 18 * mm, 13 * mm)
    canvas.setFont(REGULAR, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 8 * mm, "matiasignaciogaglio@gmail.com")
    canvas.drawRightString(width - 18 * mm, 8 * mm, f"{doc.page}")
    canvas.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "name": ParagraphStyle("Name", parent=base["Title"], fontName=BOLD, fontSize=27, leading=29, textColor=INK, spaceAfter=2),
        "role": ParagraphStyle("Role", parent=base["Normal"], fontName=BOLD, fontSize=11.5, leading=14, textColor=ACCENT, spaceAfter=7),
        "contact": ParagraphStyle("Contact", parent=base["Normal"], fontName=REGULAR, fontSize=8.3, leading=11, textColor=MUTED, spaceAfter=9),
        "summary": ParagraphStyle("Summary", parent=base["Normal"], fontName=REGULAR, fontSize=9.3, leading=13.2, textColor=INK, spaceAfter=8),
        "heading": ParagraphStyle("Heading", parent=base["Heading2"], fontName=BOLD, fontSize=10.5, leading=13, textColor=INK, spaceBefore=7, spaceAfter=5, borderColor=LINE, borderWidth=0, borderPadding=0),
        "body": ParagraphStyle("Body", parent=base["Normal"], fontName=REGULAR, fontSize=8.6, leading=12, textColor=INK, spaceAfter=4),
        "small": ParagraphStyle("Small", parent=base["Normal"], fontName=REGULAR, fontSize=7.8, leading=10.5, textColor=MUTED),
        "case_title": ParagraphStyle("CaseTitle", parent=base["Heading3"], fontName=BOLD, fontSize=9.2, leading=11.5, textColor=INK, spaceAfter=2),
        "case_metric": ParagraphStyle("CaseMetric", parent=base["Normal"], fontName=BOLD, fontSize=8.4, leading=11, textColor=ACCENT, spaceAfter=2),
    }


def block(label: str, value: str, st: dict[str, ParagraphStyle]):
    return [Paragraph(label, st["heading"]), Paragraph(value.replace("\n", "<br/>"), st["body"])]


def build(lang: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    content = COPY[lang]
    path = OUT / content["file"]
    doc = BaseDocTemplate(str(path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=17 * mm, title=f"Matias Gaglio - {content['role']}", author="Matias Gaglio")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="resume", frames=[frame], onPage=page)])
    st = styles()
    story = [
        Paragraph("Matías Gaglio", st["name"]),
        Paragraph(content["role"], st["role"]),
        Paragraph('<link href="mailto:matiasignaciogaglio@gmail.com">matiasignaciogaglio@gmail.com</link>  |  <link href="https://linkedin.com/in/matiasignaciogaglio">LinkedIn</link>  |  <link href="https://github.com/MynosIII">GitHub</link>  |  Buenos Aires, Argentina', st["contact"]),
        Paragraph(content["summary"], st["summary"]),
    ]
    overview = Table([[block(content["current"], content["current_value"], st), block(content["expertise"], content["expertise_value"], st)]], colWidths=[doc.width * .39, doc.width * .61])
    overview.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, -1), 10), ("LEFTPADDING", (1, 0), (1, -1), 10), ("BOX", (0, 0), (-1, -1), .5, LINE), ("BACKGROUND", (0, 0), (-1, -1), PALE)]))
    story.extend([overview, Spacer(1, 4), Paragraph(content["evidence"], st["heading"])])
    for title, metric, contribution in content["cases"]:
        story.append(KeepTogether([Paragraph(title, st["case_title"]), Paragraph(metric, st["case_metric"]), Paragraph(contribution, st["small"]), Spacer(1, 4)]))
    bottom = Table([
        [block(content["approach"], content["approach_value"], st), block(content["education"], content["education_value"], st)],
        [block(content["skills"], content["skills_value"], st), block(content["availability"], content["availability_value"], st)],
    ], colWidths=[doc.width * .58, doc.width * .42])
    bottom.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, -1), 12), ("LEFTPADDING", (1, 0), (1, -1), 12), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    story.append(bottom)
    doc.build(story)
    return path


if __name__ == "__main__":
    for language in ("es", "en"):
        print(build(language))
