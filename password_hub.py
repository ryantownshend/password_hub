"""
password_hub.py.

Save account details in an encypted YAML file.

Allow entry create / edit / delete / get behaviours
"""
import os
import sys
import yaml
import logging
from phub_crypto import PhubCrypto
from cryptography.fernet import InvalidToken

log = logging.getLogger(__name__)


class PasswordHub:
    """PasswordHub object."""

    def __init__(self, phub_config, phub_file, password):
        """__init__ for PasswordHub."""
        log.debug('PasswordHub __init__')

        self.salt = phub_config['salt']
        self.password = password
        self.file = phub_file
        self.crypto = PhubCrypto(self.salt, self.password)
        self.data = self.load_data(phub_file)

    def load_data(self, phub_file):
        """
        check for existance of phub_file.

        if file exists, load data from it,
        else return an empty list
        """
        log.debug('load_data %s' % phub_file)

        product = []

        if os.path.isfile(phub_file):
            try:
                with open(phub_file, 'r') as f:
                    cipher_text = f.read()
                    clear_text = self.crypto.decrypt(cipher_text)
                    product = yaml.load(clear_text)

            except yaml.YAMLError as exc:
                log.error("Error in data file: %s" % exc)
                sys.exit(3)

            except InvalidToken:
                log.error('Invalid password')
                sys.exit(2)

        return product

    def save_data(self):
        """save the data to the file."""
        log.debug('save_data %s' % self.file)

        yaml_data = yaml.dump(self.data, default_flow_style=False)

        cipher_text = self.crypto.encrypt(yaml_data)
        with open(self.file, 'wb') as f:
            f.write(cipher_text)
        f.close()

    def list_entries(self):
        """return list of entries."""
        log.debug('list_entries')

        product = []
        for item in self.data:
            product.append(item['entry'])

        return product

    def find_entries(self, entry):
        """given entry name, return correct dictionary."""
        log.debug('find_entries %s' % entry)

        product = []
        for item in self.data:
            if entry in item['entry']:
                product.append(item)

        return product

    def create_entry(self, entry, username, password):
        """create new entry."""
        log.debug('create_entry %s' % entry)

        # check for existing entry
        if self.find_entries(entry):
            raise ValueError("Entry '%s' already exists" % entry)

        dict = {
            'entry': entry,
            'username': username,
            'password': password,
        }

        self.data.append(dict)
        self.save_data()

    def edit_entry(self, entry, username, password):
        """edit existing entry."""
        log.debug('edit_entry %s' % entry)

        # check for existing entry
        entries = self.find_entries(entry)

        if len(entries) > 1:
            raise ValueError("Multiple entries match %s" % entry)
        elif len(entries) == 0:
            raise ValueError("No entries match %s" % entry)
        elif len(entries) == 1:
            # DO THE THING
            entry = entries[0]
            entry['username'] = username
            entry['password'] = password

            self.save_data()
