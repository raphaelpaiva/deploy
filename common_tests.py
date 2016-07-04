import unittest
from mock import MagicMock
from mock import patch
from StringIO import StringIO

import common

@patch("sys.stdout", new_callable=StringIO)
class CommonTests(unittest.TestCase):
    def test_initialize_controller(self, mock_stdout):
        args = MagicMock()
        args.controller = "host:port"
        args.auth = "user:passw"

        value = common.initialize_controller(args)

        self.assertIsNone(value)
        self.assertEquals(mock_stdout.getvalue(), "Failed to parse: host:port\n")

if __name__ == "__main__":
    unittest.main()
