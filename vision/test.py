import unittest

import main


class TestDecodeQR(unittest.TestCase):
    def test(self):
        text, com = main.decode_QR('vision/test_files/easy_qr.png')
        self.assertEqual('123456789abcd', text)
        self.assertEqual((150,160), com)

        text, _ = main.decode_QR('vision/test_files/distorted_qr.png')
        self.assertEqual('HORN O.K. PLEASE.', text)

        text, _ = main.decode_QR('vision/test_files/stained_qr.png')
        self.assertEqual('123456789abcd', text)

        text, _ = main.decode_QR('vision/test_files/camera_qr1.jpg')
        self.assertEqual('changed', text)

        text, _ = main.decode_QR('vision/test_files/camera_qr2.jpg')
        self.assertEqual('changed', text)

        text, com = main.decode_QR('vision/test_files/not_qr.png')
        self.assertIsNone(text)
        self.assertIsNone(com)


if __name__ == '__main__':
    unittest.main()
