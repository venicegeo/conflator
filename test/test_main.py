import os
import unittest
import conflator.main as main


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    def test_main(self):
        """ Run main function """
        cmd = ''
        args = main.parse_args(cmd)
        self.assertTrue(isinstance(args, dict))
