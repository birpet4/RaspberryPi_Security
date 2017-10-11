import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from raspberry_sec.module.email.action import EmailAction
from raspberry_sec.interface.action import ActionMessage


def system_test():
	# Given
	email_action = EmailAction()

	# When
	email_action.fire([
		ActionMessage('<p><b>TEST</b> Message1</p>'),
		ActionMessage('<p><a href="www.google.com">TEST</a> Message2</p>')])


if __name__ == '__main__':
	system_test()
