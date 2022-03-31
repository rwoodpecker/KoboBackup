"""
Creates a script in ~/.config/autostart that runs the automation/watcher_script.py script on startup.
"""

import os
from pathlib import Path
import signal
import subprocess
import sys


def automate_for_linux(args):
    """
    Automates the Kobo backup process for Linux.
    """
    # Check status of auto backup
    if args.status:
        # Check if auto backup is enabled
        try:
            # Check if watcher script is running (will throw subprocess.CalledProcessError if not)
            subprocess.check_output(["pgrep", "-f", "automation/watcher_script"])
            print("Auto backup is currently enabled (watching for Kobo...).")
        except subprocess.CalledProcessError:
            print("Auto backup is currently disabled (watcher script not detected).")
        # Check of the autostart file exists
        autostart_path = os.path.expanduser("~/.config/autostart/")
        desktop_file_name = "auto_kobo_backup.desktop"
        if os.path.exists(autostart_path + desktop_file_name):
            print("Auto backup will be enabled on restart.")
        else:
            print("Auto backup script will not run on restart.")
        sys.exit()

    # Setup auto backup
    if args.auto:
        create_linux_autostart_script(args)
        run_linux_watcher_script(args)
        sys.exit()

    # Temporarily disable auto_backup
    if args.disable:
        try:
            # Find pid of running watcher script
            pid = (
                subprocess.check_output(["pgrep", "-f", "automation/watcher_script"])
                .decode("utf-8")
                .strip()
            )
            # Kill it
            os.kill(int(pid), signal.SIGTERM)
            sys.exit()
        except subprocess.CalledProcessError:  # Command '['pgrep', '-f', 'automation/watcher_script']' will return non-zero exit status 1 if no process is found.
            print("No auto backup is currently running.")
            sys.exit()

    # Re-enable auto backup just for this session (will run in the terminal window it's called from)
    if args.enable:
        # Run the automation script
        run_linux_watcher_script(args)

    # Cancel auto backup
    if args.remove:
        # Remove the autostart script
        autostart_path = os.path.expanduser("~/.config/autostart/")
        desktop_file_name = "auto_kobo_backup.desktop"
        try:
            os.remove(autostart_path + desktop_file_name)
            print(
                "Cancelled auto-backup (removed file in autostart called "
                + desktop_file_name
                + ")"
            )
            try:
                # Find pid of running watcher script
                pid = (
                    subprocess.check_output(
                        ["pgrep", "-f", "automation/watcher_script"]
                    )
                    .decode("utf-8")
                    .strip()
                )
                # Kill it
                os.kill(int(pid), signal.SIGTERM)
                print("Killed running watcher script as well.")
            except subprocess.CalledProcessError:
                pass
        except FileNotFoundError:
            print("There was no auto backup set up.")
        sys.exit()


def create_linux_autostart_script(args):

    autostart_path = os.path.expanduser("~/.config/autostart/")
    desktop_file_name = "auto_kobo_backup.desktop"
    repo_location = os.getcwd()
    script_name = "automation/watcher_script.py"

    desktopfile = f"""[Desktop Entry]
Type=Application
Name=Auto Kobo Backup
Comment=Automatically backup your Kobo
Path={repo_location}
Exec={sys.executable} {script_name}
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
    subprocess.run(["chmod", "+x", repo_location + os.sep + script_name])

    print(
        f"Created file in autostart called {desktop_file_name}... Launching directory. After restarting your PC, your Kobo will be automatically backed up whenever you connect it. If you would like to do so before restarting, leave this terminal session running."
    )
    subprocess.run(["xdg-open", autostart_path])


def run_linux_watcher_script(args):
    """
    Run the linux watcher script temporarily (in current terminal).
    """
    print(
        "Running automation script temporarily in this terminal session. Connect your Kobo..."
    )
    path_to_automation_script = os.getcwd() + os.sep + "automation/watcher_script.py"
    subprocess.run(["chmod", "+x", path_to_automation_script])
    subprocess.run([sys.executable, path_to_automation_script])
