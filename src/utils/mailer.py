import os
import smtplib
from email.message import EmailMessage
from typing import Optional
from email.utils import formataddr

from email_validator import validate_email, EmailNotValidError


class Mailer:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_name = os.getenv("FROM_NAME", "")
        self.reply_to = os.getenv("REPLY_TO", "")

        missing = []
        if not self.smtp_user:
            missing.append("SMTP_USER")
        if not self.smtp_password:
            missing.append("SMTP_PASSWORD")
        if missing:
            raise RuntimeError(
                f"Config SMTP incompleta. Faltan: {', '.join(missing)}. Define estas variables en .env"
            )

    def _build_message(self, to: str, subject: str, html: str) -> EmailMessage:
        # Validar correo destino
        try:
            validate_email(to)
        except EmailNotValidError as e:
            raise ValueError(f"Correo inválido: {to} ({e})")

        msg = EmailMessage()
        from_addr = self.smtp_user
        if self.from_name:
            msg["From"] = formataddr((self.from_name, from_addr))
        else:
            msg["From"] = from_addr
        msg["To"] = to
        msg["Subject"] = subject
        if self.reply_to:
            msg["Reply-To"] = self.reply_to

        msg.set_content("Este mensaje requiere un cliente compatible con HTML.")
        msg.add_alternative(html, subtype="html")
        return msg

    def send_email(self, to: str, subject: str, html: str):
        msg = self._build_message(to, subject, html)

        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)

    def test_connection(self):
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls()
            server.login(self.smtp_user, self.smtp_password)
