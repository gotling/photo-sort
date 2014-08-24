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
import errno
import shutil
from glob import glob
from docopt import docopt

def folder_name(arguments, serial=None):
    output_folder_name = '%s - %s' % (arguments['<year>'], arguments['<event>'])
    if serial:
        output_folder_name += ' - ' + str(serial)
    if arguments['<photographer>']:
        output_folder_name += ' - ' + arguments['<photographer>']

    return output_folder_name

def folder_path(arguments):
    output_folder_name = folder_name(arguments)
    output_folder = os.path.abspath(arguments['<output>']) + '/' + output_folder_name

    serial = 1
    while (os.path.isdir(output_folder)):
        serial += 1
        output_folder_name = folder_name(arguments, serial)
        output_folder = os.path.abspath(arguments['<output>']) + '/' + output_folder_name

    return output_folder

def mkdir(output_folder):
    try:
        os.makedirs(output_folder)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def get_index_mask(file_count):
    if file_count < 10:
        return '%d'
    elif file_count < 100:
        return '%02d'
    elif file_count < 1000:
        return '%03d'
    else:
        return '%04d' 

def get_output_file_name(arguments, index_mask, index, input_file):
    file_name_format = index_mask + ' - %s %s'
    output_file_name = file_name_format % (index + 1, arguments['<event>'], arguments['<year>'])
    if arguments['<photographer>']:
        output_file_name += ' - ' + arguments['<photographer>']
    extension = os.path.splitext(input_file)[1]
    output_file_name += extension.lower()

    return output_file_name

def copy_files(arguments, output_folder):
    files = glob(arguments['<input>'] + '/' + '*.*')
    file_count = len(files)
    index_mask = get_index_mask(file_count)

    for index, input_file in enumerate(files):
        output_file_name = get_output_file_name(arguments, index_mask, index, input_file)
        output_file = output_folder + '/' + output_file_name
        shutil.copy2(input_file, output_file)
        print output_file_name

    print 'Copied %d files' % file_count

def process(arguments):
    output_folder = folder_path(arguments)
    print "Output directory:", output_folder
    mkdir(output_folder)
    copy_files(arguments, output_folder)

def main():
    arguments = docopt(__doc__, version='Photo Sort 0.1')

    process(arguments)

if __name__ == '__main__':
    main()