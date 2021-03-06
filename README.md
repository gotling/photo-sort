Photo Sort
==========

Copy photos, rename, create folders, compress videos.

All according to pre defined rules.

Command line
------------
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
        https://handbrake.fr/downloads2.php
        http://www.sno.phy.queensu.ca/~phil/exiftool/