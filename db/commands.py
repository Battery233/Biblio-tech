# this file is designed for generating commands for sql

TABLE_NAME = 'books'
TABLE_DESIGN = '''ISBN INTEGER, title TEXT, author TEXT, position TEXT,
                 status INTEGER, UNIQUE(ISBN) ON CONFLICT REPLACE'''


def command_create():
    return '''CREATE TABLE %s
                 (%s)''' % (TABLE_NAME, TABLE_DESIGN)


def command_delete():
    return "DELETE FROM %s" % TABLE_NAME


def command_add_item(ISBN, title, author, position, status):
    return '''INSERT INTO %s VALUES (%s, '%s', '%s', '%s',%s)''' % (TABLE_NAME, ISBN, title, author, position, status)


def command_select_all():
    return "SELECT * FROM %s" % TABLE_NAME


def command_update_book_position(ISBN, position):
    return "UPDATE %s SET position='%s' WHERE ISBN= %d" % (TABLE_NAME, position, ISBN)


def command_update_book_status(ISBN, status):
    return "UPDATE %s SET status='%s' WHERE ISBN=%d" % (TABLE_NAME, status, ISBN)


def command_get_all_titles_and_positions():
    return "SELECT title, position FROM %s" % TABLE_NAME


def command_get_all_ISBNs():
    return "SELECT ISBN FROM %s" % TABLE_NAME


def command_get_position_by_ISBN(isbn):
    return "SELECT position FROM %s WHERE ISBN=%d" % (TABLE_NAME, isbn)


def command_get_position_by_title(title):
    return "SELECT position FROM %s WHERE title=%s" % (TABLE_NAME, title)


def command_get_ISBN_by_title(title):
    return "SELECT ISBN FROM %s WHERE title=%s" % (TABLE_NAME, title)

