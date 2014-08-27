#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort

Usage:
    photo-sort.py -i <input> ... -o <output> -y <year> -e <event> [-p <photographer>] [options]

Options:
    -i --input ...     Folder(s) with photos to process
    -o --output        Where to create new folder
    -y --year          Year the photos were taken
    -e --event         Name of the event
    -p --photographer  Name of person taking the photos
    --skip-encode      Do not encode videos
    --dry-run          Make no changes

Example:
    photo-sort.py -i "Canon" -i "Samsung" -o "My Photos" -y 2014 -e Boom -p Marcus

More info:
    Encoding of videos requires HandBrakeCLI to be on the system path
"""

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"

import os
import re
import time
import errno
import shutil
import timeit
import calendar
import subprocess
from glob import glob
from datetime import datetime

import exifread
from docopt import docopt
import exiftool

video_extensions = ['.avi', '.dv', '.mpg', '.mpeg', '.ogm', '.m4v', '.mp4', '.mkv', '.mov', '.qt']
handbrake_preset = 'Normal'
dry_run = False

def folder_name(year, event, photographer, serial=None):
    output_folder_name = '%s - %s' % (year, event)
    
    if serial:
        output_folder_name += ' - ' + str(serial)
    
    if photographer:
        output_folder_name += ' - ' + photographer

    return output_folder_name

def folder_path(output, year, event, photographer):
    output_folder_name = folder_name(year, event, photographer)
    output_folder = os.path.abspath(output) + '/' + output_folder_name

    serial = 1

    while (os.path.isdir(output_folder)):
        serial += 1
        output_folder_name = folder_name(year, event, photographer, serial)
        output_folder = os.path.abspath(output) + '/' + output_folder_name

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
    else:
        return '%0' + str(len(str(file_count))) + 'd'

def get_output_file_name(year, event, photographer, index_mask, index, input_file):
    file_name_format = index_mask + ' - %s %s'
    output_file_name = file_name_format % (index + 1, event, year)
    
    if photographer:
        output_file_name += ' - ' + photographer

    extension = os.path.splitext(input_file)[1]
    output_file_name += extension.lower()

    return output_file_name

def copy_files(year, event, photographer, input_files, output_folder):
    file_count = len(input_files)
    index_mask = get_index_mask(file_count)

    for index, key in enumerate(sorted(input_files)):
        input_file = input_files[key]
        output_file_name = get_output_file_name(year, event, photographer, index_mask, index, input_file)
        output_file = output_folder + '/' + output_file_name

        if not dry_run:
            shutil.copy2(input_file, output_file)

        print output_file_name

    print 'Copied %d files.' % file_count

def get_video_rotation(et, file):
    """Return value HandBrake uses for rotation"""
    
    rotation = et.get_tag('Rotation', file)

    if rotation == 90:
        return 4
    elif rotation == 180:
        return 3
    elif rotation == 270:
        return 7
    else:
        return None

def encode_videos(output_folder):
    """Encode videos using HandBrakeCLI"""
    files = glob(output_folder + '/*.*')

    with exiftool.ExifTool() as et:
        for input_file in files:
            (base, extension)=os.path.splitext(input_file)

            if extension in video_extensions:
                output_file = base + '.mp4'

                if os.path.exists(output_file):
                    shutil.move(input_file, input_file + '_')
                    input_file = input_file + '_'

                command = ["HandBrakeCLI", "--preset", handbrake_preset, "-i" ,input_file, "-o", output_file]

                rotation = get_video_rotation(et, input_file)
                if rotation:
                    command.append("--rotate=" + str(rotation))

                subprocess.call(command)
                os.remove(input_file)

def get_time_taken(file):
    """Return date time when photo or video was most likely taken"""

    f = open(file, 'rb')
    tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeOriginal')
    
    if 'EXIF DateTimeOriginal' in tags:
        date_time = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
        return calendar.timegm(date_time.utctimetuple())

    match=re.search(r'.+(\d{8}_\d{6}).+', file)
    
    if match:
        date_time = datetime.strptime(match.group(1), '%Y%m%d_%H%M%S')
        return calendar.timegm(date_time.utctimetuple())

    os_modify_time = os.path.getmtime(file)
    return os_modify_time

def get_input_files(directories):
    """Get all files from multiple directories sorted by date"""
    input_files = {}

    for directory in directories:
        files = glob(directory + '/' + '*.*')

        for file in files:
            time_taken = get_time_taken(file)

            while time_taken in input_files:
                time_taken += 1

            input_files[time_taken] = file

    return input_files

def process(input, output, year, event, photographer, skip_encode=False):
    output_folder = folder_path(output, year, event, photographer)
    mkdir(output_folder)
    print "Output directory:", output_folder

    input_files = get_input_files(input)
    
    copy_files(year, event, photographer, input_files, output_folder)

    if not skip_encode and not dry_run:
        encode_videos(output_folder)

    print "\nAll done!"

def main():
    arguments = docopt(__doc__, version='Photo Sort 1.0.0')

    if arguments['--dry-run']:
        dry_run = True

    process(arguments['--input'], arguments['<output>'], arguments['<year>'], arguments['<event>'], arguments['<photographer>'], arguments['--skip-encode'])

if __name__ == '__main__':
    main()