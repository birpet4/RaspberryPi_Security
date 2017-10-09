import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from raspberry_sec.interface.action import Action


class EmailAction(Action):
	"""
	Action class for sending emails (with HTML content)
	"""
	LOGGER = logging.getLogger('EmailAction')
	FROM_ADDR = 'mt.raspberry.pi@gmail.com'
	TO_ADDR = 'mate.torok.de@gmail.com'
	SMTP_ADDR = 'smtp.gmail.com:587'
	SMTP_TIMEOUT = 10
	USER = 'mt.raspberry.pi'
	PASSWORD = ''

	def get_name(self):
		return 'EmailAction'

	def fire(self, msg: list):
		"""
		This method sends an email with the content set to the msg.
		:param msg: ActionMessage-s
		"""
		EmailAction.LOGGER.info('Action fired:')

		mail = MIMEMultipart('alternative')
		mail['From'] = EmailAction.FROM_ADDR
		mail['To'] = EmailAction.TO_ADDR
		mail['Subject'] = 'RaspberryPi ALERT'

		content = ''.join([m.data for m in msg])
		mail.attach(MIMEText('<html>' + content + '</html>', 'html'))

		try:
			with smtplib.SMTP(host=EmailAction.SMTP_ADDR, timeout=EmailAction.SMTP_TIMEOUT) as server:
				server.ehlo()
				server.starttls()
				server.login(EmailAction.USER, EmailAction.PASSWORD)
				server.sendmail(EmailAction.FROM_ADDR, EmailAction.TO_ADDR, mail.as_string())
			EmailAction.LOGGER.info('Email has been successfully sent')
		except Exception:
			EmailAction.LOGGER.error('Email could not be sent')
