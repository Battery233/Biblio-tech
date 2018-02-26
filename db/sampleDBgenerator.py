from db import main

db = main.TEST_DB

main.flush_db(db)
main.create_book_table(db)
main.add_sample_books(db)
