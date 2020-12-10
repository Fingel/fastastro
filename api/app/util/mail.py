from email.message import EmailMessage
from typing import Optional
from contextlib import contextmanager
import aiosmtplib
import sys

from ..config import settings


class SMTPEmailBackend:
    async def send_mail(self, message: EmailMessage):
        await aiosmtplib.send(message, hostname=settings.smtp_host, port=settings.smtp_port)


class ConsoleEmailBackend:
    """
    Email backend does not send any mail, but logs them as plain
    text to the console
    """
    async def send_mail(self, message: EmailMessage):
        sys.stdout.write(message.as_string())
        sys.stdout.flush()


outbox = []


class TestEmailBackend:
    """
    Does not send mail, but records messages in a global
    outbox to be used with the context manager below
    """
    async def send_mail(self, message: EmailMessage):
        outbox.append(message)


@contextmanager
def record_messages():
    """
    This decorator must be used in conjunction with the TestEmailBackend
    It has no effect on other backends
    """
    global outbox
    try:
        yield outbox
    finally:
        outbox = list()


email_backends = {
    'SMTPEmailBackend': SMTPEmailBackend,
    'ConsoleEmailBackend': ConsoleEmailBackend,
    'TestEmailBackend': TestEmailBackend
}


async def send_mail(subject: str, body: str, to: str, from_address: Optional[str] = settings.from_address):
    try:
        backend_class = email_backends.get(settings.email_backend)
    except KeyError:
        raise ValueError('Email backend not available: ' + settings.email_backend)
    backend = backend_class()

    message = EmailMessage()
    message['From'] = from_address
    message['To'] = to
    message['Subject'] = subject
    message.set_content(body)

    await backend.send_mail(message)
