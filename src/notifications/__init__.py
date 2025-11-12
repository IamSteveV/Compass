"""Notifications module for sending alerts and reports"""

from .email_service import EmailService, EmailNotification

__all__ = ['EmailService', 'EmailNotification']
