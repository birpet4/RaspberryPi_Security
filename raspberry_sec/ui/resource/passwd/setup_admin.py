import base64
import os, sys
import getpass
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))
import raspberry_sec.ui.util as secutil


def enter_passwd():
	"""
	Reads in the password
	:return: the password
	"""
	passwd = getpass.getpass('Enter your password please: ')
	re_passwd = getpass.getpass('Repeat it please: ')

	if passwd != re_passwd:
		raise Exception('Passwords do not match!')
	else:
		return passwd


def create(salt_len: int, hash_len: int):
	"""
	Main logic
	:param salt_len: salt length
	:param hash_len: hash length
	"""
	passwd = enter_passwd()
	salt = base64.b64encode(os.urandom(salt_len)).decode()
	hash_line = salt + '$' + secutil.encode_passwd(passwd, salt, hash_len) + '$' + str(hash_len)

	with open('passwd', 'w') as passwd_file:
		passwd_file.write(hash_line)


if __name__ == '__main__':
	create(128, 256)
