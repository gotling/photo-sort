#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort

Usage:
    photo-sort.py -i <input> -o <output> -y <year> -e <event> [-p <photographer>]

Options:
    -i --input         Folder with photos to process
    -o --output        Where to create new folder
    -y --year          Year the photos were taken
    -e --event         Name of the event
    -p --photographer  Name of person taking the photos

Exapmle:
    photo-sort.py -i DCIM100 -o "My Photos" -y 2014 -e Boom -p Marcus
"""

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"

from docopt import docopt

def process(arguments):
    print "Input valid"

def main():
    arguments = docopt(__doc__, version='Photo Sort 0.1')

    process(arguments)

if __name__ == '__main__':
    main()