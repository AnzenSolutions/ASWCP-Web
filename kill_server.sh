#!/bin/sh

PID=$(netstat -ntlup | grep python | grep -v tcp6 | grep `cat .config | grep "^port" | awk '{print $3}'` | awk '{print $7}' | cut -d/ -f1)

kill -15 $PID

exit 0
