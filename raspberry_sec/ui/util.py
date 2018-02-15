import scrypt
import base64


def encode_passwd(passwd: str, salt: str, hash_len: int):
	"""
	Creates the hash
	:param passwd: to be hashed
	:param salt: for salting
	:param hash_len: of the entire hash
	:return: hash
	"""
	return base64.b64encode(scrypt.hash(
		password=passwd,
		salt=salt,
		buflen=hash_len,
		N=1 << 15,
		r=8,
		p=1
	)).decode()


def validate(passwd: str, passwd_path: str):
	"""
	Checks the password hashes
	:param passwd: to be checked
	:param passwd_path: passwd file path
	:return: True if password hashes match
	"""
	with open(passwd_path, 'r') as passwd_file:
		hash_line = passwd_file.read()

	[salt, hash, hash_len] = hash_line.split('$')

	passwd = base64.b64encode(passwd.encode())
	new_hash = encode_passwd(passwd, salt, int(hash_len))
	return new_hash == hash
