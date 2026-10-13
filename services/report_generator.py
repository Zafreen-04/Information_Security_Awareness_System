"""
Academic PDF Report Generation Service
Generates formal, publication-ready research reports summarizing live assessment results,
validity analysis, reliability scores, and institutional recommendations using ReportLab.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

from config import Config
from services.statistics import get_dashboard_statistics
from services.validation import perform_validity_and_reliability_analysis

class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically display total page counts: 'Page X of Y'"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header banner text (on pages after cover)
        if self._pageNumber > 1:
            self.drawString(54, 755, "Information Security Awareness Measurement System — Empirical Research Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 747, 558, 747)
            
        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 36, text)
        self.drawString(54, 36, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} | Confidential Research Summary")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, 558, 48)
        
        self.restoreState()

def generate_pdf_report(db_path=None):
    """
    Builds a complete PDF report summarizing survey findings, validity, reliability, and recommendations.
    Returns a BytesIO stream containing the PDF document.
    """
    stats = get_dashboard_statistics(db_path)
    val = perform_validity_and_reliability_analysis(db_path)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Brand Colors
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_secondary = colors.HexColor("#1E3A8A")  # Blue 900
    c_accent = colors.HexColor("#2563EB")     # Blue 600
    c_dark = colors.HexColor("#334155")       # Slate 700
    c_light = colors.HexColor("#F8FAFC")      # Slate 50
    c_border = colors.HexColor("#E2E8F0")     # Slate 200
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=c_primary,
        alignment=0,
        spaceAfter=6
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=c_accent,
        alignment=0,
        spaceAfter=15
    )
    
    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=c_secondary,
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=c_dark,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=c_dark,
        spaceAfter=6
    )
    
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_dark
    )
    
    cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=c_primary
    )
    
    story = []
    
    # Header Banner Block
    story.append(Paragraph(Config.PROJECT_TITLE, title_style))
    story.append(Paragraph(Config.PROJECT_SUBTITLE, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=12))
    
    # Executive Summary & Metadata
    meta_data = [
        [Paragraph("<b>Report Type:</b> Academic Research Assessment", cell_style),
         Paragraph(f"<b>Generated Date:</b> {datetime.now().strftime('%B %d, %Y')}", cell_style)],
        [Paragraph(f"<b>Sample Size:</b> N = {stats['total_respondents']} ({stats['total_students']} Students, {stats['total_teachers']} Teachers)", cell_style),
         Paragraph("<b>Assessment Rubric:</b> 5-Point Likert Scale (9 Items)", cell_style)]
    ]
    meta_table = Table(meta_data, colWidths=[250, 250])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_light),
        ('BOX', (0,0), (-1,-1), 1, c_border),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))
    
    # Section 1: Study Objective & Methodology
    story.append(Paragraph("1. Study Objective & Methodology", h1_style))
    story.append(Paragraph(
        "This project implements an empirical measurement system inspired by the research paper <i>'Measuring information security behaviour of high school students and teachers'</i>. "
        "The primary objective is to quantitatively assess and compare cybersecurity behaviours across three essential focus areas: <b>Password Management</b>, <b>Social Media Use</b>, and <b>Email Use</b>.",
        body_style
    ))
    story.append(Paragraph(
        "Respondents evaluate 9 validated behavioural statements using a 5-point Likert scale (1 = Strongly Disagree to 5 = Strongly Agree). "
        "Individual responses are converted into standardized percentages: <code>percentage = (answer / 5) * 100</code>. Focus-area scores represent the mean of their constituent 3 items, and overall awareness represents the composite mean of all 9 items.",
        body_style
    ))
    
    # Awareness Classification Table
    class_data = [
        [Paragraph("Score Range (%)", cell_bold), Paragraph("Awareness Classification", cell_bold), Paragraph("Operational Definition & Action Priority", cell_bold)],
        [Paragraph("80.0% – 100.0%", cell_style), Paragraph("<b>Good</b>", cell_style), Paragraph("High security vigilance. No immediate remediation required.", cell_style)],
        [Paragraph("60.0% – 79.9%", cell_style), Paragraph("<b>Average</b>", cell_style), Paragraph("Moderate consciousness. Secondary training recommended.", cell_style)],
        [Paragraph("0.0% – 59.9%", cell_style), Paragraph("<b>Poor</b>", cell_style), Paragraph("Critical exposure risk. Immediate intervention and training required.", cell_style)]
    ]
    t_class = Table(class_data, colWidths=[110, 110, 280])
    t_class.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_class)
    story.append(Spacer(1, 12))
    
    # Section 2: Empirical Results & Student-Teacher Comparison
    story.append(Paragraph("2. Empirical Assessment Findings", h1_style))
    story.append(Paragraph(
        "The table below contrasts live findings from the system's database against the benchmark findings published in the reference research paper.",
        body_style
    ))
    
    ref = stats['reference_data']
    res_data = [
        [Paragraph("Assessment Dimension", cell_bold), 
         Paragraph("Live Project: Students", cell_bold), 
         Paragraph("Live Project: Teachers", cell_bold),
         Paragraph("Live Project: Overall", cell_bold),
         Paragraph("Reference Paper (Benchmark)", cell_bold)],
        
        [Paragraph("Password Management", cell_style),
         Paragraph(f"{stats['student_password_avg']}%", cell_style),
         Paragraph(f"{stats['teacher_password_avg']}%", cell_style),
         Paragraph(f"<b>{stats['password_avg']}%</b> ({stats['password_level']})", cell_style),
         Paragraph(f"S: {ref['students']['password_score']}% | T: {ref['teachers']['password_score']}%", cell_style)],
         
        [Paragraph("Social Media Use", cell_style),
         Paragraph(f"{stats['student_social_media_avg']}%", cell_style),
         Paragraph(f"{stats['teacher_social_media_avg']}%", cell_style),
         Paragraph(f"<b>{stats['social_media_avg']}%</b> ({stats['social_media_level']})", cell_style),
         Paragraph(f"S: {ref['students']['social_media_score']}% | T: {ref['teachers']['social_media_score']}%", cell_style)],
         
        [Paragraph("Email Use", cell_style),
         Paragraph(f"{stats['student_email_avg']}%", cell_style),
         Paragraph(f"{stats['teacher_email_avg']}%", cell_style),
         Paragraph(f"<b>{stats['email_avg']}%</b> ({stats['email_level']})", cell_style),
         Paragraph(f"S: {ref['students']['email_score']}% | T: {ref['teachers']['email_score']}%", cell_style)],
         
        [Paragraph("<b>Composite Awareness</b>", cell_bold),
         Paragraph(f"<b>{stats['student_average']}%</b> ({stats['student_level']})", cell_bold),
         Paragraph(f"<b>{stats['teacher_average']}%</b> ({stats['teacher_level']})", cell_bold),
         Paragraph(f"<b>{stats['overall_average']}%</b> ({stats['overall_level']})", cell_bold),
         Paragraph(f"All: {ref['all']['overall_score']}% ({ref['all']['awareness_level']})", cell_bold)]
    ]
    t_res = Table(res_data, colWidths=[120, 95, 95, 95, 95])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, c_light]),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#E0E7FF")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 12))
    
    # Section 3: Questionnaire Validity & Reliability Analysis
    story.append(Paragraph("3. Questionnaire Validity & Reliability Analysis", h1_style))
    story.append(Paragraph(
        f"Item validity is established using Pearson Product-Moment Item-Total Correlation (α = 0.05). "
        f"For the current sample size of N = {val['sample_size']}, the two-tailed critical correlation threshold is <b>r_crit = {val['critical_r'] if val['critical_r'] else 'N/A'}</b> (compared to r ≈ {val['reference_critical_r']} in the reference study).",
        body_style
    ))
    
    val_rows = [
        [Paragraph("Item Code", cell_bold),
         Paragraph("Focus Area", cell_bold),
         Paragraph("Mean Score (1-5)", cell_bold),
         Paragraph("Pearson r", cell_bold),
         Paragraph("p-value", cell_bold),
         Paragraph("Validity Status", cell_bold)]
    ]
    for item in val['validity_items']:
        status_color = colors.HexColor("#166534") if item['is_valid'] else colors.HexColor("#991B1B")
        status_p = Paragraph(f"<font color='{status_color}'><b>{item['status']}</b></font>", cell_style)
        val_rows.append([
            Paragraph(f"<b>{item['code']}</b>", cell_style),
            Paragraph(item['focus_area'], cell_style),
            Paragraph(str(item['mean']), cell_style),
            Paragraph(str(item['correlation']), cell_style),
            Paragraph(str(item['p_value']), cell_style),
            status_p
        ])
    t_val = Table(val_rows, colWidths=[60, 110, 80, 75, 75, 100])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 10))
    
    # Reliability Table
    story.append(Paragraph("Reliability Analysis (Cronbach's Alpha)", h2_style))
    rel_rows = [
        [Paragraph("Focus Area", cell_bold),
         Paragraph("Items (k)", cell_bold),
         Paragraph("Live Cronbach's α", cell_bold),
         Paragraph("Interpretation", cell_bold),
         Paragraph("Reference Paper α", cell_bold)]
    ]
    for k_key in ['password', 'social_media', 'email', 'overall']:
        if k_key in val['reliability']:
            r_info = val['reliability'][k_key]
            rel_rows.append([
                Paragraph(r_info['focus_area'], cell_style),
                Paragraph(str(r_info['k']), cell_style),
                Paragraph(f"<b>{r_info['alpha'] if r_info['alpha'] is not None else 'N/A'}</b>", cell_style),
                Paragraph(r_info['interpretation'], cell_style),
                Paragraph(str(r_info['ref_value']), cell_style)
            ])
    t_rel = Table(rel_rows, colWidths=[160, 60, 95, 95, 90])
    t_rel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EFF6FF")),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_rel)
    story.append(Spacer(1, 12))
    
    # Section 4: Targeted Recommendations
    story.append(Paragraph("4. Evidence-Based Recommendations", h1_style))
    recs_text = [
        "<b>1. Mandatory Teacher Cybersecurity Enablement:</b> As emphasized in the foundational research, teachers directly influence student habits. Comprehensive professional development addressing password hygiene and phishing detection must be prioritized.",
        "<b>2. Technical Controls & MFA Enforcement:</b> Transition from knowledge-only mandates to technical enforcement: require multi-factor authentication on school portals, implement password manager allowances, and isolate administrative email accounts.",
        "<b>3. Social Engineering Drills:</b> Conduct realistic phishing and social engineering simulations quarterly to reinforce vigilance regarding unexpected links and unauthorized email attachments.",
        "<b>4. Digital Footprint Curriculum Integration:</b> Embed privacy configuration modules within high school computer literacy courses, teaching students about geolocation privacy and metadata exposure."
    ]
    for r_t in recs_text:
        story.append(Paragraph(r_t, body_style))
        story.append(Spacer(1, 2))
        
    story.append(Spacer(1, 6))
    story.append(Paragraph("5. Conclusion", h1_style))
    story.append(Paragraph(
        "The empirical findings demonstrate clear behavioral variations between students and teachers. "
        "By operationalizing continuous Likert-based self-assessments alongside automated statistical validation, educational institutions can pinpoint behavioral vulnerabilities and deploy targeted, data-backed interventions.",
        body_style
    ))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
