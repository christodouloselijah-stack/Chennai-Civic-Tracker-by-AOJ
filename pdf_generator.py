import io
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import urllib.request

def generate_pdf_report(constituency_name, updates, month_str=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom styles
    summary_style = ParagraphStyle(
        'Summary',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=11,
        spaceAfter=14,
        alignment=TA_JUSTIFY,
        textColor='#333333',
        backColor='#f0f4f8',
        borderPadding=(10, 10, 10, 10),
    )
    
    elements = []
    
    # Title
    date_context = f" for {month_str}" if month_str else ""
    elements.append(Paragraph(f"Civic Updates Report: {constituency_name}{date_context}", title_style))
    elements.append(Spacer(1, 12))
    
    # Generate Executive Summary
    total = len(updates)
    if total > 0:
        resolved = sum(1 for u in updates if u.status == "Resolved")
        in_progress = sum(1 for u in updates if u.status == "In Progress")
        reported = sum(1 for u in updates if u.status == "Reported")
        
        summary_text = (
            f"<b>Executive Summary:</b> During this period, the constituency of {constituency_name} recorded a total of {total} news updates regarding civic changes and infrastructure. "
            f"Of these highlighted projects, {resolved} have been fully resolved, showcasing active development. "
            f"Meanwhile, {in_progress} projects are currently underway, and {reported} new issues have been freshly reported by local news agencies."
        )
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 20))
    else:
        elements.append(Paragraph("No updates found for this constituency in this period.", normal_style))
    
    # Detailed News Feed
    for update in updates:
        elements.append(Paragraph(f"<b>{update.title}</b>", heading_style))
        source_info = f" | <b>Source:</b> {update.source}" if getattr(update, 'source', None) else ""
        elements.append(Paragraph(f"<b>Date:</b> {update.date} | <b>Status:</b> {update.status}{source_info}", normal_style))
        elements.append(Spacer(1, 6))
        
        desc_text = update.description or ""
        for paragraph in desc_text.split("\n\n"):
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), normal_style))
                elements.append(Spacer(1, 4))
        elements.append(Spacer(1, 6))
        
        # Load real image
        if update.image_url:
            try:
                # Add headers to avoid 403 Forbidden on some real images
                req = urllib.request.Request(
                    update.image_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                img_data = urllib.request.urlopen(req, timeout=5).read()
                img_io = io.BytesIO(img_data)
                img = Image(img_io, width=250, height=140)
                img.hAlign = 'LEFT'
                elements.append(img)
            except Exception as e:
                elements.append(Paragraph(f"(Image could not be loaded: {e})", normal_style))
                
        elements.append(Spacer(1, 20))
            
    doc.build(elements)
    buffer.seek(0)
    return buffer
