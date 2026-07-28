import io
import os
import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

INK = HexColor("#0B2E6B")
GOLD = HexColor("#B9822F")
GOLD_DEEP = HexColor("#8F6421")
INK_SOFT = HexColor("#4A5F8A")
HAIRLINE = HexColor("#D3D8E4")
PALE_GOLD = Color(0.725, 0.510, 0.184, alpha=0.08)
PALE_INK = Color(0.043, 0.180, 0.420, alpha=0.05)

SIGNATURE_PATH = os.path.join(os.path.dirname(__file__), "static", "certificate_assets", "signature.png")
LOGO_PATH = os.path.join(os.path.dirname(__file__), "static", "logo", "hero-academy-logo-transparent.png")
LOGO_WATERMARK_PATH = os.path.join(os.path.dirname(__file__), "static", "logo", "hero-academy-logo-watermark.png")
DEFAULT_ISSUER_NAME = "Dr. Hero Laurenciano Tolosa"


def _draw_logo(c, cx, cy, size, watermark=False):
    """Draws the real Hero Academy logo (square, centered) at the given center point."""
    path = LOGO_WATERMARK_PATH if watermark else LOGO_PATH
    if not os.path.exists(path):
        return
    try:
        img = ImageReader(path)
        c.drawImage(img, cx - size / 2, cy - size / 2, width=size, height=size, mask="auto", preserveAspectRatio=True)
    except Exception:
        pass


def _draw_corner_flourish(c, x, y, size, flip_x=1, flip_y=1, color=GOLD):
    """Draws a simple decorative arc flourish in one corner."""
    c.saveState()
    c.translate(x, y)
    c.scale(flip_x, flip_y)
    c.setStrokeColor(color)
    c.setLineWidth(1.1)
    c.arc(0, 0, size, size * 0.55, 0, 90)
    c.arc(size * 0.18, size * 0.18, size * 0.72, size * 0.34, 0, 90)
    c.restoreState()


def generate_certificate_pdf(*, student_name: str, course_title: str, site_name: str, completed_date: datetime.date, issuer_name: str = DEFAULT_ISSUER_NAME) -> bytes:
    """Renders a landscape, branded certificate of completion and returns the raw PDF bytes."""
    buffer = io.BytesIO()
    width, height = landscape(letter)
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    center_x = width / 2
    center_y = height / 2

    # Subtle full-page background tint
    c.setFillColor(Color(0.933, 0.945, 0.965, alpha=1))
    c.rect(0, 0, width, height, stroke=0, fill=1)
    c.setFillColor(HexColor("#FFFFFF"))
    c.rect(0.15 * inch, 0.15 * inch, width - 0.3 * inch, height - 0.3 * inch, stroke=0, fill=1)

    # Large pale watermark seal, centered behind all text
    _draw_logo(c, center_x, center_y, size=3.6 * inch, watermark=True)

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

    # Corner flourishes (all four corners)
    fl_size = 0.55 * inch
    fl_inset = inner_margin + 0.15 * inch
    _draw_corner_flourish(c, fl_inset, height - fl_inset, fl_size, flip_x=1, flip_y=-1)
    _draw_corner_flourish(c, width - fl_inset, height - fl_inset, fl_size, flip_x=-1, flip_y=-1)
    _draw_corner_flourish(c, fl_inset, fl_inset, fl_size, flip_x=1, flip_y=1)
    _draw_corner_flourish(c, width - fl_inset, fl_inset, fl_size, flip_x=-1, flip_y=1)

    # Small seal mark at top center, above the eyebrow
    _draw_logo(c, center_x, height - 1.05 * inch, size=0.64 * inch)

    # Eyebrow
    c.setFillColor(GOLD_DEEP)
    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, height - 1.55 * inch, "CERTIFICATE OF COMPLETION")

    # Site name
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(center_x, height - 1.92 * inch, site_name)

    # "This certifies that"
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 2.55 * inch, "This certifies that")

    # Student name
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 29)
    c.drawCentredString(center_x, height - 3.18 * inch, student_name)

    # Underline under name
    name_width = c.stringWidth(student_name, "Helvetica-Bold", 29)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1)
    c.line(center_x - name_width / 2 - 20, height - 3.38 * inch, center_x + name_width / 2 + 20, height - 3.38 * inch)

    # "has successfully completed"
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 13)
    c.drawCentredString(center_x, height - 3.85 * inch, "has successfully completed the course")

    # Course title
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(center_x, height - 4.35 * inch, course_title)

    # Date
    c.setFillColor(INK_SOFT)
    c.setFont("Helvetica", 11)
    date_str = completed_date.strftime("%B %d, %Y")
    c.drawCentredString(center_x, height - 5.05 * inch, f"Completed on {date_str}")

    # Official seal stamp near the signature (bottom right)
    stamp_cx = width - 2.1 * inch
    stamp_cy = 1.15 * inch
    _draw_logo(c, stamp_cx, stamp_cy, size=0.92 * inch)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.circle(stamp_cx, stamp_cy, 0.58 * inch, stroke=1, fill=0)

    # Signature block (bottom left/center) — real signature image + name + title
    sig_x = center_x - 1.3 * inch
    sig_line_y = 1.1 * inch

    if os.path.exists(SIGNATURE_PATH):
        try:
            sig_img = ImageReader(SIGNATURE_PATH)
            iw, ih = sig_img.getSize()
            draw_w = 1.7 * inch
            draw_h = draw_w * (ih / iw)
            c.drawImage(
                sig_img,
                sig_x - draw_w / 2,
                sig_line_y + 0.06 * inch,
                width=draw_w,
                height=draw_h,
                mask="auto",
                preserveAspectRatio=True,
            )
        except Exception:
            pass  # fall back to just the line + name if the image can't be read

    c.setStrokeColor(INK_SOFT)
    c.setLineWidth(0.75)
    c.line(sig_x - 1.5 * inch, sig_line_y, sig_x + 1.5 * inch, sig_line_y)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(INK)
    c.drawCentredString(sig_x, sig_line_y - 0.2 * inch, issuer_name)
    c.setFont("Helvetica", 8)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(sig_x, sig_line_y - 0.36 * inch, "Founder & Lead Instructor")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
