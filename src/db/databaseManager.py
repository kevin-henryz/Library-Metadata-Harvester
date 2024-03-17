import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name='metadata.sqlite'):
        directory = os.path.dirname(os.path.abspath(__file__))
        self.db_name = os.path.join(directory, db_name)

    def execute_query(self, query, params=(), fetch=False):
        """General purpose method to execute database queries."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(query, params)
                if fetch:
                    return cursor.fetchall()
                conn.commit()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
            except Exception as e:
                print(f"Exception in query execution: {e}")

    def create_table(self, table_name, columns):
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})"
        self.execute_query(query)

    def insert_data(self, table_name, data):
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        self.execute_query(query, data)

    def fetch_data(self, table_name, condition=''):
        query = f"SELECT * FROM {table_name} {condition}"
        return self.execute_query(query, fetch=True)

    def update_data(self, table_name, update_values, condition):
        query = f"UPDATE {table_name} SET {update_values} WHERE {condition}"
        self.execute_query(query)

    def delete_data(self, table_name, condition):
        query = f"DELETE FROM {table_name} WHERE {condition}"
        self.execute_query(query)

    def data_exists(self, table_name, condition):
        """Check if data exists in the table matching the condition."""
        result = self.fetch_data(table_name, f"WHERE {condition}")
        return result is not None and len(result) > 0

# Example Usage
if __name__ == "__main__":
    db = DatabaseManager()
    db.create_table("book_data", "Isbn INTEGER PRIMARY KEY, Ocn INTEGER, Lccn TEXT, Source TEXT, Doi TEXT")

    # Insert data
    isbn_to_insert = 123456789
    data_to_insert = (isbn_to_insert, 123, 'lccn123', 'source123', 'doi123')
    db.insert_data("book_data", data_to_insert)

    # Check if data was inserted
    if db.data_exists("book_data", f"Isbn = {isbn_to_insert}"):
        print("Insertion successful: Data exists")
    else:
        print("Insertion failed: Data does not exist")

    # Delete the inserted data
    db.delete_data("book_data", f"Isbn = {isbn_to_insert}")

    # Check if data was deleted
    if db.data_exists("book_data", f"Isbn = {isbn_to_insert}"):
        print("Deletion failed: Data still exists")
    else:
        print("Deletion successful: Data does not exist")
