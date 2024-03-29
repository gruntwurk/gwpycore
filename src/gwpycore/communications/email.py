from pathlib import Path
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from typing import Union

__all__ = [
    "mail_server",
    "send_mail",
]

import logging

LOG = logging.getLogger("main")


def mail_server(server="localhost", port=465, username='', password='', use_tls=False) -> smtplib.SMTP:
    """
    Establishes a connection to an SMTP mail server.

    :param server: URL of the server
    :param port: defaults to 587
    :param username: login ID
    :param password: corresponding password
    :param use_tls: defaults to True
    """
    smtp = smtplib.SMTP_SSL(timeout=2.0)
    smtp._host = server  # bug workaround to prevent "server_hostname cannot be an empty string or start with a leading dot."
    smtp.connect(server, port)
    if use_tls:
        smtp.starttls()
    smtp.login(username, password)
    return smtp


def send_mail(smtp: smtplib.SMTP, send_from: str, send_to: Union[str, list], subject: str, body: str, attachments=None):
    """
    Send a basic email to one or more recipients.

    :usage:
        smtp = mail_server(...)
        send_mail(smtp, ...)
        send_mail(smtp, ...)
        smtp.quit()
    """
    if attachments is None:
        attachments = []
    if isinstance(send_to, str):
        send_to = [send_to]

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(body))

    for attachment_path_str in attachments:
        attachment_path = Path(attachment_path_str)
        if not attachment_path.exists():
            LOG.warning(f"Unable to attach a file that doesn't exist: {attachment_path_str}")
            continue
        part = MIMEBase('application', "octet-stream")
        with open(attachment_path_str, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        f'attachment; filename={Path(attachment_path_str).name}')
        msg.attach(part)

    smtp.sendmail(send_from, send_to, msg.as_string())
