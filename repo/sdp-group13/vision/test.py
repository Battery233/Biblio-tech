import unittest

import main


class TestDecodeQR(unittest.TestCase):
    def test(self):
        text, offset = main.decode_QR('vision/test_files/easy_qr.png')
        # 210: side in pixels
        # 150: x coordinate of center of mass of QR
        # 320: horizontal halfpoint for camera
        expected_offset = int((float(main.ACTUAL_QR_SIDE) / 210) * (150 - 320))
        self.assertEqual('123456789abcd', text)
        self.assertEqual(expected_offset, offset)

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
