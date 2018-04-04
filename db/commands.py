# this file is designed for generating commands for sql

BOOKS_TABLE_NAME = 'books'
LOGS_TABLE_NAME = 'logs'

TABLE_SCHEMA = '''ISBN INTEGER, title TEXT, author TEXT, position TEXT,
                 status INTEGER, UNIQUE(ISBN) ON CONFLICT REPLACE'''

LOGS_TABLE_SCHEMA = '''position TEXT, ISBN INTEGER, title TEXT'''


def command_create():
    return '''CREATE TABLE %s
                 (%s)''' % (BOOKS_TABLE_NAME, TABLE_SCHEMA)


def command_create_logs_table():
    return '''CREATE TABLE %s
                 (%s)''' % (LOGS_TABLE_NAME, LOGS_TABLE_SCHEMA)

def command_clear_logs():
    return "DELETE FROM %s" % LOGS_TABLE_NAME

def command_add_log(position, ISBN, title):
    return '''INSERT INTO %s VALUES ('%s', %s, '%s')''' % (LOGS_TABLE_NAME, position, ISBN, title)

def command_delete():
    return "DELETE FROM %s" % BOOKS_TABLE_NAME


def command_add_item(ISBN, title, author, position, status):
    return '''INSERT INTO %s VALUES (%s, '%s', '%s', '%s',%s)''' % (BOOKS_TABLE_NAME, ISBN, title, author, position, status)


def command_select_all(table=BOOKS_TABLE_NAME):
    return "SELECT * FROM %s" % table

def command_update_book_position(ISBN, position):
    return "UPDATE %s SET position='%s' WHERE ISBN= %s" % (BOOKS_TABLE_NAME, position, ISBN)


def command_update_book_status(ISBN, status):
    return "UPDATE %s SET status='%s' WHERE ISBN=%s" % (BOOKS_TABLE_NAME, status, ISBN)


def command_get_all_titles_and_positions():
    return "SELECT title, position FROM %s" % BOOKS_TABLE_NAME


def command_get_all_ISBNs():
    return "SELECT ISBN FROM %s" % BOOKS_TABLE_NAME


def command_get_position_by_ISBN(isbn):
    return "SELECT position FROM %s WHERE ISBN=%s" % (BOOKS_TABLE_NAME, isbn)


def command_get_position_by_title(title):
    return "SELECT position FROM %s WHERE title='%s'" % (BOOKS_TABLE_NAME, title)


def command_get_ISBN_by_title(title):
    return "SELECT ISBN FROM %s WHERE title='%s'" % (BOOKS_TABLE_NAME, title)

def command_get_book_status_by_ISBN(isbn):
    return "SELECT status FROM %s WHERE ISBN=%s" % (BOOKS_TABLE_NAME, isbn)
