import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.module.email.action import EmailAction
from raspberry_sec.interface.action import ActionMessage


def set_parameters():
	print('Do not forget to set the password !!!')
	parameters = dict()
	parameters['from_addr'] = 'mt.raspberry.pi@gmail.com'
	parameters['smtp_addr'] = 'smtp.gmail.com:587'
	parameters['subject'] = 'RaspberryPi ALERT'
	parameters['to_addr'] = 'mate.torok.de@gmail.com'
	parameters['user'] = 'mt.raspberry.pi'
	parameters['password'] = ''
	return parameters


def integration_test():
	# Given
	email_action = EmailAction(set_parameters())

	# When
	email_action.fire([
		ActionMessage('<b>TEST</b> Message1'),
		ActionMessage('<a href="www.google.com">TEST</a> Message2')])


if __name__ == '__main__':
	integration_test()
