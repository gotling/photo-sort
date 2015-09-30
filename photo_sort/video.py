import os
import shutil
import subprocess
from glob import glob

import exiftool

__author__ = 'marcus'


video_extensions = ['.avi', '.dv', '.mpg', '.mpeg', '.ogm', '.m4v', '.mp4', '.mkv', '.mov', '.qt', '.wmv', '.3gp', '.mod']
handbrake_preset = 'Normal'


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


def encode_videos(output_folder, decomb=False):
    """Encode videos using HandBrakeCLI"""
    files = glob(os.path.join(output_folder, '*.*'))

    with exiftool.ExifTool() as et:
        for input_file in files:
            (base, extension)=os.path.splitext(input_file)

            if extension in video_extensions:
                output_file = base + '.mp4'

                if os.path.exists(output_file):
                    shutil.move(input_file, input_file + '_')
                    input_file += '_'

                command = ["HandBrakeCLI", "--preset", handbrake_preset, "-i", input_file, "-o", output_file]

                rotation = get_video_rotation(et, input_file)
                if rotation:
                    command.append("--rotate=" + str(rotation))

                if decomb:
                    command.append("--decomb")

                subprocess.call(command)

                # Copy EXIF data and date from old to new file
                ret = subprocess.call(["exiftool", "-quiet", "-preserve", "-overwrite_original", "-TagsFromFile", input_file, output_file])
                if ret != 0:
                    print("Error copying EXIF information to new video!")

                os.remove(input_file)
