import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SMTPClient:
    def __init__(
        self, server: str, port: int, username: str, password: str, _from: str, use_tls=False, opportunistic_tls=False
    ):
        self.server = server
        self.port = port
        self._from = _from
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.opportunistic_tls = opportunistic_tls

    def send(self, mail: dict):
        smtp = None
        try:
            if self.port == 465:
                smtp = smtplib.SMTP_SSL(self.server, self.port, timeout=10)
            else:
                smtp = smtplib.SMTP(self.server, self.port, timeout=10)
                if self.use_tls:
                    smtp.starttls()

            if self.username and self.password:
                smtp.login(self.username, self.password)

            msg = MIMEMultipart()
            msg["Subject"] = mail["subject"]
            msg["From"] = self._from
            msg["To"] = mail["to"]
            msg.attach(MIMEText(mail["html"], "html"))

            smtp.sendmail(self._from, mail["to"], msg.as_string())
        except smtplib.SMTPException:
            logging.exception("SMTP error occurred")
            raise
        except TimeoutError:
            logging.exception("Timeout occurred while sending email")
            raise
        except Exception:
            logging.exception(f"Unexpected error occurred while sending email to {mail['to']}")
            raise
        finally:
            if smtp:
                try:
                    smtp.quit()
                except Exception:
                    pass
