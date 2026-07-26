import io
import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

INK = HexColor("#16213E")
GOLD = HexColor("#B9822F")
INK_SOFT = HexColor("#4A5578")
HAIRLINE = HexColor("#D3D8E4")


def generate_certificate_pdf(*, student_name: str, course_title: str, site_name: str, completed_date: datetime.date) -> bytes:
    """Renders a landscape certificate of completion and returns the raw PDF bytes."""
    buffer = io.BytesIO()
    width, height = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=landscape(letter))

    # Outer border
    margin = 0.4 * inch
    c.setStrokeColor(GOLD)
    c.setLineWidth(2)
    c.rect(margin, margin, width - 2 * margin, height - 2 * margin)

    # Inner hairline border
    inner_margin = margin + 0.12 * inch
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.75)
    c.rect(inner_margin, inner_margin, width - 2 * inner_margin, height - 2 * inner_margin)

    center_x = width / 2

    # Eyebrow
    c.setFillColor(GOLD)
    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, height - 1.35 * inch, "CERTIFICATE OF COMPLETION")

    # Site name
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(center_x, height - 1.75 * inch, site_name)

    # "This certifies that"
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 2.5 * inch, "This certifies that")

    # Student name
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(center_x, height - 3.15 * inch, student_name)

    # Underline under name
    name_width = c.stringWidth(student_name, "Helvetica-Bold", 30)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(center_x - name_width / 2 - 20, height - 3.35 * inch, center_x + name_width / 2 + 20, height - 3.35 * inch)

    # "has successfully completed"
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 3.85 * inch, "has successfully completed the course")

    # Course title
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 19)
    c.drawCentredString(center_x, height - 4.4 * inch, course_title)

    # Date
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 11)
    date_str = completed_date.strftime("%B %d, %Y")
    c.drawCentredString(center_x, height - 5.3 * inch, f"Completed on {date_str}")

    # Signature line
    sig_y = 1.1 * inch
    c.setStrokeColor(INK_SOFT)
    c.setLineWidth(0.75)
    c.line(center_x - 1.6 * inch, sig_y, center_x + 1.6 * inch, sig_y)
    c.setFont("Helvetica", 10)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(center_x, sig_y - 0.2 * inch, site_name)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
