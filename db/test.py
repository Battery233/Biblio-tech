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

    def testUpdatePosition(self):
        main.add_book(db, '9780241197806', 'The Castle', 'Franz Kafka', '1:3', main.STATUS_AVAILABLE)
        main.update_book_position(db, '9780241197806', '1:5')

        books = main.get_books(db)

        self.assertEqual((9780241197806, u'The Castle', u'Franz Kafka', u'1:5', int(main.STATUS_AVAILABLE)),
            books[0])

    def testUpdateStatus(self):
        main.add_book(db, '9780241197806', 'The Castle', 'Franz Kafka', '1:3', main.STATUS_AVAILABLE)
        main.update_book_status(db, '9780241197806', main.STATUS_UNAVAILABLE)

        books = main.get_books(db)

        self.assertEqual((9780241197806, u'The Castle', u'Franz Kafka', u'1:3', int(main.STATUS_UNAVAILABLE)),
            books[0])

    def testAddSamePosition(self):
        main.add_book(db, '9780241197806', 'The Castle', 'Franz Kafka', '1:3', main.STATUS_AVAILABLE)
        main.add_book(db, '9781840226881', 'Wealth of Nations', 'Adam Smith', '1:3', main.STATUS_AVAILABLE)

        previous_ISBN = '9780241197806'
        current_ISBN = '9781840226881'

        self.assertIsNone(main.get_position_by_ISBN(db, previous_ISBN))
        self.assertEqual(main.get_position_by_ISBN(db, current_ISBN), '1:3')


if __name__ == '__main__':
    unittest.main()
