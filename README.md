Photo Sort
==========

Copy photos, rename, create folders, compress videos.

All according to pre defined rules.

Command line
------------
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