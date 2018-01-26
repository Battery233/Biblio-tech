import unittest

import main


class TestDecodeQR(unittest.TestCase):
    def test(self):
        self.assertEqual('HORN O.K. PLEASE.', main.decode_QR('vision/test_files/qr.png'))
        self.assertEqual('changed', main.decode_QR('vision/test_files/qr1.jpg'))
        self.assertEqual('changed', main.decode_QR('vision/test_files/qr2.jpg'))

if __name__ == '__main__':
    unittest.main()
