"""
Creates a script in ~/.config/autostart that runs the linux_automation.py script on startup.
"""

import os


def create_linux_autostart_script():

    autostart_path = os.path.expanduser("~/.config/autostart/")
    script_name = "linux_automation.py"
    desktop_file_name = "auto_kobo_backup.desktop"
    repo_location = os.getcwd()

    desktopfile = f"""[Desktop Entry]
Type=Application
Name=Auto Kobo Backup
Comment=Automatically backup your Kobo
Path={repo_location}
Exec=/usr/bin/python3 {script_name}
StartupNotify=true
X-GNOME-Autostart-enabled=true
X-GNOME-Autostart-Delay=0
    """

    # write the desktop file, which will be run when the user logs in
    with open(autostart_path + desktop_file_name, "w") as script:
        script.write(desktopfile)

    # The python automation script called script_name that watches for the Kobo connection
    # is in the same directory as this script.
    # Allow it to be executable.
    os.system("chmod +x " + repo_location + os.sep + script_name)

    print(
        f"Created file in autostart called {desktop_file_name}... Launching directory."
    )
    os.system(f"xdg-open {autostart_path}")
