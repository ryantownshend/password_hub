from __future__ import with_statement
from setuptools import setup

setup(
    name='phub',
    version='0.1',
    description='Commandline password storage and retrieval tool',
    url='https://github.com/ryantownshend/password_hub',
    author='Ryan Townshend',
    author_email='citizen.townshend@gmail.com',
    install_requires=[
        'click>=6.7',
        'click-log>=0.1.4',
        'cryptography>=1.4',
        'PyYAML>=3.11',
        'pytest>=3.0.1',
        'pyperclip>=1.5.27',
    ],
    py_modules=[
        'phub',
        'password_hub',
        'phub_crypto',
    ],
    entry_points={
        'console_scripts': [
            'phub = phub:cli'
        ],
    },
)
