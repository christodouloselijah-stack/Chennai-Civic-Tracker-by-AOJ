import io
import datetime
import calendar
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Rect
import urllib.request

def format_months_label(month_str):
    if not month_str:
        return ""
    months_list = month_str.split(',')
    formatted = []
    for m in months_list:
        try:
            y, mo = map(int, m.split('-'))
            month_name = calendar.month_name[mo]
            formatted.append(f"{month_name} {y}")
        except Exception:
            formatted.append(m)
    return ", ".join(formatted)

def generate_pdf_report(constituency_name, updates, month_str=None):
    buffer = io.BytesIO()
    # Left, right margins: 36pt (0.5 inch) to maximize printable width to 540pt
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Custom colors
    c_primary = colors.HexColor('#1e3a8a') # Indigo-900
    c_secondary = colors.HexColor('#475569') # Slate-600
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=c_secondary,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'UpdateTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e293b') # Slate-800
    )
    
    normal_style = ParagraphStyle(
        'UpdateBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155') # Slate-700
    )
    
    meta_style = ParagraphStyle(
        'UpdateMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#64748b') # Slate-500
    )
    
    summary_style = ParagraphStyle(
        'SummaryText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
    )
    
    val_style = ParagraphStyle(
        'MetricVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=0
    )
    
    lbl_style = ParagraphStyle(
        'MetricLbl',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        alignment=TA_CENTER,
        spaceAfter=0
    )
    
    elements = []
    
    # Title Block
    formatted_months = format_months_label(month_str)
    date_context = f"Report Period: {formatted_months}" if formatted_months else "All-Time Aggregate Report"
    
    elements.append(Paragraph(f"Civic Updates Report: {constituency_name}", title_style))
    elements.append(Paragraph(f"{date_context} | Generated on {datetime.date.today().strftime('%B %d, %Y')}", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=c_primary, spaceBefore=0, spaceAfter=15))
    
    # Metrics calculations
    total = len(updates)
    resolved = sum(1 for u in updates if u.status == "Resolved")
    in_progress = sum(1 for u in updates if u.status == "In Progress")
    reported = sum(1 for u in updates if u.status == "Reported")
    
    if total > 0:
        # Dashboard cards
        data = [
            [
                Paragraph("<font color='#1e3a8a'>TOTAL ISSUES</font>", lbl_style),
                Paragraph("<font color='#10b981'>RESOLVED</font>", lbl_style),
                Paragraph("<font color='#d97706'>IN PROGRESS</font>", lbl_style),
                Paragraph("<font color='#dc2626'>REPORTED</font>", lbl_style)
            ],
            [
                Paragraph(f"<font color='#1e3a8a'>{total}</font>", val_style),
                Paragraph(f"<font color='#10b981'>{resolved}</font>", val_style),
                Paragraph(f"<font color='#d97706'>{in_progress}</font>", val_style),
                Paragraph(f"<font color='#dc2626'>{reported}</font>", val_style)
            ]
        ]
        
        # Total printable width is 540pt (letter width=612 - 72 margins)
        metrics_table = Table(data, colWidths=[135, 135, 135, 135])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,1), colors.HexColor('#eff6ff')), # Light blue
            ('BACKGROUND', (1,0), (1,1), colors.HexColor('#ecfdf5')), # Light green
            ('BACKGROUND', (2,0), (2,1), colors.HexColor('#fffbeb')), # Light yellow
            ('BACKGROUND', (3,0), (3,1), colors.HexColor('#fef2f2')), # Light red
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOX', (0,0), (0,-1), 1.5, colors.HexColor('#bfdbfe')),
            ('BOX', (1,0), (1,-1), 1.5, colors.HexColor('#a7f3d0')),
            ('BOX', (2,0), (2,-1), 1.5, colors.HexColor('#fde68a')),
            ('BOX', (3,0), (3,-1), 1.5, colors.HexColor('#fecaca')),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 12))
        
        # Visual stacked progress bar chart (Graphic report)
        d = Drawing(540, 20)
        d.add(Rect(0, 2, 540, 14, fillColor=colors.HexColor('#f1f5f9'), strokeColor=None))
        
        curr_x = 0
        if resolved > 0:
            w = (resolved / total) * 540
            d.add(Rect(curr_x, 2, w, 14, fillColor=colors.HexColor('#10b981'), strokeColor=None))
            curr_x += w
        if in_progress > 0:
            w = (in_progress / total) * 540
            d.add(Rect(curr_x, 2, w, 14, fillColor=colors.HexColor('#f59e0b'), strokeColor=None))
            curr_x += w
        if reported > 0:
            w = (reported / total) * 540
            d.add(Rect(curr_x, 2, w, 14, fillColor=colors.HexColor('#ef4444'), strokeColor=None))
            curr_x += w
            
        elements.append(d)
        elements.append(Spacer(1, 15))
        
        # Executive Summary paragraph
        summary_text = (
            f"<b>Executive Summary:</b> During the specified period, the constituency of <b>{constituency_name}</b> "
            f"registered a total of <b>{total}</b> civic updates and infrastructure reports. "
            f"Out of these, <b>{resolved}</b> projects ({round((resolved/total)*100,1)}%) have been successfully resolved, "
            f"<b>{in_progress}</b> updates are in progress, and <b>{reported}</b> issues are currently reported and pending resolution."
        )
        
        # Box summary table
        summary_p = Paragraph(summary_text, summary_style)
        summary_table = Table([[summary_p]], colWidths=[540])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor('#f8fafc')),
            ('BOX', (0,0), (0,0), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0,0), (0,0), 10),
            ('BOTTOMPADDING', (0,0), (0,0), 10),
            ('LEFTPADDING', (0,0), (0,0), 12),
            ('RIGHTPADDING', (0,0), (0,0), 12),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
    else:
        elements.append(Paragraph("No updates found for this constituency in this period.", normal_style))
        elements.append(Spacer(1, 20))
        
    # Detailed News Feed Heading
    feed_title_style = ParagraphStyle(
        'FeedTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=c_primary,
        spaceAfter=10
    )
    elements.append(Paragraph("Detailed Updates Log", feed_title_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=0, spaceAfter=15))
    
    # Detailed updates list
    badge_style = ParagraphStyle(
        'BadgeText',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        alignment=TA_CENTER,
        textColor=colors.white
    )
    
    for idx, update in enumerate(updates):
        # 1. Title and status badge
        if update.status == "Resolved":
            badge_bg = '#10b981'
        elif update.status == "In Progress":
            badge_bg = '#f59e0b'
        else:
            badge_bg = '#ef4444'
            
        badge_p = Paragraph(update.status.upper(), badge_style)
        badge_table = Table([[badge_p]], colWidths=[85])
        badge_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,0), colors.HexColor(badge_bg)),
            ('ALIGN', (0,0), (0,0), 'CENTER'),
            ('VALIGN', (0,0), (0,0), 'MIDDLE'),
            ('TOPPADDING', (0,0), (0,0), 3),
            ('BOTTOMPADDING', (0,0), (0,0), 3),
            ('LEFTPADDING', (0,0), (0,0), 6),
            ('RIGHTPADDING', (0,0), (0,0), 6),
        ]))
        
        title_p = Paragraph(f"<b>{update.title}</b>", heading_style)
        
        header_table = Table([[title_p, badge_table]], colWidths=[445, 95])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 4))
        
        # 2. Metadata line
        source_lbl = f" | Source: {update.source}" if getattr(update, 'source', None) else ""
        meta_text = f"DATE: {update.date}{source_lbl}"
        elements.append(Paragraph(meta_text, meta_style))
        elements.append(Spacer(1, 6))
        
        # 3. Description
        desc_text = update.description or ""
        for paragraph in desc_text.split("\n\n"):
            if paragraph.strip():
                elements.append(Paragraph(paragraph.strip(), normal_style))
                elements.append(Spacer(1, 5))
                
        # 4. Optional Image
        if update.image_url:
            try:
                req = urllib.request.Request(
                    update.image_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                img_data = urllib.request.urlopen(req, timeout=5).read()
                img_io = io.BytesIO(img_data)
                img = Image(img_io, width=240, height=135)
                img.hAlign = 'LEFT'
                elements.append(Spacer(1, 4))
                elements.append(img)
            except Exception:
                pass
                
        elements.append(Spacer(1, 10))
        
        # 5. Item separator
        if idx < total - 1:
            elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceBefore=8, spaceAfter=12))
            
    doc.build(elements)
    buffer.seek(0)
    return buffer
