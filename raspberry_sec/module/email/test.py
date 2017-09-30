from raspberry_sec.module.email.action import EmailAction


def integration_test():
	# Given
	email_action = EmailAction()

	# When
	email_action.fire('TEST Message')


if __name__ == '__main__':
	integration_test()
