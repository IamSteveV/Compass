"""Unit tests for notifications module"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestEmailService:
    """Tests for EmailService"""

    def test_initialization(self):
        """Test email service can be initialized"""
        from src.notifications.email_service import EmailService

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587,
            smtp_user='user@test.com',
            smtp_password='password',
            use_tls=True,
            from_email='sender@test.com',
            from_name='Test Sender'
        )

        assert service is not None
        assert service.smtp_host == 'smtp.test.com'
        assert service.smtp_port == 587
        assert service.use_tls is True

    def test_generate_failure_subject(self):
        """Test failure email subject generation"""
        from src.notifications.email_service import EmailService
        from src.models import ValidationReport, ValidationSummary, ValidationStatus, Severity

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587
        )

        # Create mock report with critical issues
        report = Mock(spec=ValidationReport)
        report.id = 'test-123'
        report.overall_status = ValidationStatus.FAILED
        report.results = [
            Mock(status=ValidationStatus.FAILED, severity=Severity.CRITICAL),
            Mock(status=ValidationStatus.FAILED, severity=Severity.HIGH)
        ]
        report.summary = Mock(failed=2)

        subject = service._generate_failure_subject(report)

        assert 'CRITICAL' in subject
        assert 'test-123' in subject or 'test-12' in subject

    def test_generate_summary_subject(self):
        """Test summary email subject generation"""
        from src.notifications.email_service import EmailService
        from src.models import ValidationReport, ValidationSummary, ValidationStatus

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587
        )

        report = Mock(spec=ValidationReport)
        report.id = 'test-456'
        report.overall_status = ValidationStatus.PASSED
        report.summary = Mock(compliance_score=0.95)

        subject = service._generate_summary_subject(report)

        assert '95%' in subject or 'test-456' in subject or 'test-45' in subject

    @patch('src.notifications.email_service.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        from src.notifications.email_service import EmailService

        # Mock SMTP server
        mock_server = Mock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587,
            smtp_user='user@test.com',
            smtp_password='password'
        )

        result = service.send_email(
            to=['recipient@test.com'],
            subject='Test Subject',
            body='Test Body',
            is_html=False
        )

        assert result is True
        mock_server.send_message.assert_called_once()

    @patch('src.notifications.email_service.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp):
        """Test email sending failure"""
        from src.notifications.email_service import EmailService

        # Mock SMTP server to raise exception
        mock_smtp.return_value.__enter__.side_effect = Exception('SMTP Error')

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587
        )

        result = service.send_email(
            to=['recipient@test.com'],
            subject='Test Subject',
            body='Test Body'
        )

        assert result is False

    def test_email_notification_model(self):
        """Test EmailNotification pydantic model"""
        from src.notifications.email_service import EmailNotification

        notification = EmailNotification(
            recipients=['user1@test.com', 'user2@test.com'],
            subject='Test Subject',
            body='Test Body',
            cc=['cc@test.com'],
            bcc=['bcc@test.com']
        )

        assert len(notification.recipients) == 2
        assert notification.subject == 'Test Subject'
        assert len(notification.cc) == 1


class TestEmailTemplates:
    """Tests for email template generation"""

    def test_failure_body_structure(self):
        """Test failure email body contains required elements"""
        from src.notifications.email_service import EmailService
        from src.models import ValidationReport, ValidationStatus, Severity, ValidationSummary
        from datetime import datetime

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587
        )

        # Create mock report
        report = Mock(spec=ValidationReport)
        report.id = 'test-789'
        report.overall_status = ValidationStatus.FAILED
        report.timestamp = datetime.now().isoformat()
        report.source_type = 'terraform'
        report.summary = Mock(
            total_rules=10,
            passed=5,
            failed=3,
            warnings=2,
            compliance_score=0.5
        )
        report.results = [
            Mock(
                status=ValidationStatus.FAILED,
                severity=Severity.HIGH,
                rule_name='Test Rule',
                message='Test violation',
                category=Mock(value='security')
            )
        ]

        body = service._generate_failure_body(report)

        assert 'test-789' in body
        assert 'Validation Failed' in body or 'FAILED' in body.lower()
        assert '50%' in body  # Compliance score
        assert 'Test Rule' in body

    def test_summary_body_structure(self):
        """Test summary email body contains required elements"""
        from src.notifications.email_service import EmailService
        from src.models import ValidationReport, ValidationStatus
        from datetime import datetime

        service = EmailService(
            smtp_host='smtp.test.com',
            smtp_port=587
        )

        report = Mock(spec=ValidationReport)
        report.id = 'test-999'
        report.overall_status = ValidationStatus.PASSED
        report.timestamp = datetime.now().isoformat()
        report.summary = Mock(
            total_rules=10,
            passed=10,
            failed=0,
            warnings=0,
            compliance_score=1.0
        )

        body = service._generate_summary_body(report)

        assert 'test-999' in body
        assert '100%' in body
        assert 'Validation' in body
