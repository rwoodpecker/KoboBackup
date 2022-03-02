import os

def create_linux_autostart_script(label, backup_base_directory):
    import os

    autostart_path = os.path.expanduser('~/.config/autostart/')
    script_name = 'linux_automation.py'
    desktop_file_name = 'auto_kobo_backup.desktop'
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
    with open(autostart_path + desktop_file_name, 'w') as script:
        script.write(desktopfile)

    # The python script called script_name is already in backup_base_directory
    # Allow it to be executable
    os.system('chmod +x ' + os.getcwd() + os.sep + script_name)

    print("Created file in autostart, see list of files there: ", os.listdir(os.path.expanduser('~/.config/autostart/')))