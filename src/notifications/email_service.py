"""Email notification service for validation reports"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
import logging

from ..models import ValidationReport, ValidationStatus, Severity

logger = logging.getLogger(__name__)


class EmailNotification(BaseModel):
    """Email notification configuration"""
    recipients: List[EmailStr] = Field(..., description="List of email recipients")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body (HTML supported)")
    cc: Optional[List[EmailStr]] = Field(default=None, description="CC recipients")
    bcc: Optional[List[EmailStr]] = Field(default=None, description="BCC recipients")
    attachments: Optional[List[Dict[str, Any]]] = Field(default=None, description="Email attachments")


class EmailService:
    """Service for sending email notifications"""

    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True,
        from_email: str = "noreply@compass.local",
        from_name: str = "Compass Validation System"
    ):
        """
        Initialize email service

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username (if authentication required)
            smtp_password: SMTP password (if authentication required)
            use_tls: Whether to use TLS encryption
            from_email: Sender email address
            from_name: Sender display name
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.use_tls = use_tls
        self.from_email = from_email
        self.from_name = from_name

    def send_email(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        is_html: bool = True
    ) -> bool:
        """
        Send an email

        Args:
            to: List of recipient email addresses
            subject: Email subject
            body: Email body (HTML or plain text)
            cc: Optional CC recipients
            bcc: Optional BCC recipients
            attachments: Optional list of attachments (dict with 'filename' and 'content')
            is_html: Whether body is HTML (default: True)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(to)
            msg['Subject'] = subject
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

            if cc:
                msg['Cc'] = ', '.join(cc)

            # Add body
            body_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, body_type))

            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEApplication(attachment['content'])
                    part.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=attachment['filename']
                    )
                    msg.attach(part)

            # Send email
            all_recipients = to + (cc or []) + (bcc or [])

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                server.send_message(msg, self.from_email, all_recipients)

            logger.info(f"Email sent successfully to {', '.join(to)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def send_validation_failure_notification(
        self,
        report: ValidationReport,
        recipients: List[str],
        include_pdf: bool = False
    ) -> bool:
        """
        Send notification for failed validation

        Args:
            report: ValidationReport object
            recipients: List of recipient email addresses
            include_pdf: Whether to include PDF report as attachment

        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate email subject
        subject = self._generate_failure_subject(report)

        # Generate email body
        body = self._generate_failure_body(report)

        # Prepare attachments
        attachments = []
        if include_pdf:
            try:
                from ..reporting import PDFReportGenerator
                pdf_generator = PDFReportGenerator()
                pdf_content = pdf_generator.generate_report(report)
                attachments.append({
                    'filename': f'validation-report-{report.id}.pdf',
                    'content': pdf_content
                })
            except Exception as e:
                logger.error(f"Failed to generate PDF attachment: {e}")

        return self.send_email(
            to=recipients,
            subject=subject,
            body=body,
            attachments=attachments if attachments else None,
            is_html=True
        )

    def send_validation_summary_notification(
        self,
        report: ValidationReport,
        recipients: List[str]
    ) -> bool:
        """
        Send summary notification for validation (any status)

        Args:
            report: ValidationReport object
            recipients: List of recipient email addresses

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = self._generate_summary_subject(report)
        body = self._generate_summary_body(report)

        return self.send_email(
            to=recipients,
            subject=subject,
            body=body,
            is_html=True
        )

    def _generate_failure_subject(self, report: ValidationReport) -> str:
        """Generate email subject for failed validation"""
        critical_count = sum(
            1 for r in report.results
            if r.status == ValidationStatus.FAILED and r.severity == Severity.CRITICAL
        )

        if critical_count > 0:
            return f"🚨 CRITICAL: Validation Failed - {critical_count} Critical Issues ({report.id[:8]})"
        else:
            return f"⚠️ Validation Failed - {report.summary.failed} Violations ({report.id[:8]})"

    def _generate_summary_subject(self, report: ValidationReport) -> str:
        """Generate email subject for validation summary"""
        status_emoji = {
            ValidationStatus.PASSED: "✅",
            ValidationStatus.FAILED: "❌",
            ValidationStatus.WARNING: "⚠️"
        }
        emoji = status_emoji.get(report.overall_status, "ℹ️")
        compliance = int(report.summary.compliance_score * 100)

        return f"{emoji} Validation Complete - {compliance}% Compliance ({report.id[:8]})"

    def _generate_failure_body(self, report: ValidationReport) -> str:
        """Generate HTML email body for failed validation"""
        compliance_score = int(report.summary.compliance_score * 100)

        # Count violations by severity
        critical = sum(
            1 for r in report.results
            if r.status == ValidationStatus.FAILED and r.severity == Severity.CRITICAL
        )
        high = sum(
            1 for r in report.results
            if r.status == ValidationStatus.FAILED and r.severity == Severity.HIGH
        )
        medium = sum(
            1 for r in report.results
            if r.status == ValidationStatus.FAILED and r.severity == Severity.MEDIUM
        )
        low = sum(
            1 for r in report.results
            if r.status == ValidationStatus.FAILED and r.severity == Severity.LOW
        )

        # Get top violations
        violations = [r for r in report.results if r.status == ValidationStatus.FAILED]
        violations.sort(key=lambda x: ["critical", "high", "medium", "low"].index(x.severity.value))

        violations_html = ""
        for i, violation in enumerate(violations[:10], 1):  # Show top 10
            severity_color = {
                "critical": "#dc3545",
                "high": "#fd7e14",
                "medium": "#ffc107",
                "low": "#6c757d"
            }.get(violation.severity.value, "#6c757d")

            violations_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{i}</td>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                    <span style="background-color: {severity_color}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                        {violation.severity.value.upper()}
                    </span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">
                    <strong>{violation.rule_name}</strong><br/>
                    <span style="color: #666; font-size: 13px;">{violation.message}</span>
                </td>
                <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #666; font-size: 13px;">
                    {violation.category.value.title()}
                </td>
            </tr>
            """

        if len(violations) > 10:
            violations_html += f"""
            <tr>
                <td colspan="4" style="padding: 12px; text-align: center; color: #666; font-style: italic;">
                    ... and {len(violations) - 10} more violations
                </td>
            </tr>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .metrics {{ display: flex; justify-content: space-around; margin: 30px 0; }}
                .metric {{ text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px; flex: 1; margin: 0 10px; }}
                .metric-value {{ font-size: 32px; font-weight: bold; color: #dc3545; }}
                .metric-label {{ color: #666; margin-top: 8px; font-size: 14px; }}
                .compliance {{ background: #dc3545; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .compliance-score {{ font-size: 48px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #6c757d; color: white; padding: 12px; text-align: left; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 13px; }}
                .button {{ display: inline-block; background: #0d6efd; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Validation Failed</h1>
                    <p>Architecture validation has detected violations that require attention</p>
                </div>

                <div class="content">
                    <div class="compliance">
                        <div class="compliance-score">{compliance_score}%</div>
                        <div>Compliance Score</div>
                    </div>

                    <h2>Validation Summary</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Report ID</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><code>{report.id}</code></td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Source</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{report.source_type.upper()}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Timestamp</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{datetime.fromisoformat(str(report.timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Total Rules</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{report.summary.total_rules}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Passed</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #198754; font-weight: bold;">{report.summary.passed}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Failed</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #dc3545; font-weight: bold;">{report.summary.failed}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Warnings</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #ffc107; font-weight: bold;">{report.summary.warnings}</td>
                        </tr>
                    </table>

                    <h2>Violations by Severity</h2>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value" style="color: #dc3545;">{critical}</div>
                            <div class="metric-label">Critical</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" style="color: #fd7e14;">{high}</div>
                            <div class="metric-label">High</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" style="color: #ffc107;">{medium}</div>
                            <div class="metric-label">Medium</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value" style="color: #6c757d;">{low}</div>
                            <div class="metric-label">Low</div>
                        </div>
                    </div>

                    <h2>Top Violations</h2>
                    <table>
                        <tr>
                            <th style="width: 50px;">#</th>
                            <th style="width: 100px;">Severity</th>
                            <th>Rule & Message</th>
                            <th style="width: 150px;">Category</th>
                        </tr>
                        {violations_html}
                    </table>

                    <div style="text-align: center; margin: 30px 0;">
                        <p>For complete details, please review the full validation report.</p>
                    </div>
                </div>

                <div class="footer">
                    <p><strong>Architecture Validation & Pattern Management System</strong></p>
                    <p>Report ID: {report.id}</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                    <p>For questions or concerns, please contact your architecture team.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_summary_body(self, report: ValidationReport) -> str:
        """Generate HTML email body for validation summary"""
        compliance_score = int(report.summary.compliance_score * 100)

        status_info = {
            ValidationStatus.PASSED: {
                "color": "#198754",
                "emoji": "✅",
                "title": "Validation Passed",
                "message": "All validation rules passed successfully!"
            },
            ValidationStatus.FAILED: {
                "color": "#dc3545",
                "emoji": "❌",
                "title": "Validation Failed",
                "message": "Some validation rules failed. Please review the violations."
            },
            ValidationStatus.WARNING: {
                "color": "#ffc107",
                "emoji": "⚠️",
                "title": "Validation Completed with Warnings",
                "message": "Validation completed with some warnings."
            }
        }

        info = status_info.get(report.overall_status, status_info[ValidationStatus.PASSED])

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; }}
                .content {{ background: white; padding: 30px; }}
                .compliance {{ background: {info['color']}; color: white; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0; }}
                .compliance-score {{ font-size: 48px; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #6c757d; color: white; padding: 12px; text-align: left; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{info['emoji']} {info['title']}</h1>
                    <p>{info['message']}</p>
                </div>

                <div class="content">
                    <div class="compliance">
                        <div class="compliance-score">{compliance_score}%</div>
                        <div>Compliance Score</div>
                    </div>

                    <h2>Validation Summary</h2>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Report ID</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;"><code>{report.id}</code></td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Timestamp</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{datetime.fromisoformat(str(report.timestamp)).strftime('%Y-%m-%d %H:%M:%S UTC')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Total Rules</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">{report.summary.total_rules}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Passed</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #198754; font-weight: bold;">{report.summary.passed}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Failed</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #dc3545; font-weight: bold;">{report.summary.failed}</td>
                        </tr>
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6;">Warnings</td>
                            <td style="padding: 12px; border-bottom: 1px solid #dee2e6; color: #ffc107; font-weight: bold;">{report.summary.warnings}</td>
                        </tr>
                    </table>
                </div>

                <div class="footer">
                    <p><strong>Architecture Validation & Pattern Management System</strong></p>
                    <p>Report ID: {report.id}</p>
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html
