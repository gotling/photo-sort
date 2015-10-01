import os
import shutil
import subprocess
from glob import glob

import exiftool
import photo_sort

__author__ = 'marcus'


video_extensions = ['.avi', '.dv', '.mpg', '.mpeg', '.ogm', '.m4v', '.mp4', '.mkv', '.mov', '.qt', '.wmv', '.3gp', '.mod']
handbrake_preset = 'Normal'


def degrees_to_handbrake_rotation(degrees):
    """Return value HandBrake uses for rotation"""

    if degrees == 90:
        return 4
    elif degrees == 180:
        return 3
    elif degrees == 270:
        return 7
    else:
        return None


def get_rotation(et, input_file):
    degrees = et.get_tag('Rotation', input_file)
    return degrees_to_handbrake_rotation(degrees)


def get_encode_command(input_file, output_file, rotation, decomb):
    command = ["HandBrakeCLI", "--preset", handbrake_preset, "-i", input_file, "-o", output_file]

    if rotation:
        command.append("--rotate=" + str(rotation))

    if decomb:
        command.append("--decomb")

    return command


def get_exif_command(input_file, output_file):
    return ["exiftool", "-quiet", "-preserve", "-overwrite_original", "-TagsFromFile", input_file, output_file]


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

                rotation = get_rotation(et, input_file)
                command = get_encode_command(input_file, output_file, rotation, decomb)
                subprocess.call(command)

                # Copy EXIF data and date from old to new file
                command = get_exif_command(input_file, output_file)
                ret = subprocess.call(command)
                if ret != 0:
                    print("Error copying EXIF information to new video!")

                os.remove(input_file)


def write_batch_list_windows(output_folder, decomb=False):
    """Write batch file which will encode videos when runt
    Find videos
    Build output name
    Rename file if output exists
    Encode video
    Copy Exif data from old video to new
    Remove old video
    """
    error = " || goto :error"
    content = []

    files = glob(os.path.join(output_folder, '*.*'))

    with open(os.path.join(output_folder, 'batch-encode.bat'), 'w') as batch:
        content.append("@echo off\n")
        content.append("rem created by: %s\n\n" % photo_sort.version)
        # content.append("rem files: %d\n\n" % len(files))  # Write number of video files
        with exiftool.ExifTool() as et:
            for input_file in files:
                (base, extension) = os.path.splitext(input_file)

                if extension in video_extensions:
                    output_file = base + '.mp4'

                    rotation = get_rotation(et, input_file)

                    if os.path.exists(output_file):
                        content.append("move %s %s_ %s\n" % (input_file, input_file, error))
                        input_file += '_'

                    command = get_encode_command(input_file, output_file, rotation, decomb)
                    content.append(" ".join(command) + error + "\n")

                    command = get_exif_command(input_file, output_file)
                    content.append(" ".join(command) + error + "\n")

                    content.append("rm %s %s\n\n" % (input_file, error))
        content.append(":error\n")
        content.append("echo Failed with error #%errorlevel%.\n")
        content.append("exit /b %errorlevel%\n")

        batch.writelines(content)
