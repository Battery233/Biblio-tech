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
