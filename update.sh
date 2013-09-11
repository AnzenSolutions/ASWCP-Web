#!/bin/sh

CUR_VER=$(cat version)
NEW_VER=$(wget --no-check-certificate -O - -o /dev/null https://raw.github.com/AnzenSolutions/ASWCP/master/web/version)

echo "Current Version: $CUR_VER"
echo "Most Recent Version: $NEW_VER"

if [ "$CUR_VER" != "$NEW_VER" ]; then
    echo "Update required.  Running install script..."
    
    # Below code is essentially copy/pasted from install.sh slightly fitted for update though
    GIT_BIN=$(which git | awk '{print $1}')
    WGET_BIN=$(which wget | awk '{print $1}')
    CURL_BIN=$(which curl | awk '{print $1}')

    URL="https://github.com/AnzenSolutions/ASWCP-Web/archive/master.tar.gz"

    FOLDER="ASWCP-Web"
    
    DL=0

    if [ -n "$GIT_BIN" ]; then
        git pull
        DL=2
    elif [ -n "$WGET_BIN" ]; then
        cd ..
        wget --no-check-certificate "$URL"
        DL=1
    elif [ -n "$CURL_BIN" ]; then
        cd ..
        curl "$URL"
        DL=1
    fi

    if [ $DL -eq 1 ]; then
        tar -xf master.tar.gz
        FOLDER="$FOLDER-master"
        rm -rf master.tar.gz
        cd $FOLDER
    elif [ $DL -eq 0 ]; then
        echo "Unable to download ASWCP Web Panel.  Please install either git, wget or curl and make sure `where` command can find it."
        exit 1
    fi

    echo "ASWCP Web Panel updated to $(cat version)."
fi

exit 0
