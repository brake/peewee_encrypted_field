# -*- coding: UTF-8 -*-
#-------------------------------------------------------------------------------
# Name: peewee_encrypted_field.py        
# Module: peewee_encrypted_field
#
# Created: 02.12.2015 14:01    
# Copyright:  (c) Constantin Roganov, 2015 - 2016 
# MIT License
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#-------------------------------------------------------------------------------
#!/usr/bin/env python

"""Encrypted field for Peewee.
Saves data to the DB as Fernet tokens.
For details about fernet see https://github.com/fernet/spec
Uses simple fernet implementation https://github.com/heroku/fernet-py
Idea caught from SQLAlchemy.
"""

import fernet
import fernet.secret as secret
from peewee import *

__author__ = 'Constantin Roganov'


class KeyIsInvalid(Exception): pass


def validate_key(key):
    """Perform a simple key validation.
    In case key is invalid raises exception.
    """
    try:
        secret.Secret(key)
    except secret.Secret.InvalidSecret as e:
        raise KeyIsInvalid(e.message)


class EncryptedField(Field):
    """Encrypted field.
    Encrypted content is a Fernet token.

    Field maintains a list of keys as map of maps where the first key is
    model_class and second key is id(self_field).
    """

    class KeyIsUndefined(RuntimeError): pass

    class KeyAlreadyExists(RuntimeError): pass

    _keys = {}
    db_field = 'text'

    def db_value(self, value):
        if not self.key:
            raise EncryptedField.KeyIsUndefined()

        return fernet.generate(self.key, value)

    def python_value(self, value):
        if not self.key:
            raise EncryptedField.KeyIsUndefined()

        return super(EncryptedField, self).python_value(
            fernet.Token(value, self.key, enforce_ttl=False).message()
        )

    def key_exists(self):
        return (self.model_class in EncryptedField._keys
                and id(self) in EncryptedField._keys[self.model_class])

    @property
    def key(self):
        return (
            EncryptedField._keys[self.model_class][id(self)] if self.key_exists() else None
        )

    @key.setter
    def key(self, key_val):
        """Allows to set key only once"""

        if self.key_exists():
            raise EncryptedField.KeyAlreadyExists()

        validate_key(key_val)

        if self.model_class not in self._keys:
            EncryptedField._keys[self.model_class] = {}

        EncryptedField._keys[self.model_class][id(self)] = key_val

    @key.deleter
    def key(self):
        if self.key_exists():
            del EncryptedField._keys[self.model_class][id(self)]



