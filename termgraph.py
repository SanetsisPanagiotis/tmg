#!/usr/bin/env python
# coding=utf-8

# termgraph.py - draw basic graphs on terminal
# https://github.com/mkaz/termgraph

# Marcus Kazmierczak
# http://mkaz.com/

from __future__ import print_function
from colorama import init
from itertools import *

import argparse
import sys

init()

# ANSI escape SGR Parameters color codes
available_colors = {
    'red': 91,
    'blue': 94,
    'green': 92,
    'magenta': 95,
    'yellow': 93,
    'black': 90,
    'cyan': 96
}

# TODO: change TICK character
TICK = '▇'
SM_TICK = '▏'

try:
    range = xrange
except NameError:
    pass

# Returns the min/max value of a list of lists (i.e. list=[ [], [], ..., [] ]).
def findMinMax(data, find):
    if find == 'min':
        dat = min(data[0])
        for i in range(1, len(data)):
            if min(data[i]) < dat:
                dat = min(data[i])
    elif find == 'max':
        dat = max(data[0])
        for i in range(1, len(data)):
            if max(data[i]) > dat:
                dat = max(data[i])
    else:
        print(">> Error: 'find' variable should only be 'min' or 'max'")
        sys.exit(1)
    return dat

# Normalizes data and returns them.
def normalize(data, width):
    min_dat = findMinMax(data, 'min')
    # We offset by the mininum if there's a negative.
    off_data = []
    if min_dat < 0:
        min_dat = abs(min_dat)
        for dat in data:
            off_data.append([_d + min_dat for _d in dat])
    else:
        off_data = data
    min_dat = findMinMax(off_data, 'min')
    max_dat = findMinMax(off_data, 'max')

    if max_dat < width:
        # Don't need to normalize if the max value
        # is less than the width we allow.
        return off_data

    norm_factor = width / float(max_dat - min_dat)
    normal_dat = []
    for dat in off_data:
        normal_dat.append([(_v - min_dat) * norm_factor for _v in dat])
    return normal_dat

# Prepares the horizontal graph.
# Each row is printed through print_row function.
def horiontal_rows(labels, data, normal_dat, args, colors):
    val_min = findMinMax(data, 'min')
    for i in range(len(labels)):
        if args['ignore_labels']:
            # Hide the labels.
            label = ''
        else:
            label = "{}: ".format(labels[i])

        values = data[i]
        num_blocks = normal_dat[i]
        for j in range(len(values)):
            # In Multiple series chart 1st category has label at the beginning,
            # whereas the rest categories have only spaces.
            if j > 0:
                len_label = len(label)
                label = ' ' * len_label
            tail = ' {}{}'.format(args['format'].format(values[j]), args['suffix'])
            if colors:
                color = colors[j]
            else:
                color = None
            if not args['vertical']:
                print(label, end="")
            yield (values[j], int(num_blocks[j]), val_min, color)
            if not args['vertical']:
                print(tail)


# Prints a row of the horizontal graph.
def print_row(value, num_blocks, val_min, color):
    """A method to print a row for a horizontal graphs.

    i.e:
    1: ▇▇ 2
    2: ▇▇▇ 3
    3: ▇▇▇▇ 4
    """
    if color:
        sys.stdout.write(f'\033[{color}m') # Start to write colorized.
    if num_blocks < 1 and (value > val_min or value > 0):
        # Print something if it's not the smallest
        # and the normal value is less than one.
        sys.stdout.write(SM_TICK)
    else:
        for i in range(num_blocks):
            sys.stdout.write(TICK)
    sys.stdout.write('\033[0m') # Back to original.

# Prepares the horizontal Stacked graph.
# Each row is printed through print_row function.
def stacked_graph(labels, data, normal_data, len_categories, args, colors):
    val_min = findMinMax(data, 'min')
    # If user hasn't inserted colors, pick the first n colors
    # from the dict (n = number of categories).
    if not colors:
        colors = [v for v in list(available_colors.values())[:len_categories]]
    for i in range(len(labels)):
        if args['ignore_labels']:
            # Hide the labels.
            label = ''
        else:
            label = "{}: ".format(labels[i])
        print(label, end="")
        values = data[i]
        num_blocks = normal_data[i]
        for j in range(len(values)):
            print_row(values[j], int(num_blocks[j]), val_min, colors[j])
        tail = ' {}{}'.format(args['format'].format(sum(values)), args['suffix'])
        print(tail)

vertical_list, zipped_list, value_list, maxi = [], [], [], 0

def vertically(value, num_blocks, val_min, color):
    global maxi, value_list

    value_list.append(str(value))

    if maxi < num_blocks:
        maxi = num_blocks

    if num_blocks > 0:
        vertical_list.append((TICK * num_blocks))
    else:
        vertical_list.append(SM_TICK)

    for row in zip_longest(*vertical_list, fillvalue='  '):
        zipped_list.append(row)

    counter,result_list = 0, []

    for i in reversed(zipped_list):
        result_list.append(i)
        counter+=1

        if maxi == args['width']:
            if counter==(args['width']):
                break
        else:
            if counter == maxi:
                break
    return result_list


def print_vertical(vertical_rows, labels, color):
    if color:
        sys.stdout.write(f'\033[{color}m') # Start to write colorized.

    for j in vertical_rows:
        print(*j)
    sys.stdout.write('\033[0m')

    print("-" * len(j) + "Values" + "-" * len(j))

    for l in zip_longest(*value_list, fillvalue=' '):
        print("  ".join(l))
    print("-" * len(j) + "Labels" + "-" * len(j))

    for k in zip_longest(*labels,fillvalue=''):
        print("  ".join(k))


# Handles the normalization of data and the print of the graph.
def chart(len_categories, colors, data, args, labels):
    if len_categories > 1:
        # Stacked graph chart
        if args['stacked']:
            normal_dat = normalize(data, args['width'])
            stacked_graph(labels, data, normal_dat, len_categories, args, colors)
        else:
            if not colors:
                colors = [None] * len_categories
            # Multiple series chart with different scales
            # Normalization per category
            if args['different_scale']:
                for i in range(len_categories):
                    category_data = []
                    for dat in data:
                        category_data.append([dat[i]])
                    # Normalize data, handle negatives.
                    normal_category_data = normalize(category_data, args['width'])
                    # Generate data for a row.
                    for row in horiontal_rows(labels, category_data, normal_category_data, args, [colors[i]]):
                        # Print the row
                        if not args['vertical']:
                            print_row(*row)
                        else:
                            vertic = vertically(*row)
                    # Vertical graph chart
                    if args['vertical']:
                        print_vertical(vertic, labels, colors[i])
                    print()
    # One category/Multiple series chart with same scale
    # All-together normalization
    if len_categories == 1 or not args['different_scale']:
        if not args['stacked']:
            normal_dat = normalize(data, args['width'])
            for row in horiontal_rows(labels, data, normal_dat, args, colors):
                if not args['vertical']:
                    print_row(*row)
                else:
                    vertic = vertically(*row)
            if args['vertical'] and len_categories == 1:
                print_vertical(vertic, labels, colors[0])
            print()


# Main function
def main(args):
    # determine type of graph
    # read data
    categories, labels, data, colors = read_data(args['filename'])
    # Find the number of categories from the first data row
    # (user may have not inserted categories' names).
    len_categories = len(data[0])

    chart(len_categories, colors, data, args, labels)

# Parses and returns arguments.
def init():
    parser = argparse.ArgumentParser(description='draw basic graphs on terminal')
    parser.add_argument('filename', nargs='?', default="-",
                        help='data file name (comma or space separated). Defaults to stdin.')
    parser.add_argument('--width', type=int, default=50,
                        help='width of graph in characters default:50')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--format', default='{:<5.2f}',
                        help='format specifier to use.')
    parser.add_argument('--suffix', default='',
                        help='string to add as a suffix to all data points.')
    parser.add_argument('--ignore_labels', action='store_true',
                        help='Do not print the label column')
    parser.add_argument('--color', nargs='*', choices=available_colors,
                        help='Graph bar color(s)')
    parser.add_argument('--vertical', action= 'store_true', help='Vertical graph chart')
    parser.add_argument('--stacked', action='store_true',
                        help='Stacked bar graph')
    parser.add_argument('--different_scale', action='store_true',
                        help='Categories have different scales.')
    args = vars(parser.parse_args())
    return args

# Checks that all data were inserted correctly and returns colors.
def check_data(labels, data, len_categories, color):
    # Check that there are data for all labels.
    if len(labels) != len(data):
        print(">> Error: Label and data array sizes don't match")
        sys.exit(1)
    # Check that there are data for all categories per label.
    for dat in data:
        if len(dat) != len_categories:
            print(">> Error: There are missing values")
            sys.exit(1)
    colors = []
    # If user inserts colors, they should be as many as the categories.
    if color is not None:
        if len(color) != len_categories:
            print(">> Error: Color and category array sizes don't match")
            sys.exit(1)
        for c in color:
            colors.append(available_colors.get(c))
    # Vertical graph chart for multiple series of same scale is not supported yet.
    if args['vertical'] and len_categories > 1 and not args['different_scale']:
        print(">> Error: Vertical graph chart for multiple series of same scale is not supported yet.")
        sys.exit(1)
    return colors

# Prints a tick and the category's name for each category above the graph.
def print_categories(categories, colors):
    for i in range(len(categories)):
        if colors:
            sys.stdout.write(f'\033[{colors[i]}m') # Start to write colorized.
        sys.stdout.write(TICK + ' ' + categories[i] + '  ')
        sys.stdout.write('\033[0m') # Back to original.
    print('\n\n')

# Reads data from a file or stdin and returns them.
def read_data(filename):
    '''
    Filename includes categories, labels and data.
    We append categories and labels to lists.
    Data are inserted to a list of lists due to the categories.

    i.e.
    labels = ['2001', '2002', '2003', ...]
    categories = ['boys', 'girls']
    data = [ [20.4, 40.5], [30.7, 100.0], ...]
    '''
    # TODO: add verbose flag
    stdin = filename == '-'

    reading_from = f'Reading data from {("stdin" if stdin else filename)}'
    hyphen_num = len(reading_from)

    print('\n'+hyphen_num*'-'+'\n'+reading_from+'\n'+hyphen_num*'-'+'\n')

    categories, labels, data, colors = ([] for i in range(4))

    f = sys.stdin if stdin else open(filename, "r")
    for line in f:
        line = line.strip()
        if line:
            if not line.startswith('#'):
                if line.find(",") > 0:
                    cols = line.split(',')
                else:
                    cols = line.split()
                # Line contains categories
                if line.startswith('@'):
                    cols[0] = cols[0].replace("@ ", "")
                    categories = cols
                # Line contains label and values
                else:
                    labels.append(cols[0].strip())
                    data_points = []
                    for i in range(1, len(cols)):
                        data_points.append(float(cols[i].strip()))
                    data.append(data_points)
    f.close()
    len_categories = len(data[0])
    colors = check_data(labels, data, len_categories, args['color'])
    if categories:
        print_categories(categories, colors)

    return categories, labels, data, colors


if __name__ == "__main__":
    args = init()
    main(args)
