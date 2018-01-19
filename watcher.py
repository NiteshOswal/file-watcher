import sys
import time
from os import path, remove
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler, EVENT_TYPE_MOVED, EVENT_TYPE_DELETED, EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED
from collections import OrderedDict
from datetime import datetime, timedelta
from threading import Timer
from subprocess import call

current_dir = path.dirname(__file__)
watch_dir = path.realpath(sys.argv[1] if len(sys.argv) > 1 else ".")
print("Watch Directory: " + watch_dir)
file_pool = OrderedDict()

def set_interval(func, secs):
    def func_wrapper():
        set_interval(func, secs)
        func()
    t = Timer(secs, func_wrapper)
    t.start()
    return t

class AppEventHandler(LoggingEventHandler):

    def log_file_pool(self):
        print(file_pool)

    def set_file_pool(self, event):
        if not event.is_directory:
            if event.event_type == EVENT_TYPE_MOVED:
                del file_pool[event.src_path]
                file_path = event.dest_path
            else:
                file_path = event.src_path
            if(path.basename(file_path)[0] != "."):
                file_pool[path.join(watch_dir, file_path)] = [event.event_type, datetime.now()]

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
    print("Pushing File: ", file_path)
    call(["scp", file_path, ""])
    file_pool[file_path][0] = "completed"

def remove_file(file_path):
    print("Removing File: ", file_path)
    del file_pool[file_path]
    remove(file_path)

def file_worker():
    for file, stats in file_pool.items():
        print("File watching: " + file)
        if stats[1] + timedelta(seconds=40) <= datetime.now():
            remove_file(file)
        if stats[1] + timedelta(seconds=20) <= datetime.now() and stats[0] != "completed":
            push_to_destination(file)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    # Event handler
    event_handler = AppEventHandler()
    # Observer
    observer = Observer()

    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.start()
    set_interval(file_worker, 300) # run the file worker in every 5 mins
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()