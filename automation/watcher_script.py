#!/usr/bin/env python3
from gi.repository import GLib, Gio
import subprocess
import sys

class WatchForKobo(object):

    def __init__(self):
        someloop = GLib.MainLoop()
        self.setup_watching()
        someloop.run()

    def setup_watching(self):
        self.watchdrives = Gio.VolumeMonitor.get()
        # event to watch (see further below, "Other options")
        self.watchdrives.connect("volume_added", self.actonchange)

    def actonchange(self, event, volume):
        if volume.get_name() == "KOBOeReader":
            # Send notification to user
            subprocess.Popen(['notify-send', f"{volume.get_name()} connected", "Attempting backup..."]) 
            # Run backup script
            subprocess.call(['python3', 'kobo_backup.py'])

if __name__ == "__main__":
    WatchForKobo()