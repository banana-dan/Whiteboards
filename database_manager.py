import sqlite3


class NoteDataBaseOpenHelper:
    def __init__(self):
        # создаем коннект
        self.conn = sqlite3.connect("notes.db")
        # создаем курсор
        cursor = self.conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS notes(
        id INT
        )
        
        """)
    def add_element(self):
        pass

    def get_element_by_id(self):
        pass

    def get_id_by_path(self):
        pass

    def delete_element_by_id(self):
        pass
