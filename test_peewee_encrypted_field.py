# -*- coding: UTF-8 -*-
# ------------------------------------------------------------------------------
# Name: test_peewee_encrypted_field.py
# Module: peewee_encrypted_field
#
# Created: 14.10.2016
# Copyright:  (c) Constantin Roganov, 2016
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
# ------------------------------------------------------------------------------
#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
# from builtins import str

import unittest

from peewee import *
from peewee_encrypted_field import EncryptedField, KeyIsInvalid
from fernet import Token


TEST1_TABLE_DDL = '''CREATE TABLE test1(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  secret VARCHAR(255) NOT NULL,
  secret_test1 VARCHAR(255) NOT NULL)'''

TEST2_TABLE_DDL = '''CREATE TABLE test2(
  id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
  secret VARCHAR(255) NOT NULL,
  secret_test2 VARCHAR(255) NOT NULL)'''

UPDATE_TEST1_SECRET = '''UPDATE test1 SET secret=?'''


TEST_DATA1 = 'Peewee is a simple and small ORM.'
TEST_DATA2 = 'It has few (but expressive) concepts, making it easy to learn and intuitive to use.'
TEST_DATA3 = 'Quickstart guide – this guide covers all the bare essentials.'
TEST_DATA4 = 'It will take you between 5 and 10 minutes to go through it.'

KEY1 = '5C2C99CF0E19C28BDC77F763966CEA044CE4B98D11A9EE79326B35E9ADFECF18'.decode('hex')
KEY2 = '77EF36669FE66655F274A9055100970A926271D60F855FD554152DA8BF9C0BE1'.decode('hex')
KEY3 = '49C7646A1A2584C2FB4E2DE55B56BD3B3A2E60A18C7B179DD465C662D4FA4814'.decode('hex')
KEY4 = 'C2E9271809C6D126DCC6AAFEFA6097D530BE71925EB11543B270848540E43338'.decode('hex')
INVALID_KEY = 'C2E9271809C6D122FB4E2DE55B56BD3B3A2E60A18C7B179DD465C662'.decode('hex')
WRONG_KEY = 'FFFFFF1809C6D126DCC6AAFEFA6097D530BE71925EB11543B270848540E43338'.decode('hex')

def create_db_structure(peewee_db):

    peewee_db.get_conn().executescript(';\n'.join((TEST1_TABLE_DDL, TEST2_TABLE_DDL)))


db = SqliteDatabase(':memory:')

create_db_structure(db)


class BaseModel(Model):
    class Meta:
        database = db


class Test1Table(BaseModel):
    secret = EncryptedField()
    secret_test1 = EncryptedField()

    class Meta:
        db_table = 'test1'


class Test2Table(BaseModel):
    secret = EncryptedField()
    secret_test2 = EncryptedField()

    class Meta:
        db_table = 'test2'


class EncryptedFieldTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        Test1Table.secret.key = KEY1
        Test1Table.secret_test1.key = KEY2
        Test2Table.secret.key = KEY3
        Test2Table.secret_test2.key = KEY4

    def setUp(self):
        rec = Test1Table.create(secret=TEST_DATA1, secret_test1=TEST_DATA2)
        rec.save()

        rec = Test2Table.create(secret=TEST_DATA3, secret_test2=TEST_DATA4)
        rec.save()

    def tearDown(self):
        Test1Table.delete().execute()
        Test2Table.delete().execute()

    @staticmethod
    def _corrupt_test1_secret_data(peewee_db):
        """Corrupt data by direct update record"""

        peewee_db.get_conn().execute(UPDATE_TEST1_SECRET, [TEST_DATA1.encode('base64')])

    def test_table1_read(self):
        rec = Test1Table.get()

        self.assertEqual(rec.secret, TEST_DATA1)
        self.assertEqual(rec.secret_test1, TEST_DATA2)

    def test_table2_read(self):
        rec = Test2Table.get()

        self.assertEqual(rec.secret.decode('utf-8'), TEST_DATA3)
        self.assertEqual(rec.secret_test2, TEST_DATA4)

    def test_corrupted_data(self):
        EncryptedFieldTest._corrupt_test1_secret_data(db)

        with self.assertRaises(Token.InvalidToken):
            Test1Table.get()

    def test_redefine_key(self):
        with self.assertRaises(EncryptedField.KeyAlreadyExists):
            Test1Table.secret.key = KEY2

    def test_malformed_key(self):
        self.addCleanup(lambda v: setattr(Test1Table.secret, 'key', v), Test1Table.secret.key)

        del Test1Table.secret.key

        with self.assertRaises(KeyIsInvalid):
            Test1Table.secret.key = INVALID_KEY

    def test_wrong_key(self):

        def _cleanup(k):
            del Test1Table.secret.key
            Test1Table.secret.key = k

        self.addCleanup(_cleanup, Test1Table.secret.key)

        del Test1Table.secret.key
        Test1Table.secret.key = WRONG_KEY

        with self.assertRaises(Token.InvalidToken):
            Test1Table.get()

    def test_key_undefined(self):
        self.addCleanup(lambda v: setattr(Test2Table.secret, 'key', v), Test2Table.secret.key)

        del Test2Table.secret.key

        with self.assertRaises(EncryptedField.KeyIsUndefined):
            Test2Table.get()

if __name__ == '__main__':
    unittest.main()


