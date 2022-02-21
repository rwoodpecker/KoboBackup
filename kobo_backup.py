import json
import os
import datetime
from pathlib import Path
import subprocess
import sys
import shutil

label = 'KOBOeReader' # name of kobo - this is the default.
backup_base_directory = str(os.path.join(os.path.expanduser('~'), 'Backups', 'kobo')) # the folder in which backups will be placed. This should be os agnostic.

print(backup_base_directory)

try: #get kobo mount point
    lsblk_check = subprocess.check_output(['lsblk', '-f', '--json']).decode('utf8')
    lsblk_json = json.loads(lsblk_check)
    kobos = [device for device in lsblk_json['blockdevices'] if device.get('label', None) == label]
    kobos = [kobo['mountpoint'] for kobo in kobos]
except FileNotFoundError:  # macOS (does not have lsblk)
    print('lsblk not found - macOS detected.')
    df_output = subprocess.check_output(('df', '-Hl')).decode('utf8')
    output_parts = [o.split() for o in df_output.split('\n')]
    kobos = [o[-1] for o in output_parts if f'/Volumes/{label}' in o]

if len(kobos) > 1:
    raise RuntimeError(f'Multiple Kobo devices detected: {kobos}')
elif len(kobos) == 0:
    print('No kobos detected')
    sys.exit()
else:
    [kobo] = kobos
    print(f'Kobo mountpoint is: {Path(kobo)}.')

backup_folder_exists = os.path.isdir(backup_base_directory) # check backup base directory exists locally, if not create it.
if not backup_folder_exists:
    print(f'No backup folder detected. Creating {backup_base_directory}')
    os.makedirs(backup_base_directory)
    print(f'created folder: {backup_base_directory}')
else:
    print(f'An existing kobo backup folder was detected at {backup_base_directory}.')

backup_path = os.path.join(backup_base_directory, 'kobo_backup_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M'))
print(backup_path)
if os.path.isdir(backup_path):
    print(f"A backup of the kobo has already completed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}. Try again in a minute.")
    sys.exit()

try: # copy files
    shutil.copytree(Path(kobo), os.path.join(backup_path))
except:
    pass

def get_directory_size(directory): # figure out how much was backed up
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        # if `directory` isn't a directory, get the file size then
        return os.path.getsize(directory)
    except PermissionError:
        # if we can't open the folder, return 0
        return 0
    return total

def get_size_format(b, factor=1024, suffix="B"): # convert bytes to something human readable.
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

backup_file_count = sum(len(files) for _, _, files in os.walk(backup_path)) # count number of files backed up.
print(f'Backup complete. Copied {backup_file_count} files with a size of {get_size_format(get_directory_size(backup_path))} to {backup_path}.')
