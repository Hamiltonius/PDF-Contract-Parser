"""Email synchronization via IMAP."""
import email
import logging
from datetime import datetime
from email.header import decode_header
from typing import List, Dict, Any, Optional

from imapclient import IMAPClient

from config import get_settings

logger = logging.getLogger(__name__)


class EmailSync:
    """Sync emails from IMAP server."""

    def __init__(self):
        """Initialize email sync."""
        self.settings = get_settings()
        self.client = None

    def connect(self) -> bool:
        """
        Connect to IMAP server.

        Returns:
            True if connection successful, False otherwise
        """
        if not self.settings.email_server:
            logger.error("Email server not configured")
            return False

        try:
            self.client = IMAPClient(
                self.settings.email_server,
                port=self.settings.email_port,
                ssl=self.settings.email_use_ssl,
            )

            self.client.login(
                self.settings.email_username,
                self.settings.email_password,
            )

            logger.info(f"Successfully connected to {self.settings.email_server}")
            return True

        except Exception as e:
            logger.error(f"Error connecting to email server: {e}")
            return False

    def disconnect(self):
        """Disconnect from IMAP server."""
        if self.client:
            try:
                self.client.logout()
            except Exception as e:
                logger.warning(f"Error disconnecting: {e}")

    def get_recent_emails(
        self, folder: str = "INBOX", limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent emails from specified folder.

        Args:
            folder: Email folder to fetch from
            limit: Maximum number of emails to fetch

        Returns:
            List of email dictionaries
        """
        if not self.client:
            if not self.connect():
                return []

        try:
            self.client.select_folder(folder)

            # Search for all messages
            messages = self.client.search(["ALL"])

            # Get most recent messages
            recent_messages = list(messages)[-limit:] if len(messages) > limit else messages

            # Fetch message data
            emails = []
            for msg_id in recent_messages:
                try:
                    email_data = self._fetch_email(msg_id)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Error fetching email {msg_id}: {e}")
                    continue

            logger.info(f"Fetched {len(emails)} emails from {folder}")
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []

    def get_unread_emails(self, folder: str = "INBOX") -> List[Dict[str, Any]]:
        """
        Get unread emails from specified folder.

        Args:
            folder: Email folder to fetch from

        Returns:
            List of email dictionaries
        """
        if not self.client:
            if not self.connect():
                return []

        try:
            self.client.select_folder(folder)

            # Search for unread messages
            messages = self.client.search(["UNSEEN"])

            emails = []
            for msg_id in messages:
                try:
                    email_data = self._fetch_email(msg_id)
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    logger.warning(f"Error fetching email {msg_id}: {e}")
                    continue

            logger.info(f"Fetched {len(emails)} unread emails from {folder}")
            return emails

        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            return []

    def _fetch_email(self, msg_id: int) -> Optional[Dict[str, Any]]:
        """Fetch and parse a single email."""
        try:
            response = self.client.fetch([msg_id], ["RFC822", "FLAGS"])
            msg_data = response[msg_id]

            email_message = email.message_from_bytes(msg_data[b"RFC822"])

            # Decode subject
            subject = self._decode_header(email_message["Subject"])

            # Get sender and recipients
            sender = self._decode_header(email_message["From"])
            to = self._decode_header(email_message["To"])

            # Get body
            body = self._get_email_body(email_message)

            # Parse date
            date_str = email_message["Date"]
            received_date = email.utils.parsedate_to_datetime(date_str)

            # Check flags
            flags = msg_data[b"FLAGS"]
            is_read = b"\\Seen" in flags
            is_flagged = b"\\Flagged" in flags

            # Check for attachments
            has_attachments = any(
                part.get_content_disposition() == "attachment"
                for part in email_message.walk()
            )

            return {
                "message_id": email_message["Message-ID"],
                "subject": subject,
                "sender": sender,
                "recipients": to,
                "body": body,
                "received_date": received_date.isoformat(),
                "read": is_read,
                "flagged": is_flagged,
                "has_attachments": has_attachments,
                "metadata": {
                    "in_reply_to": email_message.get("In-Reply-To"),
                    "references": email_message.get("References"),
                },
            }

        except Exception as e:
            logger.error(f"Error parsing email {msg_id}: {e}")
            return None

    def _decode_header(self, header_value: str) -> str:
        """Decode email header."""
        if not header_value:
            return ""

        decoded_parts = decode_header(header_value)
        decoded_str = ""

        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_str += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_str += part

        return decoded_str

    def _get_email_body(self, email_message) -> str:
        """Extract email body text."""
        body = ""

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
        else:
            charset = email_message.get_content_charset() or "utf-8"
            body = email_message.get_payload(decode=True).decode(charset, errors="ignore")

        return body


def sync_recent_emails(limit: int = 50) -> List[Dict[str, Any]]:
    """Convenience function to sync recent emails."""
    sync = EmailSync()
    emails = sync.get_recent_emails(limit=limit)
    sync.disconnect()
    return emails
