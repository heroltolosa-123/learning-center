import io
import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

INK = HexColor("#16213E")
GOLD = HexColor("#B9822F")
GOLD_DEEP = HexColor("#8F6421")
INK_SOFT = HexColor("#4A5578")
HAIRLINE = HexColor("#D3D8E4")
PALE_GOLD = Color(0.725, 0.510, 0.184, alpha=0.08)
PALE_INK = Color(0.086, 0.129, 0.243, alpha=0.05)


def _draw_seal_mark(c, cx, cy, radius, alpha=1.0, label_size=None):
    """Draws the Hero Academy seal mark (circle + HA monogram + ascending bars) at the given center/radius."""
    stroke_color = Color(0.725, 0.510, 0.184, alpha=alpha)
    fill_color = Color(0.561, 0.392, 0.129, alpha=alpha)
    c.setStrokeColor(stroke_color)
    c.setLineWidth(max(1, radius * 0.03))
    c.circle(cx, cy, radius, stroke=1, fill=0)

    label_size = label_size or radius * 0.55
    c.setFillColor(fill_color)
    c.setFont("Helvetica-Bold", label_size)
    c.drawCentredString(cx, cy - label_size * 0.32, "HA")

    # ascending bars motif beneath the monogram
    bar_w = radius * 0.11
    bar_gap = radius * 0.06
    bar_heights = [radius * 0.22, radius * 0.34, radius * 0.46, radius * 0.58]
    total_w = len(bar_heights) * bar_w + (len(bar_heights) - 1) * bar_gap
    start_x = cx - total_w / 2
    base_y = cy - radius * 0.55
    c.setFillColor(fill_color)
    for i, h in enumerate(bar_heights):
        x = start_x + i * (bar_w + bar_gap)
        c.rect(x, base_y, bar_w, h, stroke=0, fill=1)


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


def generate_certificate_pdf(*, student_name: str, course_title: str, site_name: str, completed_date: datetime.date) -> bytes:
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
    _draw_seal_mark(c, center_x, center_y, radius=1.9 * inch, alpha=0.05, label_size=1.05 * inch)

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
    _draw_seal_mark(c, center_x, height - 1.05 * inch, radius=0.32 * inch, alpha=1.0, label_size=0.17 * inch)

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
    _draw_seal_mark(c, stamp_cx, stamp_cy, radius=0.5 * inch, alpha=0.85, label_size=0.24 * inch)
    c.setStrokeColor(GOLD)
    c.setLineWidth(0.6)
    c.circle(stamp_cx, stamp_cy, 0.58 * inch, stroke=1, fill=0)

    # Signature line (bottom left/center)
    sig_x = center_x - 1.3 * inch
    sig_y = 1.1 * inch
    c.setStrokeColor(INK_SOFT)
    c.setLineWidth(0.75)
    c.line(sig_x - 1.5 * inch, sig_y, sig_x + 1.5 * inch, sig_y)
    c.setFont("Helvetica", 10)
    c.setFillColor(INK_SOFT)
    c.drawCentredString(sig_x, sig_y - 0.2 * inch, site_name)
    c.setFont("Helvetica", 8)
    c.drawCentredString(sig_x, sig_y - 0.36 * inch, "Issuing Authority")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.read()
