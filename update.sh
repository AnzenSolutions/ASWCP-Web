#!/bin/sh

CUR_VER=$(cat version)
NEW_VER=$(wget --no-check-certificate -O - -o /dev/null https://raw.github.com/AnzenSolutions/ASWCP/master/web/version)

echo "Current Version: $CUR_VER"
echo "Most Recent Version: $NEW_VER"

if [ "$CUR_VER" != "$NEW_VER" ]; then
    echo "Update required.  Running install script..."
    cd ..
    wget -O - -o /dev/null https://raw.github.com/AnzenSolutions/ASWCP/master/web/install.sh | sh -
fi

exit 0
