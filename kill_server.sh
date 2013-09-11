#!/bin/sh

PID=$(netstat -ntlup | grep python | grep -v tcp6 | grep `cat .config | grep "^port" | awk '{print $3}'` | awk '{print $7}' | cut -d/ -f1)

# Only attempt to kill the server if we see its running
if [ -n "$PID" ]; then
        kill -15 $PID
else
        echo "ASWCP web panel not found as running."
fi

exit 0
