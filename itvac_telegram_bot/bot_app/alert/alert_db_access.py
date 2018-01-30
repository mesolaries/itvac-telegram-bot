"""
This module provides access to Django database (db.sqlite3) when send_alert.py module called.

"""

import sqlite3


class UserModel:
    def __init__(self, dbname="db.sqlite3"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        stmt = "CREATE TABLE IF NOT EXISTS bot_app_alert (chat_id integer UNIQUE)"
        self.conn.execute(stmt)
        self.conn.commit()

    def add_item(self, item_text):
        stmt = "INSERT INTO bot_app_alert (chat_id) VALUES (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text):
        stmt = "DELETE FROM bot_app_alert WHERE chat_id = (?)"
        args = (item_text, )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self):
        stmt = "SELECT chat_id FROM bot_app_alert"
        return [x[0] for x in self.conn.execute(stmt)]