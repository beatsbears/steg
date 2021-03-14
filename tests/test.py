import os
import unittest

from steg import steg_img

class TestSteg(unittest.TestCase):

    def test_full(self):
        s = steg_img.IMG(payload_path='./test_data/payload.txt', image_path='./test_data/pug.png')
        s.hide()
        assert os.path.exists('./new.png')

        s_prime = steg_img.IMG(image_path='./new.png')
        s_prime.extract()
        assert os.path.exists("./hidden_file.txt")
        with open("./hidden_file.txt") as extract:
            with open('./test_data/payload.txt') as orig:
                e = extract.read().strip()
                o = orig.read().strip()
                assert e == o
        os.remove("./hidden_file.txt")
        os.remove('./new.png')


if __name__ == '__main__':
    unittest.main()