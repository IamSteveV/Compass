"""Notifications API router"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import List, Optional
import logging

from ...config import get_settings
from ...notifications import EmailService
from ...models import ValidationReport

router = APIRouter()
logger = logging.getLogger(__name__)


class EmailTestRequest(BaseModel):
    """Request model for testing email configuration"""
    recipient: EmailStr
    subject: Optional[str] = "Test Email from Compass"
    body: Optional[str] = "This is a test email from the Architecture Validation System."


class ValidationNotificationRequest(BaseModel):
    """Request model for sending validation notification"""
    report: ValidationReport
    recipients: List[EmailStr]
    include_pdf: bool = False


class NotificationSettingsResponse(BaseModel):
    """Response model for notification settings"""
    enabled: bool
    smtp_host: str
    smtp_port: int
    from_email: str
    from_name: str
    notify_on_failure: bool
    notify_on_critical: bool
    notify_on_success: bool


@router.get("/settings")
async def get_notification_settings():
    """
    Get current notification settings

    Returns:
        Current notification configuration
    """
    settings = get_settings()

    return NotificationSettingsResponse(
        enabled=settings.email.enabled,
        smtp_host=settings.email.smtp_host,
        smtp_port=settings.email.smtp_port,
        from_email=settings.email.from_email,
        from_name=settings.email.from_name,
        notify_on_failure=settings.email.notify_on_failure,
        notify_on_critical=settings.email.notify_on_critical,
        notify_on_success=settings.email.notify_on_success
    )


@router.post("/test")
async def send_test_email(request: EmailTestRequest):
    """
    Send a test email to verify configuration

    Args:
        request: Email test request with recipient and optional subject/body

    Returns:
        Success status
    """
    settings = get_settings()

    if not settings.email.enabled:
        raise HTTPException(status_code=400, detail="Email notifications are disabled")

    if not settings.email.smtp_user or not settings.email.smtp_password:
        raise HTTPException(
            status_code=400,
            detail="SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD environment variables."
        )

    try:
        email_service = EmailService(
            smtp_host=settings.email.smtp_host,
            smtp_port=settings.email.smtp_port,
            smtp_user=settings.email.smtp_user,
            smtp_password=settings.email.smtp_password,
            use_tls=settings.email.use_tls,
            from_email=settings.email.from_email,
            from_name=settings.email.from_name
        )

        success = email_service.send_email(
            to=[request.recipient],
            subject=request.subject,
            body=request.body,
            is_html=False
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send test email")

        return {
            "success": True,
            "message": f"Test email sent successfully to {request.recipient}"
        }

    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send test email: {str(e)}")


@router.post("/send-validation-report")
async def send_validation_notification(request: ValidationNotificationRequest):
    """
    Send validation report notification via email

    Args:
        request: Notification request with report and recipients

    Returns:
        Success status
    """
    settings = get_settings()

    if not settings.email.enabled:
        raise HTTPException(status_code=400, detail="Email notifications are disabled")

    if not settings.email.smtp_user or not settings.email.smtp_password:
        raise HTTPException(
            status_code=400,
            detail="SMTP credentials not configured"
        )

    try:
        email_service = EmailService(
            smtp_host=settings.email.smtp_host,
            smtp_port=settings.email.smtp_port,
            smtp_user=settings.email.smtp_user,
            smtp_password=settings.email.smtp_password,
            use_tls=settings.email.use_tls,
            from_email=settings.email.from_email,
            from_name=settings.email.from_name
        )

        # Send appropriate notification based on report status
        if request.report.overall_status.value == "failed":
            success = email_service.send_validation_failure_notification(
                report=request.report,
                recipients=request.recipients,
                include_pdf=request.include_pdf or settings.email.attach_pdf_on_failure
            )
        else:
            success = email_service.send_validation_summary_notification(
                report=request.report,
                recipients=request.recipients
            )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send notification email")

        return {
            "success": True,
            "message": f"Notification sent successfully to {len(request.recipients)} recipient(s)",
            "recipients": request.recipients
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending validation notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")


@router.post("/send-failure-notification")
async def send_failure_notification(
    report: ValidationReport,
    recipients: List[EmailStr],
    include_pdf: bool = True
):
    """
    Send failure notification for a validation report

    Args:
        report: ValidationReport object
        recipients: List of email addresses
        include_pdf: Whether to attach PDF report

    Returns:
        Success status
    """
    settings = get_settings()

    if not settings.email.enabled:
        raise HTTPException(status_code=400, detail="Email notifications are disabled")

    try:
        email_service = EmailService(
            smtp_host=settings.email.smtp_host,
            smtp_port=settings.email.smtp_port,
            smtp_user=settings.email.smtp_user,
            smtp_password=settings.email.smtp_password,
            use_tls=settings.email.use_tls,
            from_email=settings.email.from_email,
            from_name=settings.email.from_name
        )

        success = email_service.send_validation_failure_notification(
            report=report,
            recipients=recipients,
            include_pdf=include_pdf
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to send failure notification")

        return {
            "success": True,
            "message": f"Failure notification sent to {len(recipients)} recipient(s)"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending failure notification: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
