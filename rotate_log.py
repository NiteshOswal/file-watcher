from os import path
from datetime import datetime
from subprocess import call

log_path = path.join(path.dirname(__file__), "logs", "log.log")
new_log_path = path.join(path.dirname(__file__), "logs", str(datetime.now().date()) + "-log.log")
call(["mv", log_path, new_log_path])