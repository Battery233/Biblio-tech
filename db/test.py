import unittest

import main

db = main.TEST_DB

class TestDB(unittest.TestCase):
    def setUp(self):
        main.flush_db(db)
        main.create_book_table(db)


    def testAddSampleBooks(self):
        main.add_sample_books(db)
        self.assertEqual(6, len(main.get_books(db)))
        main.clear_books(db)

    def testAddBook(self):
        main.add_book(db, '9780241197806', 'The Castle', 'Franz Kafka', '1:3', main.STATUS_AVAILABLE)

        books = main.get_books(db)

        self.assertEqual(1, len(books))
        self.assertEqual(
            (9780241197806, u'The Castle', u'Franz Kafka', u'1:3', int(main.STATUS_AVAILABLE)),
            books[0])

if __name__ == '__main__':
    unittest.main()
