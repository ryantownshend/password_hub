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

    def __init__(self, salt):
        """__init__."""
        log.debug('__init__')
        self.salt = bytes(salt, 'utf-8')

        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = None
        self.fernet = None

    def set_key(self, password):
        """setup_salted password."""
        log.debug('set_key')
        self.key = base64.urlsafe_b64encode(
            self.kdf.derive(bytes(password, 'utf-8'))
        )
        self.fernet = Fernet(self.key)

    def encrypt(self, thing):
        """encrypt the thing."""
        log.debug('encrypt')
        if self.fernet:
            return self.fernet.encrypt(bytes(thing, 'utf-8'))
        else:
            error = "set_key(password) before attempting operation"
            log.error(error)
            raise ValueError(error)

    def decrypt(self, thing):
        """decrypt the thing."""
        log.debug('decrypt')
        if self.fernet:
            return self.fernet.decrypt(thing).decode('utf-8')
        else:
            error = "set_key(password) before attempting operation"
            log.error(error)
            raise ValueError(error)
