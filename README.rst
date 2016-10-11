######################
peewee_encrypted_field
######################

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat 
        :target: https://opensource.org/licenses/MIT 
        
.. image:: https://badge.fury.io/gh/brake%2Fpeewee_encrypted_field.svg
        :target: https://badge.fury.io/gh/brake%2Fpeewee_encrypted_field
        
.. image:: https://img.shields.io/badge/Python-2.7-red.svg

Encrypted field for `Peewee ORM <https://github.com/coleifer/peewee>`_ models to save data in DB in encrypted form.

Data stored in DataBase as `Fernet tokens <https://github.com/fernet/spec>`_ . After you define an encryption key all cryptography will be performed transparently for your application.

Uses simple fernet implementation https://github.com/heroku/fernet-py

Idea caught from SQLAlchemy's `EncryptedType <http://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.encrypted>`_.

Usage
-----

.. code-block:: python

  from peewee import *
  from peewee_encrypted_field import EncryptedField

  ...
  
  class SecureTable(BaseModel):
      sensitive_data = EncryptedField()

      class Meta:
          db_table = 'SecureTable'
          
  ...
  
  
            
