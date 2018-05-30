import unittest
from termgraph import findMinMax

class TestFindMinMax(unittest.TestCase):
    # Test 'min'/'max' argument
    def test_data(self):
        # Test min/max when values >= 0
        data = [ [0, -0], [5, 20/6], [1000000, 0.5], [20.0, 2/5] ]
        self.assertEquals(findMinMax(data,'min'), 0)
        self.assertEquals(findMinMax(data,'max'), 1000000)
        # Test min/max when values <= 0
        data = [ [0, -0], [-10, -1000000], [-0.5, -2/5], [-5, -20/6] ]
        self.assertEquals(findMinMax(data,'min'), -1000000)
        self.assertEquals(findMinMax(data,'max'), 0)
        # Test min/max for both positive and negative values
        data = [ [0, -0], [-4000, -1000000], [-0.5, 1000000], [20.0, 2/5] ]
        self.assertEquals(findMinMax(data,'min'), -1000000)
        self.assertEquals(findMinMax(data,'max'), 1000000)

    # Test 'find' argument errors
    def test_find(self):
        # Make sure value errors are raised when necessary
        data = [ [0, -0], [5, 20/6], [1000000, 0.5], [20.0, 2/5] ]
        with self.assertRaises(SystemExit) as cm:
            findMinMax(data, 'whatever')
        self.assertEquals(cm.exception.code, 1)
