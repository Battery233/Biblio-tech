import sqlite3
import os

# test for travis-ci

PRODUCTION_DB = 'production.db'
TEST_DB = 'test.db'

STATUS_UNAVAILABLE = '0'
STATUS_AVAILABLE = '1'


def create_book_table(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE books
                 (ISBN INTEGER, title TEXT, author TEXT, position TEXT,
                 status INTEGER, UNIQUE(position) ON CONFLICT REPLACE)''')
    conn.commit()
    conn.close()


def flush_db(db):
    # Physically remove db file
    try:
        os.remove(db)
    except:
        pass


def clear_books(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Delete all table entries
    c.execute("DELETE FROM books")

    conn.commit()
    conn.close()


def add_sample_books(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Insert sample data
    c.execute(
        "INSERT INTO books VALUES (9781785782343, 'Big Data How the Information Revolution Is Transforming Our Lives', 'Brian Clegg', '1:1'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9781447221098, 'Dirk Gently Holistic Detective Agency', 'Douglas Adams', '1:2',"
        + STATUS_AVAILABLE + ")")
    c.execute("INSERT INTO books VALUES (9780241197806, 'The Castle', 'Franz Kafka', '1:3'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9781840226881, 'Wealth of Nations', 'Adam Smith', '2:1'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9780349140438, 'Steve Jobs', 'Walter Isaacson', '2:2'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9780140441185, 'Thus Spoke Zarathustra', 'Friedrich Nietzsche', '2:3'," +
        STATUS_UNAVAILABLE + ")")

    conn.commit()
    conn.close()


def add_book(db, ISBN, title, author, position, status):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("INSERT INTO books VALUES (" +
              ISBN + ", '" + title + "', '" + author + "', '" + position + "', " + status + ")")

    conn.commit()
    conn.close()


def get_books(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Get all books
    c.execute("SELECT * FROM books")
    books = c.fetchall()
    print("[DBS] running get_books in db.main")
    conn.close()

    return books


def update_book_position(db, ISBN, position):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("UPDATE books SET position='" + position + "' WHERE ISBN=" + ISBN)

    conn.commit()
    conn.close()


def update_book_status(db, ISBN, status):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute("UPDATE books SET status='" + status + "' WHERE ISBN=" + ISBN)

    conn.commit()
    conn.close()


def get_position_by_ISBN(db, ISBN):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    values = (ISBN,)
    c.execute('SELECT position FROM books WHERE ISBN=?', values)

    row = c.fetchone()

    conn.close()

    if row is not None:
        return row[0]

    return None


# TODO: refactor this and extract querying bit into a method with parameterized values
def get_position_by_title(db, title):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    values = (title,)
    c.execute('SELECT position FROM books WHERE title=?', values)

    row = c.fetchone()

    conn.close()

    if row is not None:
        return row[0]

    return None


def get_all_titles_and_positions(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('SELECT title, position FROM books')

    books = c.fetchall();

    conn.close()

    return books


def get_ISBN_by_title(db, title):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    values = (title,)
    c.execute('SELECT ISBN FROM books WHERE title=?', values)

    row = c.fetchone()

    conn.close()

    if row is not None:
        return row[0]

    return None
