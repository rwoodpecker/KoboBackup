import argparse
import datetime
import glob
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from automation.automation_utils import automate_for_linux
from utils import get_directory_size, get_size_format, get_user_os_and_kobo_mountpoint

def main(args):

    # Volume label of kobo - this is the default across models but could change in the future.
    label = "KOBOeReader"
    # the folder in which backups will be placed. This is OS agnostic.
    backup_base_directory = str(
        os.path.join(os.path.expanduser("~"), "Backups", "kobo")
    )  

    # Check if user is trying to set up automation.
    # This check could just be `if len(sys.argv) > 1` but doing it like this makes it easier to add additional arguments for other features later.
    if args.auto or args.cancel or args.disable or args.enable or args.status:
        if platform.system() == "Linux":
            automate_for_linux(args)
        else:
            print(
                "The automation feature is currently only supported on Linux. Exiting...."
            )
            sys.exit()

    system_info = get_user_os_and_kobo_mountpoint(label)

    # Check we have one and only one Kobo connected
    if len(system_info.kobos) > 1:
        raise RuntimeError(f"Multiple Kobo devices detected: {system_info.kobos}.")
    elif len(system_info.kobos) == 0:
        print("No kobos detected.")
        sys.exit()
    else:
        [kobo] = system_info.kobos
        print(f"Kobo mountpoint is: {Path(kobo)} on {system_info.user_os}.")

    # Check backup base directory exists locally, if not create it.
    backup_folder_exists = os.path.isdir(
        backup_base_directory
    ) 
    if not backup_folder_exists:
        print(f"No backup folder detected. Creating {backup_base_directory}.")
        os.makedirs(backup_base_directory)
    else:
        print(
            f"An existing kobo backup folder was detected at {backup_base_directory}."
        )

    # Append datestamp to directory name.
    backup_path = os.path.join(
        backup_base_directory,
        "kobo_backup_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),
    )  
    # Check that we haven't already backed up during this minute.
    if os.path.isdir(backup_path):
        print(
            f"A backup of the kobo was already completed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}. Try again in a minute."
        )
        sys.exit()

    # Get the folder of the previous backup that occured
    try:
        previous_backup = max(
            glob.glob(os.path.join(backup_base_directory, "*/")), key=os.path.getmtime
        )  
    except ValueError:
        pass

    # Copy files
    try: 
        shutil.copytree(Path(kobo), backup_path)
    except OSError:  # some unrequired .Trashes will return 'operation not permitted'.
        pass

    # Print size of last backup and current backup to stdout.
    try:
        previous_backup
        print(
            f"The previous backup contained {sum(len(files) for _, _, files in os.walk(previous_backup))} files and was {get_size_format(get_directory_size(previous_backup))}."
        )
    except NameError:
        pass

    print(
        f"Backup complete. Copied {sum(len(files) for _, _, files in os.walk(backup_path))} files with a size of {get_size_format(get_directory_size(backup_path))} to {backup_path}."
    )

    # Only tested the below on Linux
    try:
        # Open a notification to say it was backed up
        subprocess.Popen(["notify-send", f"Backed up!"])
        # Open the file explorer to the backed up directory
        subprocess.run(["xdg-open", backup_path])
    except Exception:
        pass


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument(
        "-c", "--cancel", help="cancel auto backup", action="store_true"
    )
    args.add_argument(
        "-d", "--disable", help="temporarily disable auto backup (until next restart)", action="store_true"
    )
    args.add_argument(
        "-e", "--enable", help="enable auto backup for this session only (will run in this terminal)", action="store_true"
    )
    args.add_argument(
        "-a", "--auto", help="create the auto backup script", action="store_true"
    )
    args.add_argument(
        "-s", "--status", help="show status of auto backup", action="store_true"
    )
    args = args.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
