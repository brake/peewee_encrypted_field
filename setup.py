import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
    
requires = [
    'peewee',
    'fernet',
]

links = [
    'git+https://github.com/heroku/fernet-py#egg=fernet',
]

version = '0.0.2'

setup(
    name='peewee_encrypted_field',
    version=version,
    py_modules=['peewee_encrypted_field'],
    description='Field with encryption/decryption on save/read for use in Peewee ORM models',
    long_description=README,
    author='Constantin Roganov',
    author_email='rccbox@gmail.com',
    url='https://github.com/brake/peewee_encrypted_field',
    download_url='https://github.com/brake/peewee_mssql/archive/' + version + '.zip', 
    keywords=['database', 'ORM', 'peewee', 'encryption', 'fernet', 'ciphering'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Topic :: Database',
        'Topic :: Security',
        'Topic :: Security :: Cryptography',
    ],
    install_requires=requires,
    dependency_links=links,
)
