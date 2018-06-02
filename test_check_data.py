import unittest
from termgraph import check_data, init

class TestCheckData(unittest.TestCase):

    # Test that there are data for all labels
    def test_labels_and_data(self):
        args = init()

        data = [[20.5, 30.5], [0, 60.0], [10, 100], [70, 80]]
        len_categories = 2

        # Labels size = data size
        labels = ['2007', '2008', '2009', '2010']
        self.assertEqual([], check_data(labels, data, len_categories, args))

        # Labels size > data size
        labels = ['2007', '2008', '2009', '2010', '2011']
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

        # Labels size < data size
        labels = ['2007', '2008', '2009']
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

    # Test that colors inserted by user are as many as the categories
    def test_colors_and_categories(self):
        args = init()

        labels = ['2007', '2008', '2009', '2010']
        data = [[20.5, 30.5], [0, 60.0], [10, 100], [70, 80]]
        len_categories = 2

        # No colors inserted by user
        self.assertEqual([], check_data(labels, data, len_categories, args))

        # Colors size = Categories sizes
        args['color'] = ['blue', 'magenta']
        self.assertEqual([94, 95], check_data(labels, data, len_categories, args))

        # Colors size < Categories sizes
        args['color'] = ['blue']
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

        # Colors size > Categories sizes
        args['color'] = ['blue', 'magenta', 'yellow']
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

    # Test that there are data for all categories per label
    def test_missing_values(self):
        args = init()

        labels = ['2007', '2008', '2009', '2010']
        len_categories = 2

        # No missing values
        data = [[20.5, 30.5], [0, 60.0], [10, 100], [70, 80]]
        self.assertEqual([], check_data(labels, data, len_categories, args))

        # Missing values
        data = [[20.5], [0], [10, 100], [70, 80]]
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

    # Test that multiple series vertical graph is not same scale
    # (Vertical graph for multiple series of same scale is not supported yet)
    def test_vertical_and_scale(self):
        args = init()

        labels = ['2007', '2008', '2009', '2010']
        len_categories = 2
        data = [[20.5, 30.5], [0, 60.0], [10, 100], [70, 80]]

        # Same scale
        args['vertical'] = True
        with self.assertRaises(SystemExit) as cm:
            check_data(labels, data, len_categories, args)
        self.assertEqual(cm.exception.code, 1)

        # Different scale
        args['vertical'] = True
        args['different_scale'] = True
        self.assertEqual([], check_data(labels, data, len_categories, args))

    # Test that the first n colors from the dict are returned, in case user has
    # chosen --stacked but no colors (n = number of categories)
    def test_colors(self):
        args = init()

        labels = ['2007', '2008', '2009', '2010']
        len_categories = 2
        data = [[20.5, 30.5], [0, 60.0], [10, 100], [70, 80]]
        args['stacked'] = True

        # User has not chosen colors
        self.assertEqual([91,94], check_data(labels, data, len_categories, args))

        # User has chosen colors
        args['color'] = ['blue', 'magenta']
        self.assertEqual([94,95], check_data(labels, data, len_categories, args))
