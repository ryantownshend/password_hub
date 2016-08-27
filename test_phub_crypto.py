import pytest
from phub_crypto import PhubCrypto


class TestPhubCrypto:

    def test_init(self):
        crypto = PhubCrypto('saltsalt')
        assert crypto

    def test_encrypt_decrypt(self):
        crypto = PhubCrypto('saltsalt')
        crypto.set_key('badpass')
        target = "This is the target string"
        ciphered = crypto.encrypt(target)
        unciphered = crypto.decrypt(ciphered)

        assert unciphered == target

    def test_exceptions(self):
        crypto = PhubCrypto('saltsalt')
        with pytest.raises(ValueError):
            crypto.encrypt('ima string')
