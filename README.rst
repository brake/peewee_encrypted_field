######################
peewee_encrypted_field
######################

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?style=flat 
        :target: https://opensource.org/licenses/MIT 
        
.. image:: https://badge.fury.io/gh/brake%2Fpeewee_encrypted_field.svg
        :target: https://badge.fury.io/gh/brake%2Fpeewee_encrypted_field
        
.. image:: https://img.shields.io/badge/Python-2.7-red.svg

.. _fernet-py: https://github.com/heroku/fernet-py
.. _Fernet tokens:
.. _fernet spec: https://github.com/fernet/spec
.. _Pycrypto: https://pypi.python.org/pypi/pycrypto

Encrypted field for `Peewee ORM <https://github.com/coleifer/peewee>`_ models to save data in DB in encrypted form.

Data stored in DataBase as `Fernet tokens`_. After you define an encryption key all cryptography will be performed transparently for your application.

Uses simple fernet implementation https://github.com/heroku/fernet-py

Idea caught from SQLAlchemy's `EncryptedType <http://sqlalchemy-utils.readthedocs.io/en/latest/data_types.html#module-sqlalchemy_utils.types.encrypted>`_.

Contents
********

* `Implementation Details`_ 
* `Features`_
* `Installation`_
* `Usage`_
* `Key Derivation Example`_

.. _Implementation Details:

Implementation Details
----------------------

A fernet-py_ package can use Pycrypto_ or `M2Crypto <https://pypi.python.org/pypi/M2Crypto>`_ as backend (`details <https://github.com1/heroku/fernet-py#installation>`_). Same belongs to this module due to its dependency from fernet-py_. Note that ``pip`` uses Pycrypto_ as a default dependency when install fernet-py_. 
**Length of entire key is 32 bytes**, 16 bytes per both signing and encryption keys, as stated in `specification <https://github.com/fernet/spec/blob/master/Spec.md#key-format>`_.

.. _Features:

Features
--------

You have to set ``key`` as a property of appropriate ``EncryptedField``. **You need to set this property once per** ``Model`` **per** ``Model`` **'s** ``Field``.
If you attempt to set ``key`` property for a ``Field`` whose ``key`` already has been set, exception ``EncryptedField.KeyAlreadyExists`` will be raised. To change the ``key`` on the fly you have to explictly perform ``del SomeEncryptedField.key`` and then set this property to desired value again.

.. _Installation:

Installation
------------

``pip install peewee_encrypted_field``

or, if you downloaded source, 

``python setup.py install``

.. _Usage:

Usage
-----

At first, import module

.. code-block:: python

  from peewee import *
  from peewee_encrypted_field import EncryptedField

Then, define the model with :code:`EncryptedField`

.. code-block:: python
  
  class SecureTable(BaseModel):
      sensitive_data = EncryptedField()

      class Meta:
          db_table = 'SecureTable'

After, configure field's encryption key

.. code-block:: python
  
  SecureTable.sensitive_data.key = key_derivation_fn()  # a hypotetical key derivation 
                                                        # function returning 32 byte key

Finally, save and retrieve data in a Peewee's usual manner

.. code-block:: python

  new_secret = SecureTable(sensitive_data='My New BIG Secret')
  new_secret.save()

.. _Key Derivation Example:

Key Derivation Example
----------------------

Example Key Derivation Function baded on Pycrypto_ module.

`Please take look at this Gist <https://gist.github.com/brake/18ab6f269fdef090034d1805308422c6>`_ - it can contain more actual version of code below.

.. code-block:: python

  from binascii import unhexlify
  from functools import partial
  from Crypto.Protocol import KDF
  from Crypto.Hash import SHA512, HMAC
  
  _SALT = unhexlify('48B755AB80CD1C3DA61182D3DCD2E3A2CA869B783618FF6551FB4B0CDC3B8066')  # some salt
  _KEY_LENGTH = 32
  
  key_derivation_fn = partial(        
      KDF.PBKDF2,
      salt=_SALT,
      dkLen=_KEY_LENGTH,
      count=5000,
      prf=lambda p,s: HMAC.new(p,s,SHA512).digest()
  )

  # KDF usage
  SecureTable.sensitive_data.key = key_derivation_fn(text_password)
