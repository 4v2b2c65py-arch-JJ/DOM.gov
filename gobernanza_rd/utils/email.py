"""Magic-link email delivery."""
import asyncio
import smtplib
from email.message import EmailMessage

import structlog

from config.settings import get_settings

settings = get_settings()
logger = structlog.get_logger()


def _render_email(
    magic_link: str, locale: str, is_temp: bool, expiry_minutes: int
) -> tuple[str, str]:
    if locale.startswith("en"):
        subject = "Your GobernanzaRD sign-in link"
        body = (
            "Hello,\n\n"
            f"Use this link to sign in:\n{magic_link}\n\n"
            f"The link expires in {expiry_minutes} minutes.\n"
        )
    else:
        subject = "Tu enlace de acceso a GobernanzaRD"
        body = (
            "Hola,\n\n"
            f"Usa este enlace para iniciar sesion:\n{magic_link}\n\n"
            f"El enlace expira en {expiry_minutes} minutos.\n"
        )
    if is_temp:
        body += (
            "\nNota: usaste un correo temporal. Para desbloquear mas funciones, "
            "registra un correo permanente.\n"
        )
    return subject, body


async def send_magic_link_email(
    to_email: str,
    magic_link: str,
    locale: str = "es",
    is_temp: bool = False,
    expiry_minutes: int = 15,
) -> bool:
    subject, body = _render_email(magic_link, locale, is_temp, expiry_minutes)

    def _send() -> None:
        message = EmailMessage()
        message["From"] = settings.EMAIL_FROM
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)

    try:
        await asyncio.to_thread(_send)
        return True
    except Exception as exc:
        logger.error("magic_link_email_failed", error=str(exc))
        return False