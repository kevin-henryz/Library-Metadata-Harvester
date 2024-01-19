# Manages SQLite database interactions

import sqlite3
class DatabaseManager:
    def __init__(self, db_name='book_data.db'):
        self.db_name = db_name
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def create_table(self, table_name, columns):
        """
        Create a table in the database.

        Args:
            table_name (str): The name of the table.
            columns (str): A string containing column definitions.

        Example:
            columns = "id INTEGER PRIMARY KEY, name TEXT, age INTEGER"
            create_table("book_data", columns)
        """
        self.connect()
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.connection.commit()
        self.disconnect()

    def insert_data(self, table_name, data):
        """
        Insert data into the specified table.

        Args:
            table_name (str): The name of the table.
            data (tuple): A tuple containing values to be inserted.

        Example:
            data = (1, 'John Doe', 25)
            insert_data("book_data", data)
        """
        self.connect()
        placeholders = ', '.join(['?' for _ in data])
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", data)
        self.connection.commit()
        self.disconnect()

    def fetch_data(self, table_name, condition=None):
        """
        Fetch data from the specified table.

        Args:
            table_name (str): The name of the table.
            condition (str): A condition to filter the data (optional).

        Returns:
            list: A list of tuples containing the fetched data.
        """
        self.connect()
        if condition:
            query = f"SELECT * FROM {table_name} WHERE {condition}"
        else:
            query = f"SELECT * FROM {table_name}"

        self.cursor.execute(query)
        result = self.cursor.fetchall()
        self.disconnect()
        return result

    def update_data(self, table_name, update_values, condition):
        """
        Update data in the specified table.

        Args:
            table_name (str): The name of the table.
            update_values (str): A string containing column-value pairs to be updated.
            condition (str): A condition to filter the data to be updated.

        Example:
            update_values = "name='Updated Name', age=30"
            condition = "id=1"
            update_data("book_data", update_values, condition)
        """
        self.connect()
        self.cursor.execute(f"UPDATE {table_name} SET {update_values} WHERE {condition}")
        self.connection.commit()
        self.disconnect()

    def delete_data(self, table_name, condition):
        """
        Delete data from the specified table.

        Args:
            table_name (str): The name of the table.
            condition (str): A condition to filter the data to be deleted.

        Example:
            condition = "id=1"
            delete_data("mytable", condition)
        """
        self.connect()
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
        self.connection.commit()
        self.disconnect()


if __name__ == "__main__":
# Example Usage:
    db = DatabaseManager()
    db.create_table("book_data", "Isbn INTEGER PRIMARY KEY, Ocn INTEGER, Lccn TEXT, Doi TEXT")
    db.create_table("lccn_data", "Lccn TEXT PRIMARY KEY, Source TEXT")

    # db.insert_data("book_data", (1, 'John Doe', 25))
    # data = db.fetch_data("book_data")
    # print(data)
    # db.update_data("book_data", "name='Updated Name', age=30", "id=1")
    # db.delete_data("book_data", "id=1")
