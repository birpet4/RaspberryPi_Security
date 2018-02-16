import unittest
import base64
import raspberry_sec.ui.util as secutil


class TestUtilMethods(unittest.TestCase):

    def test_encode_passwd_hash_length(self):
        # Given
        passwd = 'PASSWORD'
        salt = 'SALT'
        length = 256

        # When
        hash = base64.b64decode(secutil.encode_passwd(passwd, salt, length))

        # Then
        self.assertEqual(len(hash), length)

    def test_validate_hash_line(self):
        # Given
        passwd = 'PASSWORD'
        salt = 'SALT'
        length = 256
        hash_line = '$'.join([
            salt,
            secutil.encode_passwd(passwd, salt, length),
            str(length)])

        # When
        result = secutil.validate_hash_line(passwd, hash_line)

        # Then
        self.assertTrue(result)
