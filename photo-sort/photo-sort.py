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

import os
from docopt import docopt

def folder_name(arguments, serial=None):
    output_folder_name = '%s - %s' % (arguments['<year>'], arguments['<event>'])
    if serial:
        output_folder_name += ' - ' + str(serial)
    if arguments['<photographer>']:
        output_folder_name += ' - ' + arguments['<photographer>']

    return output_folder_name

def folder(arguments):
    output_folder_name = folder_name(arguments)
    output_folder = os.path.abspath(arguments['<output>']) + '/' + output_folder_name

    serial = 1
    while (os.path.isdir(output_folder)):
        serial += 1
        output_folder_name = folder_name(arguments, serial)
        output_folder = os.path.abspath(arguments['<output>']) + '/' + output_folder_name

    return output_folder

def process(arguments):
    output_folder = folder(arguments)

    print output_folder

def main():
    arguments = docopt(__doc__, version='Photo Sort 0.1')

    process(arguments)

if __name__ == '__main__':
    main()