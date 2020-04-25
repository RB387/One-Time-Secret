import unittest
import sqlite3
import os
from app.app.encryption import Crypto
from app.app.dbmanager import DataBaseManager
#from app.modules.encryption import Crypto
#from app.modules.dbmanager import DataBaseManager
from fastapi.testclient import TestClient
from app.app.main import app
#from app.main import app


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        sql_create_table = """CREATE TABLE "SECRETS" (
        	                                "uuid"	TEXT NOT NULL,
        	                                "text"	TEXT NOT NULL,
        	                                "password"	TEXT,
        	                                PRIMARY KEY("uuid"))"""
        self.db_path = os.path.join(os.getcwd(), 'test_db.db')
        print(self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(sql_create_table)
        self.conn.commit()
        self.cursor.close()

        self.client = TestClient(app)
        self.manager = DataBaseManager(self.db_path)

    def tearDown(self) -> None:
        os.remove(self.db_path)

    def test_database(self) -> None:
        objects = [
            {'id': 'id-1', 'text': 'text-1', 'password': 'password-1'},
            {'id': 'id-2', 'text': 'text-2', 'password': 'password-2'},
            {'id': 'id-3', 'text': 'text-3', 'password': 'password-3'}
        ]

        for obj in objects:
            self.manager.insert(obj.get('id'), obj.get('text'), obj.get('password'))

        self.assertFalse(self.manager.does_exist('no-id'))

        for obj in objects:
            exist_result = self.manager.does_exist(obj.get('id'))
            data_result = self.manager.select(obj.get('id'))

            self.assertTrue(exist_result)
            self.assertEqual(data_result, obj.get('text'))

            self.manager.delete(obj.get('id'))
            exist_result = self.manager.does_exist(obj.get('id'))

            self.assertFalse(exist_result)

    def test_crypto(self) -> None:
        crypto = Crypto('keytoencrypt')
        test_str = 'test_Text-1'
        test_encrypted_str = crypto.encrypt(test_str)
        test_decrypted_str = crypto.decrypt(test_encrypted_str)

        self.assertEqual(test_encrypted_str, b'g67cKddqaDlrpWo9vptdKg==')
        self.assertEqual(test_decrypted_str, test_str)

    def test_api(self) -> None:
        text = 'Secret-Text'
        password = 'Secret-password'

        response = self.client.get('/generate/')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(f'/generate?secret={text}')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(f'/generate?password={password}')
        self.assertEqual(response.status_code, 400)

        response = self.client.get(f'/generate?secret={text}&password={password}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(tuple(response.json().keys()), ('secret-key',))

        secret_id = response.json().get('secret-key')

        response = self.client.get('/secrets/000-000/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(f'/secrets/{secret_id}/')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'secret': text})

        self.assertFalse(self.manager.does_exist(secret_id))

if __name__ == '__main__':
    unittest.main()