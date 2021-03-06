import unittest
import sqlite3
import os
from app.app.encryption import Crypto
from app.app.dbmanager import DataBaseManager
from fastapi.testclient import TestClient
from app.app.main import app


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_path = os.path.join(os.getcwd(), 'test_db.db')
        self.manager = DataBaseManager(self.db_path, 1)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        os.remove(self.db_path)

    def test_database(self) -> None:
        print('\nDataBase Test: ', end='')
        objects = [
            {'id': 'id-1', 'text': 'text-1', 'password': 'password-1'},
            {'id': 'id-2', 'text': 'text-2', 'password': 'password-2'},
            {'id': 'id-3', 'text': 'text-3', 'password': 'password-3'}
        ]

        for obj in objects:
            self.manager.insert(obj.get('id'),
                                obj.get('text'),
                                obj.get('password'))

        self.assertFalse(self.manager.does_exist('no-id'))

        for obj in objects:
            exist_result = self.manager.does_exist(obj.get('id'))
            data_result = self.manager.select(obj.get('id'))

            self.assertTrue(exist_result)
            self.assertEqual(data_result, (obj.get('text'), obj.get('password')))

            self.manager.delete(obj.get('id'))
            exist_result = self.manager.does_exist(obj.get('id'))

            self.assertFalse(exist_result)

        self.manager.exp_time = 0
        self.manager.insert('id-expired', 'text', 'pass')
        self.assertFalse(self.manager.does_exist('id-expired'))

        print('OK')

    def test_crypto(self) -> None:
        print('\nCrypto Test: ', end='')

        crypto = Crypto('keytoencrypt')
        test_str = 'test_Text-1'
        test_encrypted_str = crypto.encrypt(test_str)
        test_decrypted_str = crypto.decrypt(test_encrypted_str)

        self.assertEqual(test_encrypted_str, b'g67cKddqaDlrpWo9vptdKg==')
        self.assertEqual(test_decrypted_str, test_str)

        print('OK')

    def test_api(self) -> None:
        print('\nAPI Test: ', end='')

        text = 'Secret-Text'
        password = 'secretpass'

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
        self.assertEqual(response.status_code, 400)

        response = self.client.get(f'/secrets/{secret_id}?password=wrong')
        self.assertEqual(response.status_code, 401)

        response = self.client.get(f'/secrets/{secret_id}?password={password}')
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.json(), {'secret': text})

        self.assertFalse(self.manager.does_exist(secret_id))

        print('OK')

if __name__ == '__main__':
    unittest.main()
