import sqlite3 as sql
import logging

logger = logging.getLogger(__name__)




class Database:
    def __init__(self, db_path='main.db'):
        self.connection = sql.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self):
        try:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users
            (ID INTEGER, datatime REAL, Callback TEXT, Link TEXT, Ban INTEGER, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS inwork
            (ID INTEGER, datatime REAL, Callback TEXT, Link TEXT, Hour INTEGER, Minute INTEGER, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS outwork
            (ID INTEGER, datatime REAL, Callback TEXT, Link TEXT, Hour INTEGER, Minute INTEGER, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS tasks
            (ID INTEGER, Datatime REAL, Name TEXT, Description TEXT, Photo INTEGER, Callback INTEGER, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS Improve
                (ID INTEGER, Datatime REAL, Callback INTEGER, TextOfUser TEXT, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS Doc
                (ID INTEGER, Datatime REAL, Callback INTEGER, Link TEXT, TextDoc TEXT, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()

            self.cursor.execute("""CREATE TABLE IF NOT EXISTS Admin
                (ID INTEGER, Callback INTEGER, Link TEXT, PRIMARY KEY("ID" AUTOINCREMENT))""")
            self.connection.commit()
            logger.info("Таблицы успешно созданы.")
        except Exception as e:
            logger.exception(f"Ошибка при создании таблиц: {e}")

    def add_admin(self, callback, link):
        self.cursor.execute(
            "INSERT INTO Admin(Callback, Link) VALUES (?, ?)",
            (callback, link)
        )
        self.connection.commit()

    def get_admins(self, callback_asking):
        return self.cursor.execute(
            "SELECT Callback, Link FROM Admin WHERE Callback != ?",
            (callback_asking,)
        ).fetchall()

    def delete_admin(self, callback):
        self.cursor.execute("DELETE FROM Admin WHERE Callback = ?", (callback,))
        self.connection.commit()

    def is_admin(self, callback):
        if self.cursor.execute(
            "SELECT Callback FROM Admin WHERE Callback=?",
            (callback,)
        ).fetchone():
            return True
        return False

    def add_user(self, datatime, callback, link, ban=0):
        self.cursor.execute(
            "INSERT INTO users(Datatime, Callback, Link, Ban) VALUES (?, ?, ?, ?)",
            (datatime, callback, link, ban)
        )
        self.connection.commit()

    def get_user(self, callback):
        return self.cursor.execute(
            "SELECT Callback FROM users WHERE Callback = ?",
            (callback,)
        ).fetchone()

    def get_ban(self, callback):
        result = self.cursor.execute(
            "SELECT Ban FROM users WHERE Callback = ?",
            (callback,)
        ).fetchone()
        return result[0] if result else 0

    def insert_inwork(self, datatime, callback, link, hour, minute):
        self.cursor.execute(
            "INSERT INTO inwork(Datatime, Callback, Link, Hour, Minute) VALUES (?, ?, ?, ?, ?)",
            (datatime, callback, link, hour, minute)
        )
        self.connection.commit()

    def insert_outwork(self, datatime, callback, link, hour, minute):
        self.cursor.execute(
            "INSERT INTO outwork(Datatime, Callback, Link, Hour, Minute) VALUES (?, ?, ?, ?, ?)",
            (datatime, callback, link, hour, minute)
        )
        self.connection.commit()

    def get_user_tasks(self, callback):
        return self.cursor.execute(
            "SELECT ID, Name, Description, Photo FROM tasks WHERE Callback = ?",
            (callback,)
        ).fetchall()

    def insert_task(self, datatime, name, description, photo, callback_user):
        self.cursor.execute(
            "INSERT INTO tasks(Datatime, Name, Description, Photo, Callback) VALUES (?, ?, ?, ?, ?)",
            (datatime, name, description, photo, callback_user)
        )
        self.connection.commit()

    def insert_improve(self, datatime, callback, text_of_user):
        self.cursor.execute(
            f"INSERT INTO Improve(Datatime, Callback, TextOfUser) VALUES (?, ?, ?)",
            (datatime, callback, text_of_user)
        )
        self.connection.commit()

    def insert_doc(self, datatime, callback, text_doc, link):
        self.cursor.execute(
            """INSERT INTO Doc(Datatime, Callback, TextDoc, Link) VALUES (?, ?, ?, ?)""",
            (datatime, callback, text_doc, link)
        )
        self.connection.commit()

    def get_all_docs(self):
        return self.cursor.execute("SELECT ID, Callback, Link, TextDoc FROM Doc").fetchall()

    def get_all_improves(self):
        return self.cursor.execute("SELECT Callback, TextOfUser FROM Improve").fetchall()

    def ban_user(self, callback):
        self.cursor.execute("UPDATE users SET Ban = 1 WHERE Callback = ?", (callback,))
        self.connection.commit()

    def unban_user(self, callback):
        self.cursor.execute("UPDATE users SET Ban = 0 WHERE Callback = ?", (callback,))
        self.connection.commit()

    def get_users_for_unban_keyboard(self):
        return self.cursor.execute("SELECT Callback, Link FROM users WHERE Ban = 1").fetchall()

    def get_active_users(self):
        return self.cursor.execute("SELECT Callback, Link FROM users WHERE Ban = 0").fetchall()

    def get_all_users(self):
        return self.cursor.execute("SELECT Callback FROM users").fetchall()

    def delete_user(self, callback):
        self.cursor.execute("DELETE FROM users WHERE Callback = ?", (callback,))
        self.connection.commit()

    def get_user_by_callback(self, callback):
        return self.cursor.execute("SELECT Callback FROM users WHERE Callback = ? AND Ban = 0", (callback,)).fetchone()

    def get_user_link_by_callback(self, callback):
        return self.cursor.execute("SELECT Link FROM users WHERE Callback = ?", (callback,)).fetchone()

    def delete_task(self, task_id: int):
        """Удалить задачу по ID"""
        self.cursor.execute("DELETE FROM tasks WHERE ID = ?", (task_id,))
        self.connection.commit()

    def delete_all_improves(self):
        """Очистить пожелания"""
        self.cursor.execute("DELETE FROM Improve")
        self.connection.commit()

    def delete_doc(self, doc_id: int):
        """Удалить отчет по ID-отчета"""
        self.cursor.execute("DELETE FROM Doc WHERE ID = ?", (doc_id,))
        self.connection.commit()

db = Database()