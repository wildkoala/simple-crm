"""Tests for email module."""

from unittest.mock import MagicMock, patch

import pytest

from app.email import send_email, send_password_reset_email


@pytest.mark.asyncio
async def test_send_email_dev_mode():
    """When SMTP not configured, email is logged but not sent."""
    with patch("app.email.SMTP_USERNAME", ""), patch("app.email.SMTP_PASSWORD", ""):
        # Should not raise
        await send_email("test@example.com", "Subject", "<p>HTML</p>", "Text")


@pytest.mark.asyncio
async def test_send_email_dev_mode_no_text():
    """Dev mode with no text_content."""
    with patch("app.email.SMTP_USERNAME", ""), patch("app.email.SMTP_PASSWORD", ""):
        await send_email("test@example.com", "Subject", "<p>HTML</p>")


@pytest.mark.asyncio
async def test_send_email_smtp_configured():
    """When SMTP is configured, actually try to send."""
    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.email.SMTP_USERNAME", "user@test.com"),
        patch("app.email.SMTP_PASSWORD", "password123"),
        patch("app.email.smtplib.SMTP", mock_smtp_cls),
    ):
        await send_email(
            "recipient@test.com",
            "Test Subject",
            "<p>HTML</p>",
            "Text content",
        )
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user@test.com", "password123")
        mock_server.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_smtp_html_only():
    """Send with HTML only, no text part."""
    mock_server = MagicMock()
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.email.SMTP_USERNAME", "user@test.com"),
        patch("app.email.SMTP_PASSWORD", "password123"),
        patch("app.email.smtplib.SMTP", mock_smtp_cls),
    ):
        await send_email(
            "recipient@test.com",
            "Test Subject",
            "<p>HTML only</p>",
        )
        mock_server.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_smtp_failure():
    """SMTP failure should re-raise."""
    mock_server = MagicMock()
    mock_server.starttls.side_effect = Exception("SMTP connection failed")
    mock_smtp_cls = MagicMock()
    mock_smtp_cls.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_cls.return_value.__exit__ = MagicMock(return_value=False)

    with (
        patch("app.email.SMTP_USERNAME", "user@test.com"),
        patch("app.email.SMTP_PASSWORD", "password123"),
        patch("app.email.smtplib.SMTP", mock_smtp_cls),
    ):
        with pytest.raises(Exception, match="SMTP connection failed"):
            await send_email("r@test.com", "Subject", "<p>X</p>")


@pytest.mark.asyncio
async def test_send_password_reset_email():
    """Test the password reset email builder."""
    with patch("app.email.send_email") as mock_send:
        mock_send.return_value = None
        await send_password_reset_email("user@test.com", "Test User", "token123")
        mock_send.assert_called_once()
        args = mock_send.call_args
        assert args[0][0] == "user@test.com"
        assert "Password Reset" in args[0][1]
        assert "token123" in args[0][2]  # HTML content
        assert "token123" in args[0][3]  # Text content
