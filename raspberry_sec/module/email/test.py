from raspberry_sec.module.email.action import EmailAction
from raspberry_sec.interface.action import ActionMessage


def integration_test():
	# Given
	email_action = EmailAction()

	# When
	email_action.fire([ActionMessage('TEST Message')])


if __name__ == '__main__':
	integration_test()
