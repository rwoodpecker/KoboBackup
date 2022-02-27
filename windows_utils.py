import os

def get_windows_mount_point(label):
    import wmi

    # Set up WMI object for later
    c = wmi.WMI()
    kobos = []
    # Get all drives and their infos
    for drive in c.Win32_LogicalDisk():
        # If any drive is called the label, append it to the list
        if drive.VolumeName == label:
            kobos.append(drive.Name + os.sep)
    return kobos
        