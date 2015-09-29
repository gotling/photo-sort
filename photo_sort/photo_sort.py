import calendar
from datetime import datetime
import errno
from glob import glob
import json
import os
import re
import shutil

from exceptions import NoFileException, FolderNotEmptyException
import exiftool
from video import get_metadata_file, encode_videos

__author__ = 'marcus'

ignored_extensions = ['.thm', '.db', '.info']
version = 'Photo Sort 1.1.0.b1'


def folder_name(year=None, event=None, photographer=None, serial=None):
    if year and event:
        output_folder_name = '%s - %s' % (year, event)
    elif year:
        output_folder_name = year
    elif event:
        output_folder_name = event
    else:
        output_folder_name = ''

    if serial:
        if len(output_folder_name):
            output_folder_name += ' - ' + str(serial)
        else:
            output_folder_name = str(serial)

    if photographer:
        output_folder_name += ' - ' + photographer

    return output_folder_name


def folder_path(output=None, year=None, event=None, sub_event=None, photographer=None):
    if not year and not event and not sub_event and not photographer:
        output_folder_name = folder_name(serial=1)
    else:
        output_folder_name = folder_name(year=year, event=event, photographer=photographer)
    output_folder = os.path.join(os.path.abspath(output), output_folder_name)

    serial = 1

    while os.path.isdir(output_folder):
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


def get_output_file_name(year, event, sub_event, photographer, index_mask, index, input_file):
    output_file_name = index_mask % (index + 1)

    if sub_event:
        output_file_name += ' - ' + sub_event

    if event:
        output_file_name += ' - ' + event

    if year:
        if sub_event or event:
            output_file_name += ' ' + year
        else:
            output_file_name += ' - ' + year

    if photographer:
        output_file_name += ' - ' + photographer

    extension = os.path.splitext(input_file)[1]
    output_file_name += extension.lower()

    return output_file_name


def get_time_taken(file, et):
    """Return date time when photo or video was most likely taken"""
    metadata_file = get_metadata_file(file)

    try:
        date_time = datetime.strptime(str(et.get_tag('EXIF:DateTimeOriginal', metadata_file)), '%Y:%m:%d %H:%M:%S')
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

    with exiftool.ExifTool() as et:
        for directory in directories:
            files = glob(os.path.join(directory, '*.*'))

            for file in files:
                (base, extension)=os.path.splitext(file)
                if extension.lower() in ignored_extensions:
                    continue

                time_taken = get_time_taken(file, et)

                while time_taken in input_files:
                    time_taken += 1

                input_files[time_taken] = file

    return input_files


def get_rename_list(year, event, sub_event, photographer, input_files, output_folder):
    rename_list = []
    file_count = len(input_files)
    index_mask = get_index_mask(file_count)

    for index, key in enumerate(sorted(input_files)):
        input_file = input_files[key]
        output_file_name = get_output_file_name(year, event, sub_event, photographer, index_mask, index, input_file)
        if not output_folder:
            output_folder = os.path.dirname(input_file)
        output_file = os.path.join(output_folder, output_file_name)

        rename = {'from': input_file, 'to': output_file}
        rename_list.append(rename)

    return rename_list


class Mode:
    COPY = 0
    MOVE = 1


def mode_to_string(mode):
    if mode == Mode.COPY:
        return "copy"
    else:
        return "move"


class PhotoSort:
    def __init__(self, input, output, year, event, sub_event, photographer, encode, dry_run, move=False, rename_history=False):
        self.encode = encode
        self.dry_run = dry_run
        self.rename_history = rename_history
        self.input = input
        self.output = output
        self.year = year
        self.event = event
        self.sub_event = sub_event
        self.photographer = photographer

        self.output_folder = folder_path(self.output, self.year, self.event, self.sub_event, self.photographer) if self.output else None
        self.mode = Mode.MOVE if move else Mode.COPY

        input_files = get_input_files(input)
        if not len(input_files):
            raise NoFileException

        self.rename_list = get_rename_list(self.year, self.event, self.sub_event, self.photographer, input_files, self.output_folder)

    def set_mode(self, mode):
        self.mode = mode

    def set_encode_videos(self, encode):
        self.encode = encode

    def move_files(self, rename_list):
        for rename in rename_list:
            shutil.move(rename["from"], rename["to"])

            path, file_name = os.path.split(rename["to"])
            print(file_name)

        if not self.dry_run:
            print('Moved/renamed %d files.' % len(rename_list))

            if self.rename_history:
                with open(os.path.join(path, 'rename_history.json'), 'w') as rename_history:
                    json.dump(rename_list, rename_history)
        else:
            print('Would have moved/renamed %d files, if not dry run' % len(rename_list))

    def copy_files(self, rename_list):
        for rename in rename_list:
            if not self.dry_run:
                shutil.copy2(rename["from"], rename["to"])

            path, file_name = os.path.split(rename["to"])
            print(file_name)

        if not self.dry_run:
            print('Copied %d files.' % len(rename_list))
        else:
            print('Would have copied %d files, if not dry run' % len(rename_list))

    def process_files(self, rename_list):
        if self.mode == Mode.MOVE:
            self.move_files(rename_list)
        else:
            self.copy_files(rename_list)

    def get_summary(self):
        return """
Event: {0:<30}Sub event: {2}
Year:  {1:<27}Photographer: {3}

processing={6}, dry-run={4}, encode-videos={5},
output="{7}"
""".format(self.event or "", self.year or "", self.sub_event or "", self.photographer or "", self.dry_run, self.encode,
           mode_to_string(self.mode), self.output_folder or "Input directories")

    def get_preview(self):
        text = ""
        extension_count = {}

        len_before = len(os.path.split(self.rename_list[0]["from"])[1])
        len_after = len(os.path.split(self.rename_list[0]["to"])[1])

        header_format = "{0:^" + str(len_before) + "}{1:^" + str(len_after) + "}"
        text += header_format.format("Before", "After") + "\n"
        text += "-" * len_before + "\t" + "-" * len_after + "\n"

        for rename in self.rename_list:
            path, old_name = os.path.split(rename['from'])
            base, extension = os.path.splitext(old_name)
            path, new_name = os.path.split(rename['to'])

            if extension in extension_count:
                extension_count[extension] += 1
            else:
                extension_count[extension] = 1

            text += old_name + "\t" + new_name + "\n"

        extensions = []

        for extension in extension_count:
            extensions.append("%s=%d" % (extension, extension_count[extension]))

        text += "\nNumber of files:" + ", ".join(extensions)

        return text

    def process(self):
        if not self.dry_run and self.output:
            mkdir(self.output_folder)

        self.process_files(self.rename_list)

        if self.encode and not self.dry_run:
            if self.output:
                encode_videos(self.output_folder)
            else:
                for input_folder in self.input:
                    encode_videos(input_folder)

        if self.mode == Mode.MOVE and self.output:
            for input_folder in self.input:
                try:
                    os.rmdir(input_folder)
                except OSError as ex:
                    if ex.errno == errno.ENOTEMPTY:
                        raise FolderNotEmptyException('Directory "{0}" not empty, cold not remove'.format(input_folder))
