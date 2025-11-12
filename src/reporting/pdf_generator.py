"""PDF Report Generator for validation reports"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from typing import Dict, Any, List
import io
import os

from ..models import ValidationReport, ValidationStatus, Severity


class PDFReportGenerator:
    """Generate professional PDF reports from validation results"""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()

    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0d6efd'),
            spaceBefore=20,
            spaceAfter=12,
            borderPadding=5,
            leftIndent=0
        ))

        # Status text
        self.styles.add(ParagraphStyle(
            name='StatusPassed',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#198754'),
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='StatusFailed',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#dc3545'),
            fontName='Helvetica-Bold'
        ))

        self.styles.add(ParagraphStyle(
            name='StatusWarning',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#ffc107'),
            fontName='Helvetica-Bold'
        ))

    def generate_report(self, report: ValidationReport, output_path: str = None) -> bytes:
        """
        Generate PDF report from validation results

        Args:
            report: ValidationReport object
            output_path: Optional path to save PDF file

        Returns:
            PDF content as bytes
        """
        # Create buffer for PDF
        buffer = io.BytesIO()

        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Add header
        story.extend(self._create_header(report))

        # Add executive summary
        story.extend(self._create_executive_summary(report))

        # Add pattern match section
        if report.pattern_match:
            story.extend(self._create_pattern_match_section(report))

        # Add validation results summary
        story.extend(self._create_results_summary(report))

        # Add violations detail
        story.extend(self._create_violations_detail(report))

        # Add pattern deviations
        if report.pattern_match and report.pattern_match.deviations:
            story.extend(self._create_deviations_section(report))

        # Add footer
        story.extend(self._create_footer(report))

        # Build PDF
        doc.build(story)

        # Get PDF content
        pdf_content = buffer.getvalue()
        buffer.close()

        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_content)

        return pdf_content

    def _create_header(self, report: ValidationReport) -> List:
        """Create report header"""
        elements = []

        # Title
        title = Paragraph(
            "Architecture Validation Report",
            self.styles['CustomTitle']
        )
        elements.append(title)

        # Subtitle with timestamp
        timestamp = datetime.fromisoformat(str(report.timestamp)).strftime('%B %d, %Y at %I:%M %p')
        subtitle = Paragraph(
            f"Generated on {timestamp}",
            self.styles['CustomSubtitle']
        )
        elements.append(subtitle)

        elements.append(Spacer(1, 0.3 * inch))

        # Metadata table
        metadata_data = [
            ['Report ID:', report.id],
            ['Source Type:', report.source_type.upper()],
            ['Source Identifier:', report.source_identifier or 'N/A'],
            ['Overall Status:', self._format_status(report.overall_status)]
        ]

        metadata_table = Table(metadata_data, colWidths=[2 * inch, 4 * inch])
        metadata_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(metadata_table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_executive_summary(self, report: ValidationReport) -> List:
        """Create executive summary section"""
        elements = []

        header = Paragraph("Executive Summary", self.styles['SectionHeader'])
        elements.append(header)

        summary = report.summary
        compliance_score = int(summary.compliance_score * 100)

        # Summary metrics table
        summary_data = [
            ['Metric', 'Count', 'Percentage'],
            ['Rules Passed', str(summary.passed), f"{(summary.passed / summary.total_rules * 100):.1f}%"],
            ['Warnings', str(summary.warnings), f"{(summary.warnings / summary.total_rules * 100):.1f}%"],
            ['Violations', str(summary.failed), f"{(summary.failed / summary.total_rules * 100):.1f}%"],
            ['Total Rules Evaluated', str(summary.total_rules), '100%'],
        ]

        summary_table = Table(summary_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Compliance score callout
        compliance_color = self._get_compliance_color(compliance_score)
        compliance_text = f"<font color='{compliance_color}' size='18'><b>Overall Compliance: {compliance_score}%</b></font>"
        compliance_para = Paragraph(compliance_text, self.styles['Normal'])
        elements.append(compliance_para)

        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_pattern_match_section(self, report: ValidationReport) -> List:
        """Create pattern match section"""
        elements = []

        header = Paragraph("Pattern Match Analysis", self.styles['SectionHeader'])
        elements.append(header)

        pattern_match = report.pattern_match
        similarity_score = int(pattern_match.similarity_score * 100)

        # Pattern info
        pattern_data = [
            ['Pattern Name', pattern_match.pattern_name],
            ['Pattern ID', pattern_match.pattern_id],
            ['Similarity Score', f"{similarity_score}%"],
            ['Approval Track', self._format_approval_track(report.approval_track)],
        ]

        pattern_table = Table(pattern_data, colWidths=[2 * inch, 4 * inch])
        pattern_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(pattern_table)
        elements.append(Spacer(1, 0.2 * inch))

        return elements

    def _create_results_summary(self, report: ValidationReport) -> List:
        """Create validation results summary"""
        elements = []

        header = Paragraph("Validation Results by Severity", self.styles['SectionHeader'])
        elements.append(header)

        # Count violations by severity
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }

        for result in report.results:
            if result.status == ValidationStatus.FAILED:
                severity_counts[result.severity.value] += 1

        # Create severity table
        severity_data = [
            ['Severity', 'Violation Count', 'Status'],
            ['Critical', str(severity_counts['critical']), self._get_severity_status(severity_counts['critical'])],
            ['High', str(severity_counts['high']), self._get_severity_status(severity_counts['high'])],
            ['Medium', str(severity_counts['medium']), self._get_severity_status(severity_counts['medium'])],
            ['Low', str(severity_counts['low']), self._get_severity_status(severity_counts['low'])],
        ]

        severity_table = Table(severity_data, colWidths=[2 * inch, 2 * inch, 2 * inch])
        severity_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(severity_table)
        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_violations_detail(self, report: ValidationReport) -> List:
        """Create detailed violations section"""
        elements = []

        # Get failed validations
        violations = [r for r in report.results if r.status == ValidationStatus.FAILED]

        if not violations:
            return elements

        header = Paragraph("Detailed Violations", self.styles['SectionHeader'])
        elements.append(header)

        # Group by severity
        critical_violations = [v for v in violations if v.severity == Severity.CRITICAL]
        high_violations = [v for v in violations if v.severity == Severity.HIGH]
        medium_violations = [v for v in violations if v.severity == Severity.MEDIUM]
        low_violations = [v for v in violations if v.severity == Severity.LOW]

        # Critical violations
        if critical_violations:
            elements.extend(self._create_severity_section("Critical Issues", critical_violations, '#dc3545'))

        # High violations
        if high_violations:
            elements.extend(self._create_severity_section("High Priority Issues", high_violations, '#ffc107'))

        # Medium violations
        if medium_violations:
            elements.extend(self._create_severity_section("Medium Priority Issues", medium_violations, '#0dcaf0'))

        # Low violations
        if low_violations:
            elements.extend(self._create_severity_section("Low Priority Issues", low_violations, '#6c757d'))

        return elements

    def _create_severity_section(self, title: str, violations: List, color: str) -> List:
        """Create a section for violations of a specific severity"""
        elements = []

        subtitle_text = f"<font color='{color}'><b>{title}</b></font>"
        subtitle = Paragraph(subtitle_text, self.styles['Heading3'])
        elements.append(subtitle)
        elements.append(Spacer(1, 0.1 * inch))

        for violation in violations:
            # Violation details
            violation_text = f"""
            <b>{violation.rule_id}: {violation.rule_name}</b><br/>
            <i>Category: {violation.category.value.title()}</i><br/>
            {violation.message}
            """

            if violation.resource_name:
                violation_text += f"<br/><font color='#666666'>Resource: {violation.resource_name}</font>"

            violation_para = Paragraph(violation_text, self.styles['Normal'])
            elements.append(KeepTogether(violation_para))
            elements.append(Spacer(1, 0.15 * inch))

        return elements

    def _create_deviations_section(self, report: ValidationReport) -> List:
        """Create pattern deviations section"""
        elements = []

        header = Paragraph("Pattern Deviations", self.styles['SectionHeader'])
        elements.append(header)

        deviations = report.pattern_match.deviations

        # Create numbered list
        deviation_text = "<br/>".join([f"{i + 1}. {dev}" for i, dev in enumerate(deviations)])
        deviation_para = Paragraph(deviation_text, self.styles['Normal'])
        elements.append(deviation_para)

        elements.append(Spacer(1, 0.3 * inch))

        return elements

    def _create_footer(self, report: ValidationReport) -> List:
        """Create report footer"""
        elements = []

        elements.append(Spacer(1, 0.5 * inch))

        # Footer text
        footer_text = f"""
        <para align='center'>
        <font size='8' color='#666666'>
        This report was generated by the Architecture Validation & Pattern Management System<br/>
        Report ID: {report.id} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        For questions or concerns, please contact your architecture team
        </font>
        </para>
        """

        footer_para = Paragraph(footer_text, self.styles['Normal'])
        elements.append(footer_para)

        return elements

    # Helper methods

    def _format_status(self, status: ValidationStatus) -> str:
        """Format validation status as colored text"""
        if status == ValidationStatus.PASSED:
            return "PASSED"
        elif status == ValidationStatus.FAILED:
            return "FAILED"
        else:
            return "WARNING"

    def _format_approval_track(self, track: str) -> str:
        """Format approval track"""
        if not track:
            return "N/A"
        return track.replace('_', ' ').title()

    def _get_compliance_color(self, score: int) -> str:
        """Get color for compliance score"""
        if score >= 90:
            return '#198754'  # Green
        elif score >= 70:
            return '#ffc107'  # Yellow
        else:
            return '#dc3545'  # Red

    def _get_severity_status(self, count: int) -> str:
        """Get status indicator for severity count"""
        if count == 0:
            return "✓ None"
        else:
            return f"✗ {count} found"
