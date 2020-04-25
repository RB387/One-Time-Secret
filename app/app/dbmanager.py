import sqlite3


class DataBaseManager:
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(path)
        self.cursor = self.conn.cursor()

    def does_exist(self, id: str) -> bool:
        sql = f'SELECT EXISTS(SELECT 1 FROM SECRETS WHERE uuid = "{id}")'
        result = self.cursor.execute(sql).fetchone()
        return bool(result[0])

    def insert(self, id: str, secret: str, password: str) -> None:
        sql = f'INSERT INTO SECRETS (uuid, text, password) VALUES ("{id}", "{secret}", "{password}")'
        self.cursor.execute(sql)
        self.conn.commit()

    def select(self, id: str) -> str:
        sql = f'SELECT text FROM SECRETS WHERE uuid = "{id}"'
        result = self.cursor.execute(sql).fetchone()
        return result[0]

    def delete(self, id: str) -> None:
        sql = f'DELETE FROM SECRETS WHERE uuid = "{id}"'
        self.cursor.execute(sql)
        self.conn.commit()
