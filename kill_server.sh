#!/bin/sh

PID=$(netstat -ntlup | grep python | grep -v tcp6 | grep `cat .config | grep "^port" | awk '{print $3}'` | awk '{print $7}' | cut -d/ -f1)
CRON_PID=$(ps aux | grep cron. | grep -v grep | awk '{ print $2 }')

# Only attempt to kill the server if we see its running
if [ -n "$PID" ]; then
        kill -15 $PID
	kill -15 $CRON_PID
else
        echo "ASWCP web panel not found as running."
fi

exit 0
