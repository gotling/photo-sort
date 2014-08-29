#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort

Usage:
    photo-sort.py -i <input> ... -o <output> -y <year> -e <event> [-p <photographer>] [options]

Options:
    -i --input <input>...             Folder(s) with photos to process
    -o --output <output>              Where to create new folder
    -y --year <year>                  Year the photos were taken
    -e --event <event>                Name of the event
    -p --photographer <photographer>  Name of person taking the photos
    --skip-encode                     Do not encode videos
    --dry-run                         Make no changes
    --move                            Move files instead of copy

Example:
    photo-sort.py -i "Canon" -i "Samsung" -o "My Photos" -y 2014 -e Boom -p Marcus

More info:
    Encoding of videos requires HandBrakeCLI and ExifTool to be on the system path.
"""

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"

import os
import re
import json
import time
import errno
import shutil
import timeit
import calendar
import subprocess
from glob import glob
from datetime import datetime

import exifread
import exiftool
from docopt import docopt

ignored_extensions = ['.thm']
video_extensions = ['.avi', '.dv', '.mpg', '.mpeg', '.ogm', '.m4v', '.mp4', '.mkv', '.mov', '.qt']
handbrake_preset = 'Normal'

def folder_name(year, event, photographer, serial=None):
    output_folder_name = '%s - %s' % (year, event)
    
    if serial:
        output_folder_name += ' - ' + str(serial)
    
    if photographer:
        output_folder_name += ' - ' + photographer

    return output_folder_name

def folder_path(output, year, event, photographer):
    output_folder_name = folder_name(year, event, photographer)
    output_folder = os.path.join(os.path.abspath(output), output_folder_name)

    serial = 1

    while (os.path.isdir(output_folder)):
        serial += 1
        output_folder_name = folder_name(year, event, photographer, serial)
        output_folder = os.path.join(os.path.abspath(output), output_folder_name)

    return output_folder

def mkdir(output_folder):
    try:
        os.makedirs(output_folder)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def get_index_mask(file_count):
    """Get mask for for numbering of pictures"""
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
    files = glob(os.path.join(output_folder, '*.*'))

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

def get_metadata_file(file):
    """MPEG videos sometimes store EXIF data in a sepparate .thm file"""
    (base, extension)=os.path.splitext(file)

    if extension.lower() in ['.mpg', '.mpeg']:
        for meta_extension in ['.thm', '.THM']:
            meta_file = base + meta_extension

            if os.path.isfile(meta_file):
                return meta_file

        return file
    else:
        return file

def get_time_taken(file):
    """Return date time when photo or video was most likely taken"""
    metadata_file = get_metadata_file(file)
    f = open(metadata_file, 'rb')
    tags = exifread.process_file(f, details=False, stop_tag='EXIF DateTimeOriginal')
    
    if 'EXIF DateTimeOriginal' in tags:
        try:
            date_time = datetime.strptime(str(tags['EXIF DateTimeOriginal']), '%Y:%m:%d %H:%M:%S')
            return calendar.timegm(date_time.utctimetuple())
        except:
            # Invalid format in EXIF tag, continue
            pass

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
        files = glob(os.path.join(directory, '*.*'))

        for file in files:
            (base, extension)=os.path.splitext(file)
            if extension.lower() in ignored_extensions:
                continue

            time_taken = get_time_taken(file)

            while time_taken in input_files:
                time_taken += 1

            input_files[time_taken] = file

    return input_files

def get_rename_list(year, event, photographer, input_files, output_folder):
    rename_list = []
    file_count = len(input_files)
    index_mask = get_index_mask(file_count)
    
    for index, key in enumerate(sorted(input_files)):
        input_file = input_files[key]
        output_file_name = get_output_file_name(year, event, photographer, index_mask, index, input_file)
        output_file = os.path.join(output_folder, output_file_name)

        rename = {}
        rename['from'] = input_file
        rename['to'] = output_file
        rename_list.append(rename)

    return rename_list

class Mode:
    COPY = 0
    MOVE = 1

class PhotoSort():
    def __init__(self, skip_encode, dry_run, move=False):
        self.skip_encode = skip_encode
        self.dry_run = dry_run
        
        if move:
            self.mode = Mode.MOVE
        else:
            self.mode = Mode.COPY

    def set_mode(self, mode):
        self.mode = mode

    def move_files(self, rename_list):
        for rename in rename_list:
            shutil.move(rename["from"], rename["to"])

            path, file_name = os.path.split(rename["to"])
            print file_name

        if not self.dry_run:
            print 'Moved %d files.' % len(rename_list)
            with open(os.path.join(path, 'rename_history.json'), 'w') as rename_history:
                json.dump(rename_list, rename_history)
        else:
            print 'Would have moved %d files, if not dry run' % len(rename_list)

    def copy_files(self, rename_list):
        for rename in rename_list:
            if not self.dry_run:
                shutil.copy2(rename["from"], rename["to"])

            path, file_name = os.path.split(rename["to"])
            print file_name

        if not self.dry_run:
            print 'Copied %d files.' % len(rename_list)
        else:
            print 'Would have copied %d files, if not dry run' % len(rename_list)

    def process_files(self, rename_list):
        if self.mode == Mode.MOVE:
            self.move_files(rename_list)
        else:
            self.copy_files(rename_list)

    def process(self, input, output, year, event, photographer):
        print "Dry run:", self.dry_run, "Skip encode:", self.skip_encode, "Mode:", self.mode

        output_folder = folder_path(output, year, event, photographer)
        input_files = get_input_files(input)

        if len(input_files) == 0:
            print 'No files to process'
            return

        if not self.dry_run:
            mkdir(output_folder)

        print "Output directory:", output_folder
        
        rename_list = get_rename_list(year, event, photographer, input_files, output_folder)
        self.process_files(rename_list)

        if not self.skip_encode and not self.dry_run:
            encode_videos(output_folder)

        print "\nAll done!"

def main():
    arguments = docopt(__doc__, version='Photo Sort 1.0.0')

    photoSort = PhotoSort(arguments['--skip-encode'], arguments['--dry-run'], arguments['--move'])

    photoSort.process(arguments['--input'], arguments['--output'], year=arguments['--year'], event=arguments['--event'], photographer=arguments['--photographer'])

if __name__ == '__main__':
    main()
