#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort

Usage:
    photo-sort.py -i <input> ... -o <output> -y <year> -e <event> [-p <photographer>] [--dont-encode]

Options:
    -i --input ...     Folder(s) with photos to process
    -o --output        Where to create new folder
    -y --year          Year the photos were taken
    -e --event         Name of the event
    -p --photographer  Name of person taking the photos
    --dont-encode      Do not encode videos

Example:
    photo-sort.py -i "Boom photos" -o "My Photos" -y 2014 -e Boom -p Marcus

More info:
    Encoding of videos requires HandBrakeCLI to be on the system path
"""

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"

import os
import errno
import shutil
import subprocess
from glob import glob
from docopt import docopt

video_extensions = ['.avi', '.dv', '.mpg', '.mpeg', '.ogm', '.m4v', '.mp4', '.mkv', '.mov', '.qt']
handbrake_preset = 'Normal'

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

def copy_files(arguments, input_files, output_folder):
    file_count = len(input_files)
    index_mask = get_index_mask(file_count)

    for index, key in enumerate(sorted(input_files)):
        input_file = input_files[key]
        output_file_name = get_output_file_name(arguments, index_mask, index, input_file)
        output_file = output_folder + '/' + output_file_name
        shutil.copy2(input_file, output_file)
        print output_file_name

    print 'Copied %d files.' % file_count

def encode_videos(output_folder):
    files = glob(output_folder + '/*.*')

    for input_file in files:
        (base, extension)=os.path.splitext(input_file)

        if extension in video_extensions:
            output_file = base + '.mp4'

            if os.path.exists(output_file):
                shutil.move(input_file, input_file + '_')
                input_file = input_file + '_'
            
            subprocess.call( ["HandBrakeCLI", "--preset", handbrake_preset, "-i" ,input_file, "-o", output_file])
            os.remove(input_file)

def get_input_files(directories):
    input_files = {}

    for directory in directories:
        files = glob(directory + '/' + '*.*')

        for file in files:
            create_time = os.path.getctime(file)

            while create_time in input_files:
                create_time += 1

            input_files[create_time] = file

    return input_files

def process(arguments):
    output_folder = folder_path(arguments)
    mkdir(output_folder)
    print "Output directory:", output_folder

    input_files = get_input_files(arguments['--input'])
    copy_files(arguments, input_files, output_folder)

    if not arguments['--dont-encode']:
        encode_videos(output_folder)

    print "\nAll done!"

def main():
    arguments = docopt(__doc__, version='Photo Sort 1.0.0')
    print arguments

    process(arguments)

if __name__ == '__main__':
    main()