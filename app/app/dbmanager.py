import sqlite3
import datetime
from typing import Union
from uuid import UUID


class DataBaseManager:
    """
    A class used to communicate with SQLite database

    ...

    Attributes
    ----------
    exp_time : int
        Time to live. Expiration time for secrets

    Methods
    -------
    does_exist(secret_id: str) -> str
        :returns True if such id already exists in table and False if not

    insert(secret_id: str, secret: str, password: str) -> None
        :inserts new row into table with id, secret, password, current time

    select(secret_id: str) -> str
        :returns text message by id from table

    delete(secret_id: str) -> None
        :deletes row from table by id

    """
    def __init__(self, path: str, exp_time: int) -> None:
        '''
        :param path: Path to the database.
                    If such db doesn't exist then creates the new one
        :parm exp_time: Time to live. Expiration time for secrets
        '''
        self.exp_time = exp_time
        self.__conn = sqlite3.connect(path)
        self.__cursor = self.__conn.cursor()
        self.__try_connect()

    def does_exist(self, secret_id: Union[UUID, str]) -> bool:
        '''Check uniqueness of id

        Method check uniqueness of id and TTL.
        If life time expired, row deletes and returns False

        :param secret_id: UUID that needs to be checked
        :return: bool. True if such id exists and False if not
        '''

        sql = f'SELECT created_time FROM SECRETS WHERE uuid = "{secret_id}"'
        current_time = datetime.datetime.now()
        result = self.__cursor.execute(sql).fetchone()
        if result:
            created_time = datetime.datetime.fromtimestamp(float(result[0]))
            difference = (current_time-created_time).seconds / 60 / 60
            if difference >= self.exp_time:
                self.delete(secret_id)
            else:
                return True
        return False

    def insert(self, secret_id: UUID, secret: str, password: str) -> None:
        '''Insert new row into table with id, secret, password, current time

        :param secret_id: UUID of secret
        :param secret: text message of secret
        :param password: password for the secret
        :return: None
        '''
        time = datetime.datetime.now().timestamp()
        sql = f'''INSERT INTO SECRETS (
                    uuid, text, password, created_time) VALUES (
                    "{secret_id}", "{secret}", "{password}", "{time}")'''
        self.__cursor.execute(sql)
        self.__conn.commit()

    def select(self, secret_id: str) -> tuple:
        '''Get text message and password of secret by id

        :param secret_id: uniq id in the table
        :return: tuple with string text of secret and string password
                (text: str, password: str,)
        '''
        sql = f'SELECT text, password FROM SECRETS WHERE uuid = "{secret_id}"'
        result = self.__cursor.execute(sql).fetchone()
        return result

    def delete(self, secret_id: str) -> None:
        '''Delete row with secret from the table by id

        :param secret_id: uniq id in the table
        :return: None
        '''
        sql = f'DELETE FROM SECRETS WHERE uuid = "{secret_id}"'
        self.__cursor.execute(sql)
        self.__conn.commit()

    def __try_connect(self):
        sql = 'SELECT count(name) FROM sqlite_master ' \
              'WHERE type="table" AND name="SECRETS"'
        self.__cursor.execute(sql)
        if self.__cursor.fetchone()[0] != 1:
            sql = 'CREATE TABLE "SECRETS" (' \
                    '"uuid" TEXT NOT NULL, ' \
                    '"text" TEXT NOT NULL, ' \
                    '"password" TEXT, ' \
                    '"created_time" TEXT NOT NULL, ' \
                    'PRIMARY KEY("uuid"))'
            self.__cursor.execute(sql)
            self.__conn.commit()
