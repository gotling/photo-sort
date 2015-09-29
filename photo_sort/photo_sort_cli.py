#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Photo Sort

Usage:
    photo-sort.py -i <input> ... [-o <output>] [-y <year>] [-e <event>] [-s <sub-event>] [-p <photographer>] [options]

Options:
    -i --input <input>...             Folder(s) with photos to process
    -o --output <output>              Optional: If omitted, rename files in input folder.
                                        Otherwise folder where to create new output folder.
    -y --year <year>                  Optional: Year the photos were taken
    -e --event <event>                Optional: Name of the event
    -s --sub-event <sub-event>        Optional: Name of part of the event
    -p --photographer <photographer>  Optional: Name of person taking the photos
    --skip-encode                     Do not encode videos
    --dry-run                         Make no changes
    --move                            Move files instead of copy
    --rename-history                  Write names before and after move to a file in output directory

Example:
    photo-sort.py -i "Canon" -i "Samsung" -o "My Photos" -y 2014 -e Boom -p Marcus

More info:
    Encoding of videos requires HandBrakeCLI and ExifTool to be on the system path.
"""

from docopt import docopt
from exceptions import NoFileException, FolderNotEmptyException

from photo_sort import version, PhotoSort

__author__ = "Marcus Götling"
__license__ = "MIT"
__email__ = "marcus@gotling.se"


def yes_no_dialog(prompt):
    yes = {'yes', 'y', 'ye', 'j', ''}

    choice = input(prompt).lower()

    if choice in yes:
        return True
    else:
        return False


def main():
    arguments = docopt(__doc__, version=version)

    if not arguments['--output']:
        if len(arguments['--input']) > 1:
            print("Can not replace in place with more than one input directory")
            return
        arguments['--move'] = True

    try:
        sorter = PhotoSort(input=arguments['--input'], output=arguments['--output'],
                           year=arguments['--year'], event=arguments['--event'],
                           sub_event=arguments['--sub-event'], photographer=arguments['--photographer'],
                           encode=not arguments['--skip-encode'], dry_run=arguments['--dry-run'],
                           move=arguments['--move'], rename_history=arguments['--rename-history'])
    except NoFileException:
        print('No files to process.')
        return

    print(sorter.get_summary())

    #print("Building file list..\n")

    print(sorter.get_preview())

    if not yes_no_dialog("\nContinue? [yes] "):
        print('Photo sort aborted.')
        return

    try:
        sorter.process()
    except FolderNotEmptyException as e:
        print(e.message)

    print("\nAll done!")

if __name__ == '__main__':
    main()
