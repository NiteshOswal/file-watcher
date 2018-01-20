import sys
import time
from os import path, remove, makedirs
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Timer
from subprocess import call
from getopts import getopts

argv = getopts(sys.argv[1:])

##
# Important Note: Add the host's ~/.ssh/<public_key> to ~/.ssh/authorized_keys of the remote server, for this to work in "no hands" mode.
##

if "w" not in argv:
    print("You need to specify a directory to watch")
    sys.exit(0)

if "d" not in argv:
    print("You need to specify a destination path of the format user@root:/path/to/destination")
    sys.exit(0)

opts = {
    "current_path": path.dirname(__file__),
    "watch_path": path.realpath(argv["w"]),
    "destination_path": argv["d"]
}
opts["logger_path"] = path.join(opts["current_path"], "logs")

if not path.exists(opts["logger_path"]):
    makedirs(opts["logger_path"])

print("Now Watching:", opts["watch_path"])

file_pool = OrderedDict()

def set_interval(func, secs):
    def func_wrapper():
        set_interval(func, secs)
        func()
    t = Timer(secs, func_wrapper)
    t.start()
    return t

class AppEventHandler(LoggingEventHandler):

    def set_file_pool(self, event):
        if not event.is_directory:
            if event.event_type == EVENT_TYPE_MOVED:
                del file_pool[event.src_path]
                file_path = event.dest_path
            else:
                file_path = event.src_path
            if(path.basename(file_path)[0] != "."):
                file_pool[path.join(opts["watch_path"], file_path)] = [event.event_type, datetime.now()]

    def on_created(self, event):
        super(AppEventHandler, self).on_created(event)
        self.set_file_pool(event)

    def on_modified(self, event):
        super(AppEventHandler, self).on_modified(event)
        self.set_file_pool(event)

    def on_moved(self, event):
        super(AppEventHandler, self).on_moved(event)
        self.set_file_pool(event)

    def on_deleted(self, event):
        super(AppEventHandler, self).on_deleted(event)
        self.set_file_pool(event)

def push_to_destination(file_path):
    print("Pushing File:", file_path)
    call(["scp", file_path, opts["destination_path"]])
    file_pool[file_path][0] = "completed"

def remove_file(file_path):
    print("Removing File:", file_path)
    if path.exists(file_path) and file_pool[file_path][0] != EVENT_TYPE_DELETED:
        remove(file_path)
    del file_pool[file_path]

def file_worker():
    for file, stats in file_pool.items():
        print("Watching file: ", file)
        if stats[1] + timedelta(minutes=20) <= datetime.now():
            remove_file(file)
        if stats[1] + timedelta(minutes=5) <= datetime.now() and stats[0] != "completed":
            push_to_destination(file)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", filename=path.join(opts["logger_path"], "log.log"))
    event_handler = AppEventHandler() # Event handler
    observer = Observer() # Observer
    observer.schedule(event_handler, opts["watch_path"], recursive=True)
    observer.start()
    set_interval(file_worker, 60) # run the file worker in every 5 mins
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit) as e:
        observer.stop()
    observer.join()
