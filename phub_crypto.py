"""
phub_crypto - handle the crypto behaviours.

https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet

"""

import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

log = logging.getLogger(__name__)


class PhubCrypto:

    def __init__(self, salt, password):
        """__init__."""
#        log.debug('PhubCrypto __init__ : %s' % salt)
        self.salt = salt
        self.password = password

        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = None
        self.fernet = None

        self.key = base64.urlsafe_b64encode(
            self.kdf.derive(bytes(self.password, 'utf-8'))
        )
        self.fernet = Fernet(self.key)

    def encrypt(self, thing):
        """
        encrypt the thing.
        input a clear text string
        return a ciphered string
        """
        log.debug('encrypt')
        if self.fernet:
            return self.fernet.encrypt(bytes(thing, 'utf-8'))

    def decrypt(self, thing):
        """
        decrypt the thing.
        input a ciphered string
        Return a clear text string
        """
        log.debug('decrypt')
        if self.fernet:
            bytes_thing = bytes(thing, 'utf-8')
            bytes_product = self.fernet.decrypt(bytes_thing)
            # product = bytes_product.decode('utf-8')
            product = str(bytes_product, 'utf-8')
            return product

            # return self.fernet.decrypt(bytes_thing))
