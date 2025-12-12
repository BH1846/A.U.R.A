"""
Phase 7: Report Generation
Generate comprehensive PDF and JSON reports
"""
import os
from datetime import datetime
from typing import Dict, List, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import json
from pydantic import BaseModel
from config import settings
from loguru import logger


class ReportData(BaseModel):
    """Report data structure"""
    candidate_name: str
    candidate_email: str
    role_type: str
    github_url: str
    
    # Project info
    project_name: str
    project_description: str
    tech_stack: List[str]
    frameworks: List[str]
    
    # Evaluation
    overall_score: float
    understanding_score: float
    reasoning_score: float
    communication_score: float
    logic_score: float
    
    # Questions and answers
    qa_evaluations: List[Dict[str, Any]]
    
    # Analysis
    strengths: List[str]
    weaknesses: List[str]
    recommendations: str
    hire_recommendation: str
    confidence: float
    
    # Fraud detection
    fraud_detected: bool
    fraud_signals: List[str]
    
    # Metadata
    evaluation_date: str
    total_questions: int


class ReportGenerator:
    """Generate evaluation reports"""
    
    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
    
    def generate_pdf_report(self, report_data: ReportData, candidate_id: int) -> str:
        """Generate PDF report"""
        
        filename = f"candidate_{candidate_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.reports_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Title
        story.append(Paragraph("AURA - Candidate Evaluation Report", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Candidate Information
        story.append(Paragraph("Candidate Information", heading_style))
        
        candidate_info = [
            ['Name:', report_data.candidate_name],
            ['Email:', report_data.candidate_email],
            ['Role:', report_data.role_type],
            ['GitHub:', report_data.github_url],
            ['Evaluation Date:', report_data.evaluation_date],
        ]
        
        t = Table(candidate_info, colWidths=[2*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ECF0F1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*inch))
        
        # Project Summary
        story.append(Paragraph("Project Summary", heading_style))
        story.append(Paragraph(f"<b>Project:</b> {report_data.project_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Description:</b> {report_data.project_description}", styles['Normal']))
        story.append(Paragraph(f"<b>Tech Stack:</b> {', '.join(report_data.tech_stack)}", styles['Normal']))
        story.append(Paragraph(f"<b>Frameworks:</b> {', '.join(report_data.frameworks)}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Score
        story.append(Paragraph("Overall Evaluation", heading_style))
        
        # Score color coding
        def get_score_color(score):
            if score >= 80:
                return colors.HexColor('#27AE60')  # Green
            elif score >= 60:
                return colors.HexColor('#F39C12')  # Orange
            else:
                return colors.HexColor('#E74C3C')  # Red
        
        scores_data = [
            ['Metric', 'Score', 'Weight'],
            ['Overall Score', f"{report_data.overall_score:.1f}/100", '-'],
            ['Concept Understanding', f"{report_data.understanding_score:.1f}/100", '40%'],
            ['Technical Reasoning', f"{report_data.reasoning_score:.1f}/100", '30%'],
            ['Communication', f"{report_data.communication_score:.1f}/100", '20%'],
            ['Logic & Accuracy', f"{report_data.logic_score:.1f}/100", '10%'],
        ]
        
        scores_table = Table(scores_data, colWidths=[3*inch, 2*inch, 1.5*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#ECF0F1')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 1), (-1, 1), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(scores_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Recommendation
        rec_color = get_score_color(report_data.overall_score)
        rec_text = f"<b>Hiring Recommendation:</b> {report_data.hire_recommendation.upper().replace('_', ' ')} (Confidence: {report_data.confidence*100:.0f}%)"
        rec_para = Paragraph(rec_text, styles['Normal'])
        story.append(rec_para)
        story.append(Spacer(1, 0.3*inch))
        
        # Strengths & Weaknesses
        story.append(Paragraph("Strengths", heading_style))
        for strength in report_data.strengths:
            story.append(Paragraph(f"✓ {strength}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph("Areas for Improvement", heading_style))
        for weakness in report_data.weaknesses:
            story.append(Paragraph(f"• {weakness}", styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Detailed Recommendations
        story.append(Paragraph("Detailed Recommendations", heading_style))
        story.append(Paragraph(report_data.recommendations, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Fraud Detection
        if report_data.fraud_detected:
            story.append(PageBreak())
            story.append(Paragraph("⚠️ Fraud Detection Alert", heading_style))
            story.append(Paragraph("<b>Potential Issues Detected:</b>", styles['Normal']))
            for signal in report_data.fraud_signals:
                story.append(Paragraph(f"• {signal}", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
        
        # Question-by-Question Analysis
        story.append(PageBreak())
        story.append(Paragraph("Detailed Question Analysis", heading_style))
        
        for i, qa in enumerate(report_data.qa_evaluations, 1):
            story.append(Paragraph(f"<b>Question {i}: {qa.get('question', 'N/A')}</b>", styles['Normal']))
            story.append(Paragraph(f"<i>Type: {qa.get('type', 'N/A')} | Difficulty: {qa.get('difficulty', 'N/A')}</i>", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph(f"<b>Answer:</b> {qa.get('answer', 'No answer provided')[:300]}...", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            story.append(Paragraph(f"<b>Score:</b> {qa.get('score', 0):.1f}/100", styles['Normal']))
            story.append(Paragraph(f"<b>Feedback:</b> {qa.get('feedback', 'N/A')}", styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Build PDF
        try:
            doc.build(story)
            logger.success(f"PDF report generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def generate_json_report(self, report_data: ReportData, candidate_id: int) -> str:
        """Generate JSON report"""
        
        filename = f"candidate_{candidate_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.reports_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_data.dict(), f, indent=2, ensure_ascii=False)
            
            logger.success(f"JSON report generated: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            raise
    
    def generate_reports(self, report_data: ReportData, candidate_id: int) -> Dict[str, str]:
        """Generate both PDF and JSON reports"""
        
        return {
            'pdf': self.generate_pdf_report(report_data, candidate_id),
            'json': self.generate_json_report(report_data, candidate_id)
        }


# Service instance
report_generator = ReportGenerator()
