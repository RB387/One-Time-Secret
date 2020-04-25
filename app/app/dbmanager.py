import sqlite3
import datetime


class DataBaseManager:
    """
    A class used to communicate with SQLite database

    ...

    Methods
    -------
    does_exist(id: str) -> str
        :returns True if such id already exists in table and False if not

    insert(id: str, secret: str, password: str) -> None
        :inserts new row into table with id, secret, password, current time

    select(id: str) -> str
        :returns text message by id from table

    delete(id: str) -> None
        :deletes row from table by id

    """
    def __init__(self, path: str, exp_time: int) -> None:
        '''
        :param path: Path to the database.
                    If such db doesn't exist then creates the new one
        '''
        self.exp_time = exp_time
        self.__conn = sqlite3.connect(path)
        self.__cursor = self.__conn.cursor()
        self.__try_connect()

    def does_exist(self, id: str) -> bool:
        '''Check uniqueness of id

        Method check uniqueness of id and TTL.
        If life time expired, row deletes and returns False

        :param id: UUID that needs to be checked
        :return: bool. True if such id exists and False if not
        '''

        sql = f'SELECT created_time FROM SECRETS WHERE uuid = "{id}"'
        current_time = datetime.datetime.now()
        result = self.__cursor.execute(sql).fetchone()
        if result:
            created_time = datetime.datetime.fromtimestamp(float(result[0]))
            difference = (current_time-created_time).seconds / 60 / 60
            if difference >= self.exp_time:
                self.delete(id)
            else:
                return True
        return False

    def insert(self, id: str, secret: str, password: str) -> None:
        '''Insert new row into table with id, secret, password, current time

        :param id: UUID of secret
        :param secret: text message of secret
        :param password: password for the secret
        :return: None
        '''
        time = datetime.datetime.now().timestamp()
        sql = f'''INSERT INTO SECRETS (
                    uuid, text, password, created_time) VALUES (
                    "{id}", "{secret}", "{password}", "{time}")'''
        self.__cursor.execute(sql)
        self.__conn.commit()

    def select(self, id: str) -> str:
        '''Get text message of secret by id

        :param id: uniq id in the table
        :return: string with text message of secret
        '''
        sql = f'SELECT text FROM SECRETS WHERE uuid = "{id}"'
        result = self.__cursor.execute(sql).fetchone()
        return result[0]

    def delete(self, id: str) -> None:
        '''Delete row with secret from the table by id

        :param id: uniq id in the table
        :return: None
        '''
        sql = f'DELETE FROM SECRETS WHERE uuid = "{id}"'
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
