
from password_hub import PasswordHub


class TestPasswordHub:

    def test_init(self):

        config = {'salt': b"\xdb;+\xc1~\x07\xf4;\xb7'dL\x07H\x13\x7f"}

        phub = PasswordHub(config, 'test_data.yaml', 'badpass')
        assert phub is not None
