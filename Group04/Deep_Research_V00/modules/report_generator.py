from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
import io

class ReportGenerator:
    """
    Generates downloadable PDF reports from Markdown text.
    """
    
    @staticmethod
    def generate_pdf_report(markdown_content: str, filename: str = "research_report.pdf") -> bytes:
        """
        Convert markdown content to a simple PDF buffer.
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Deep Research Report", styles['Title']))
        story.append(Spacer(1, 12))

        # Content (Simplified Markdown parsing)
        # In a real app, use a proper MD-to-PDF library, but for hackathon, we split by lines
        lines = markdown_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                story.append(Paragraph(line.replace('# ', ''), styles['Heading1']))
            elif line.startswith('## '):
                story.append(Paragraph(line.replace('## ', ''), styles['Heading2']))
            elif line.startswith('### '):
                story.append(Paragraph(line.replace('### ', ''), styles['Heading3']))
            elif line.startswith('- '):
                story.append(Paragraph(line, styles['Bullet']))
            else:
                if line.strip():
                    story.append(Paragraph(line, styles['BodyText']))
            story.append(Spacer(1, 6))

        try:
            doc.build(story)
        except Exception as e:
            # Fallback for complex text
            return f"Error generating PDF: {e}".encode('utf-8')
            
        buffer.seek(0)
        return buffer.getvalue()
