#!/usr/bin/env bash
# wait-for-it.sh
# This script waits for the specified host and port to be available.

set -e

host="$1"
shift
cmd="$@"

until nc -z "$host" 3306; do
  >&2 echo "MariaDB is unavailable - sleeping"
  sleep 
done

>&2 echo "MariaDB is up - executing command"
exec $cmd
