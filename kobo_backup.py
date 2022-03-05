import argparse
import datetime
import glob
import json
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys

from automation.automation_utils import automate_for_linux
from utils import get_directory_size, get_size_format


def main(args):

    label = "KOBOeReader"  # volume label of kobo - this is the default across models but could change in the future.
    backup_base_directory = str(
        os.path.join(os.path.expanduser("~"), "Backups", "kobo")
    )  # the folder in which backups will be placed. This should be OS agnostic.

    # This could just be `if len(sys.argv) > 1` but doing it like this makes it easier to add additional arguments for other features later.
    if args.auto or args.cancel or args.disable or args.enable or args.status:
        if platform.system() == "Linux":
            automate_for_linux(args)
        else:
            print(
                "The automation feature is currently only supported on Linux. Exiting...."
            )
            sys.exit()

    if platform.system() == "Windows":  # Get mount point on Windows
        import wmi

        # Set up WMI object for later
        c = wmi.WMI()
        kobos = []
        # Get all drives and their infos
        for drive in c.Win32_LogicalDisk():
            # If any drive is called the label, append it to the list
            if drive.VolumeName == label:
                kobos.append(drive.Name + os.sep)
        user_os = "Windows"
    elif platform.system() == "Linux":  # Get mount point on Linux
        lsblk_check = subprocess.check_output(["lsblk", "-f", "--json"]).decode("utf8")
        lsblk_json = json.loads(lsblk_check)
        kobos = [
            device
            for device in lsblk_json["blockdevices"]
            if device.get("label", None) == label
        ]
        kobos = [kobo["mountpoint"] for kobo in kobos]
        user_os = "Linux"
    elif platform.system() == "Darwin":  # Get mount point on MacOS
        df_output = subprocess.check_output(("df", "-Hl")).decode("utf8")
        output_parts = [o.split() for o in df_output.split("\n")]
        kobos = [o[-1] for o in output_parts if f"/Volumes/{label}" in o]
        user_os = "macOS"
    else:
        raise Exception(f"Unsupported OS: {platform.system()=} {platform.release()=}")

    if len(kobos) > 1:
        raise RuntimeError(f"Multiple Kobo devices detected: {kobos}.")
    elif len(kobos) == 0:
        print("No kobos detected.")
        sys.exit()
    else:
        [kobo] = kobos
        print(f"Kobo mountpoint is: {Path(kobo)} on {user_os}.")

    backup_folder_exists = os.path.isdir(
        backup_base_directory
    )  # check backup base directory exists locally, if not create it.
    if not backup_folder_exists:
        print(f"No backup folder detected. Creating {backup_base_directory}.")
        os.makedirs(backup_base_directory)
    else:
        print(
            f"An existing kobo backup folder was detected at {backup_base_directory}."
        )

    try:
        previous_backup = max(
            glob.glob(os.path.join(backup_base_directory, "*/")), key=os.path.getmtime
        )  # get the folder of the previous backup that occured
    except ValueError:
        pass

    backup_path = os.path.join(
        backup_base_directory,
        "kobo_backup_" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M"),
    )  # append datestamp to directory name.
    if os.path.isdir(backup_path):
        print(
            f"A backup of the kobo was already completed at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}. Try again in a minute."
        )
        sys.exit()

    try:  # copy files
        shutil.copytree(Path(kobo), backup_path)
    except OSError:  # some unrequired .Trashes will return 'operation not permitted'.
        pass

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
    try:
        # Only tested the below on Linux
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
