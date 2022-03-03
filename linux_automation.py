"""
A script that watches for the connection of a volume called label (str)
"""

#!/usr/bin/env python3
import gi
from gi.repository import GLib, Gio
import subprocess
from kobo_backup import label


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
        if volume.get_name() == label:  # Send notification to user
            subprocess.Popen(
                [
                    "notify-send",
                    f"{volume.get_name()} connected",
                    "Attempting backup...",
                ]
            )
            # Run backup script
            subprocess.call(["python3", "kobo_backup.py"])


WatchForKobo()
