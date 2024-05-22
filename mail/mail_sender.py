import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.config import settings

class MailSender():
    def __init__(self) -> None:
        self.mail = smtplib.SMTP(host='smtp.gmail.com', port=587)
        self.mail.starttls()
    
    async def send_forgot_password_email(self, email_to_be_sent_info: dict):
        self.mail.login(settings.MAIL_ADDRESS, settings.MAIL_PASSWORD)
        
        message = MIMEMultipart()
        message['From'] = settings.MAIL_ADDRESS
        message['To'] = email_to_be_sent_info["send_to"]
        message['Subject'] = "Código para recuperação de senha"
        
        message.attach(MIMEText(email_to_be_sent_info["email_info"], 'plain'))

        self.mail.sendmail(settings.MAIL_ADDRESS, email_to_be_sent_info["send_to"], message.as_string())
        self.mail.quit()
        
        return True