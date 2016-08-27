import pytest
from phub_crypto import PhubCrypto


class TestPhubCrypto:

    def test_init(self):
        crypto = PhubCrypto(b'saltsalt', 'badpass')
        assert crypto

    def test_encrypt_decrypt(self):
        crypto = PhubCrypto(b'saltsalt', 'badpass')
        target = "This is the target string"
        ciphered = crypto.encrypt(target)
        unciphered = crypto.decrypt(ciphered)

        assert unciphered == target
