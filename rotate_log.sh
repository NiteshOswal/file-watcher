#!/usr/bin/env bash
log_dir="$(dirname $0)/logs/"
new_log_path="${log_dir}$(date +%Y-%m-%d)-log.log"
log_path="${log_dir}log.log"

mv ${log_path} ${new_log_path}