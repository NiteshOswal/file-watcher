#### A simple file watching & sync tool.

### Usage
```bash
# Clone it!
git clone https://github.com/NiteshOswal/file-watcher.git
# Virtualenv it!
virtualenv venv -p python3
# Activate it!
source venv/bin/activate
# Try it!
python watcher.py -w /path/to/watch -d user@remote.host:/path/to/sync
```

```bash
# Probably add a cron job to rotate log files
chmod +rx ./rotate_log.sh
59 23 * * * /path/to/rotate_log.sh
```


### Daemon
We use [circus](https://github.com/circus-tent/circus) to daemonize the `watcher` process. Check dummy config in `circus.example.ini`
```ini
[circus]
statsd = 1

[watcher:file-watcher]
cmd = /path/to/file-watcher/venv/bin/python3.5 watcher.py
args = -w /path/to/directory-to-watch -d user@host:/tmp
shell = True
stdout_stream.class = StdoutStream
stderr_stream.class = StdoutStream
```

And, daemonize it with `circusd`.

```bash
circusd --daemon circus.ini
```
