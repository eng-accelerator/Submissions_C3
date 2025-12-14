from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch


def generate_pdf_from_text(title: str, content: str) -> BytesIO:
    """
    Generate a PDF from plain text and return it as a BytesIO object.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"<b>{title}</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * inch))

    # Body
    for para in content.split("\n\n"):
        story.append(
            Paragraph(para.replace("\n", "<br/>"), styles["BodyText"])
        )
        story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)

    return buffer