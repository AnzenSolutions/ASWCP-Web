#!/bin/sh

# Used to install ASWCP Web Panel.  git is the preferred method (easy to update),
# otherwise wget then finally curl is checked.  If none are installed, exits with error.

GIT_BIN=$(which git | awk '{print $1}')
WGET_BIN=$(which wget | awk '{print $1}')
CURL_BIN=$(which curl | awk '{print $1}')

URL="https://github.com/AnzenSolutions/ASWCP-Web/archive/master.tar.gz"

if [ -z "$GIT_BIN" ]; then
    echo "git not installed, attempting install with wget..."
else
    git clone git@github.com:AnzenSolutions/ASWCP-Web.git
fi

if [ -z "$WGET_BIN" ]; then
    echo "git and wget not installed, attempting install with curl..."
else
    wget "$URL"
fi

if [ -z "$CURL_BIN" ]; then
    echo "git, wget and curl are not installed.  Please install one and run $0 again."
    exit 1
else
    curl -O "$URL"
fi

if [ -e "master.tar.gz" ]; then
    tar -xf master.tar.gz
fi

echo "ASWCP Web Panel installed into ASWCP-Web."
exit 0
