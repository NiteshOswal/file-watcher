## File watching daemon

Usage
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