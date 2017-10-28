from raspberry_sec.module.email.action import EmailAction
from raspberry_sec.interface.action import ActionMessage


def set_parameters():
	print('Do not forget to set the password !!!')
	parameters = dict()
	parameters['password'] = ''
	parameters['from_addr'] = 'mt.raspberry.pi@gmail.com'
	parameters['smtp_addr'] = 'smtp.gmail.com:587'
	parameters['smtp_timeout'] = 10
	parameters['subject'] = 'RaspberryPi ALERT'
	parameters['to_addr'] = 'mate.torok.de@gmail.com'
	parameters['user'] = 'mt.raspberry.pi'
	return parameters


def integration_test():
	# Given
	email_action = EmailAction(set_parameters())

	# When
	email_action.fire([
		ActionMessage('<p><b>TEST</b> Message1</p>'),
		ActionMessage('<p><a href="www.google.com">TEST</a> Message2</p>')])


if __name__ == '__main__':
	integration_test()
