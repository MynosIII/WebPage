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


COPY = {
    "es": {
        "file": "Matias-Gaglio-CV-ES.pdf",
        "role": "Ecommerce & Amazon Growth Strategist",
        "summary": "Combino Business Intelligence, PPC y contenido visual para ayudar a marcas de ecommerce a mejorar conversión y rentabilidad. Analizo performance, detecto oportunidades y convierto datos comerciales en decisiones ejecutables.",
        "current": "ROL ACTUAL",
        "current_value": "Amazon Account Listing Manager",
        "expertise": "FOCO PROFESIONAL",
        "expertise_value": "Amazon Growth y PPC | Business Intelligence | Data-to-Creative",
        "evidence": "EVIDENCIA SELECCIONADA",
        "cases": [
            ("Amazon Growth & PPC", "US$1.560 a US$2.830 en ventas retail (+81,53%) y 6,28% a 13,69% de conversión (+118,16%) entre ventanas consecutivas de 2025. ROAS observado en la vista agregada: 6,26.", "Audité campañas y listings, reorganicé segmentación y coordiné contenido y pauta. Comparación observacional; no experimento controlado."),
            ("Business Intelligence para rentabilidad", "US$96.842,56 a US$312.480 en ventas y US$15.624,09 a US$62.314,45 de beneficio neto estimado entre julio y el corte del 27 de octubre de 2025.", "Construí la lectura mensual del portfolio y prioricé acciones cruzando ventas, publicidad, costos y margen. Marca anonimizada."),
            ("Daizzy Gear - operación Amazon", "US$874 a US$2.415 de ordered revenue entre el 14-20 y el 21-27 de junio de 2026 (+176,4% semana contra semana).", "Audité PPC, definí criterios presupuestarios y coordiné inventario, promociones, A+ Content, Storefront y catálogo. Resultado puntual, no crecimiento sostenido.")
        ],
        "approach": "ENFOQUE DE TRABAJO",
        "approach_value": "Diagnosticar la restricción - priorizar por impacto y evidencia - implementar con ownership claro - medir baseline, período, resultado y límites.",
        "skills": "HERRAMIENTAS",
        "skills_value": "Seller Central, Amazon Ads, SEO y CRO | SQL, Python, R y Power BI | GA4 y Google Ads | Reporting comercial | Arquitectura de listings | Diseño visual, 3D y automatización",
        "education": "FORMACIÓN",
        "education_value": "Licenciatura en Ciencias de la Comunicación, Universidad de Buenos Aires (UBA)\nAgente de Propaganda Médica, Universidad Favaloro",
        "availability": "DISPONIBILIDAD",
        "availability_value": "Proyectos freelance, consultoría y colaboraciones remotas.",
    },
    "en": {
        "file": "Matias-Gaglio-Resume-EN.pdf",
        "role": "Ecommerce & Amazon Growth Strategist",
        "summary": "I combine Business Intelligence, PPC and visual content to help ecommerce brands improve conversion and profitability. I analyze performance, identify opportunities and turn commercial data into executable decisions.",
        "current": "CURRENT ROLE",
        "current_value": "Amazon Account Listing Manager",
        "expertise": "PROFESSIONAL FOCUS",
        "expertise_value": "Amazon Growth and PPC | Business Intelligence | Data-to-Creative",
        "evidence": "SELECTED EVIDENCE",
        "cases": [
            ("Amazon Growth & PPC", "$1,560 to $2,830 in retail sales (+81.53%) and 6.28% to 13.69% conversion (+118.16%) across consecutive 2025 windows. Observed ROAS in the aggregate view: 6.26.", "I audited campaigns and listings, reorganized targeting, and coordinated content and media. Observational comparison; not a controlled experiment."),
            ("Business Intelligence for profitability", "$96,842.56 to $312,480 in sales and $15,624.09 to $62,314.45 in estimated net profit from July through the October 27, 2025 cutoff.", "I built the monthly portfolio view and prioritized actions by connecting sales, media, costs and margin. Brand anonymized."),
            ("Daizzy Gear - Amazon operations", "$874 to $2,415 in ordered revenue between June 14-20 and June 21-27, 2026 (+176.4% week over week).", "I audited PPC, defined budget criteria and coordinated inventory, promotions, A+ Content, Storefront and catalog. One-week recovery, not sustained growth.")
        ],
        "approach": "WORKING APPROACH",
        "approach_value": "Diagnose the constraint - prioritize by impact and evidence - implement with clear ownership - measure baseline, period, outcome and limits.",
        "skills": "TOOLS",
        "skills_value": "Seller Central, Amazon Ads, SEO and CRO | SQL, Python, R and Power BI | GA4 and Google Ads | Commercial reporting | Listing architecture | Visual design, 3D and automation",
        "education": "EDUCATION",
        "education_value": "Communication Sciences, University of Buenos Aires (UBA)\nMedical Sales Representative, Favaloro University",
        "availability": "AVAILABILITY",
        "availability_value": "Freelance projects, consulting and remote collaborations.",
    },
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
