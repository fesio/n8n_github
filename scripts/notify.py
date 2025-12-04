#!/usr/bin/env python3
"""
Notification helper: Slack webhook + SMTP email
Environment variables:
- NOTIFY_SLACK_WEBHOOK: Slack Incoming Webhook URL (optional)
- NOTIFY_EMAIL_TO: recipient email address (optional)
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS (optional) for SMTP sending
"""
import os
import logging
import json
from typing import Optional

logger = logging.getLogger(__name__)


def notify_slack(message: str, webhook_url: Optional[str] = None) -> bool:
    """Send a message to Slack via incoming webhook. Returns True if successful or simulated."""
    webhook = webhook_url or os.getenv('NOTIFY_SLACK_WEBHOOK')
    if not webhook:
        logger.info("notify_slack: no webhook configured; skipping (would send): %s", message)
        return False

    try:
        import requests
        payload = {"text": message}
        resp = requests.post(webhook, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("notify_slack: sent message to Slack")
        return True
    except Exception as e:
        logger.exception("notify_slack: failed to send message: %s", e)
        return False


def notify_email(subject: str, body: str, to_addr: Optional[str] = None) -> bool:
    """Send a simple email via SMTP. Returns True if successful or simulated."""
    to_addr = to_addr or os.getenv('NOTIFY_EMAIL_TO')
    if not to_addr:
        logger.info("notify_email: no recipient configured; skipping (would send): %s - %s", subject, body)
        return False

    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    try:
        import smtplib
        from email.message import EmailMessage

        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = smtp_user or f"noreply@{smtp_host or 'localhost'}"
        msg['To'] = to_addr
        msg.set_content(body)

        if smtp_host:
            server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            logger.info("notify_email: sent email to %s", to_addr)
        else:
            # No SMTP configured — log the email content instead
            logger.info("notify_email: SMTP not configured; would send to %s: %s", to_addr, body)
        return True
    except Exception as e:
        logger.exception("notify_email: failed to send email: %s", e)
        return False
