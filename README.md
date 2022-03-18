# Kobo Backup

A python script to backup the contents of your kobo device. Backups will be placed in ~/Backups/kobo by default but this can be customised. Backups are timestamped and independent of each other. Supports Linux, macOS and Windows.

## Auto Back-up
The Auto Back-up feature is currently supported on Linux

Auto Back-up will automatically create a back-up by running `kobo_backup.py` whenever you connect your Kobo to your PC.

### Linux
Auto back-up works by placing a `.desktop` script in your `/home/<user>/.config/autostart` folder.
This `.desktop` script contains instructions that simply execute a 'watcher' script that watches and waits for a volume named `KOBOeReader` to be added (that is, it waits for you to connect your Kobo). When it detects your Kobo, it executes `python3 kobo_backup.py`.

#### Setup
To set up auto-backup:
- Navigate to the KoboBackup folder
- Run `python3 kobo_backup.py --s` (`s` for set up)
- Restart your computer
- Connect your Kobo and it will automatically create a backup.

#### Cancel
To cancel auto back-up:
- Navigate to the KoboBackup folder
- Run `python3 kobo_backup.py --c` (`c` for cancel).

The `--c` option removes the script that autostarts the watcher script, and it also terminates the watcher script. That means you don't need to restart your PC for it to stop.

#### Disable
To temporarily disable auto back-up (until next restart):
- Navigate to the KoboBackup folder
- Run `python3 kobo_backup.py --d` (`d` for disable).

The `--d` option simply stops the background script that watches and waits for a Kobo to be connected. It assumes you have already set up auto-backup with `--s` and restarted your PC. If you haven't, nothing will happen. 
If you've setup auto-backup, the 'watcher' script will auto-run again next time you re-start your PC.

#### Enable
To temporarily enable (in a running terminal session):
- Navigate to the KoboBackup folder
- Run `python3 kobo_backup.py --e` (`e` for enable).

The `--e` option enables the watcher in your current terminal session. If you connect a Kobo, it will auto back-up. To stop this, just hit `ctrl+c` to stop the script. 
