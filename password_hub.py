"""
password_hub.py.

Save account details in an encypted YAML file.

Allow entry create / edit / delete / get behaviours
"""
import os
import yaml
import logging
from phub_crypto import PhubCrypto

log = logging.getLogger(__name__)


class PasswordHub:
    """PasswordHub object."""

    def __init__(self, phub_config, phub_file):
        """__init__ for PasswordHub."""
        log.debug('__init__')

        print(phub_config)

        self.salt = phub_config['salt']
        self.file = phub_file
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
                    product = yaml.load(f.read())

            except yaml.YAMLError as exc:
                log.error("Error in data file: %s" % exc)

        return product

    def save_data(self):
        """save the data to the file."""
        log.debug('save_data %s' % self.file)

        yaml_data = yaml.dump(self.data, default_flow_style=False)
        with open(self.file, 'w') as f:
            f.write(yaml_data)
        f.close()

    def list_entries(self):
        """return list of entries."""
        log.debug('list_entries')

        product = []
        for item in self.data:
            product.append(item['entry'])

        return product

    def find_entry(self, entry):
        """given entry name, return correct dictionary."""
        log.debug('find_entry %s' % entry)
        for item in self.data:
            if item['entry'] in entry:
                return item

    def create_entry(self, entry, username, password):
        """create new entry."""
        log.debug('create_entry %s' % entry)

        # check for existing entry
        if self.find_entry(entry):
            raise ValueError("Entry '%s' already exists" % entry)

        dict = {
            'entry': entry,
            'username': username,
            'password': password,
        }

        self.data.append(dict)
        self.save_data()
