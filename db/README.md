# README
Database interface

Run tests:
`python test.py`

Change json format: `jsonBuilder.py`

Create sample test.db in db folder:
`sampleDBgenerator.py`

Database structure:

    TABLE books

    ISBN INTEGER

    title TEXT

    author TEXT

    position TEXT (UNIQUE(position) ON CONFLICT REPLACE)

    status INTEGER
    