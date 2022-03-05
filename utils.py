from dataclasses import dataclass
import json
import os
import platform
import subprocess
from typing import List
import tarfile


def backup_notify(user_os, backup_path):
    print("The backup notification function has been called")
    if user_os == "Linux":
        subprocess.Popen(["notify-send", f"Backed up!"])
        # Open the file explorer to the backed up directory
        subprocess.run(["xdg-open", backup_path])
    elif user_os == "macOS":
        subprocess.call(
            (
                "/usr/bin/osascript",
                "-e",
                'display notification "Backup of Kobo complete" with title "KoboBackup"',
            )
        )


def get_directory_size(directory):  # figure out how much was backed up.
    total = 0
    try:
        for entry in os.scandir(directory):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_directory_size(entry.path)
    except NotADirectoryError:
        return os.path.getsize(directory)
    except PermissionError:
        return 0
    return total


def get_size_format(
    b, factor=1024, suffix="B"
):  # convert bytes to something human readable.
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz", compresslevel=6) as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def get_user_os_and_kobo_mountpoint(label):
    """
    Returns a UserSystemInfo object with the user's OS and the kobo mountpoint.
    """
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
        return UserSystemInfo(user_os="Windows", kobos=kobos)

    elif platform.system() == "Linux":  # Get mount point on Linux
        lsblk_check = subprocess.check_output(["lsblk", "-f", "--json"]).decode("utf8")
        lsblk_json = json.loads(lsblk_check)
        kobos = [
            device
            for device in lsblk_json["blockdevices"]
            if device.get("label", None) == label
        ]
        kobos = [kobo["mountpoint"] for kobo in kobos]
        return UserSystemInfo(user_os="Linux", kobos=kobos)

    elif platform.system() == "Darwin":  # Get mount point on MacOS
        df_output = subprocess.check_output(("df", "-Hl")).decode("utf8")
        output_parts = [o.split() for o in df_output.split("\n")]
        kobos = [o[-1] for o in output_parts if f"/Volumes/{label}" in o]
        return UserSystemInfo(user_os="macOS", kobos=kobos)

    else:
        raise Exception(f"Unsupported OS: {platform.system()=} {platform.release()=}")


@dataclass
class UserSystemInfo:
    """
    Class to hold user system information.
    Has two attributes: user_os (str) and kobos (list of str of paths to mounted Kobo devices).
    """

    user_os: str
    kobos: List[str]
