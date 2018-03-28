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
                 status INTEGER, UNIQUE(ISBN) ON CONFLICT REPLACE)''')
    conn.commit()
    conn.close()


# noinspection PyBroadException
def flush_db(db):
    # Physically remove db file
    try:
        os.remove(db)
    except:
        print("Exception in flush_db: failed to remove db")


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

    # Insert library data
    c.execute(
        "INSERT INTO books VALUES (9781785782343, 'Big Data How the Information Revolution Is Transforming Our Lives',"
        " 'Brian Clegg', '2'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9781447221098, 'Dirk Gently Holistic Detective Agency', 'Douglas Adams', '2',"
        + STATUS_AVAILABLE + ")")
    c.execute("INSERT INTO books VALUES (9780241197806, 'The Castle', 'Franz Kafka', '1'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9781840226881, 'Wealth of Nations', 'Adam Smith', '0'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9780349140438, 'Steve Jobs', 'Walter Isaacson', '3'," + STATUS_AVAILABLE + ")")
    c.execute(
        "INSERT INTO books VALUES (9780140441185, 'Thus Spoke Zarathustra', 'Friedrich Nietzsche', '2'," +
        STATUS_UNAVAILABLE + ")")

    conn.commit()
    conn.close()


def add_book(db, ISBN_all_type, title_all_type, author_all_type, position_all_type, status_all_type):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    ISBN = str(ISBN_all_type)
    title = str(title_all_type)
    author = str(author_all_type)
    position = str(position_all_type)
    status = str(status_all_type)
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

    books = c.fetchall()

    conn.close()

    return books


def get_all_ISBNs(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    c.execute('SELECT ISBN FROM books')

    ISBNs = c.fetchall()

    conn.close()

    return ISBNs


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
