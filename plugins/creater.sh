#!/bin/sh

# Simple helper script to create a plugin directory.
# Nothing more, nothing less.

if [ -z "$1" ]; then
	read -p "Plugin class: " CLASS
	read -p "Plugin name: " PLUGIN
elif [ -z "$2" ]; then
	CLASS="$1"
	read -p "Plugin name: " PLUGIN
else
	CLASS="$1"
	PLUGIN="$2"
fi

PDIR="$CLASS/$PLUGIN"
PFILE="$PDIR/$PLUGIN.py"
BASE=$(echo "$CLASS" | sed 's/\([a-z]\)\([a-zA-Z0-9]*\)/\u\1\2/g')
TEMPLATE="../templates/$PLUGIN.html"

if [ ! -d "$PDIR" ]; then
	mkdir -p "$PDIR"
	touch "$PFILE"

	echo "from plugins.bases.$CLASS import ${BASE}Base" > "$PFILE"
	echo "" >> "$PFILE"
	echo "class $PLUGIN(${BASE}Base):" >> "$PFILE"
	echo "    WEB_PATH = r\"/$PLUGIN\"" >> "$PFILE"
	echo "    STORE_ATTRS = True" >> "$PFILE"
	echo "    STORE_UNREF = True" >> "$PFILE"
	echo "    OPTS = {}" >> "$PFILE"
	echo "" >> "$PFILE"
	echo "    def get(self):" >> "$PFILE"
	echo "        self.show(\"$PLUGIN\", msg=\"empty\")" >> "$PFILE"

	touch $TEMPLATE

	echo "{% extends \"base.html\" %}" > $TEMPLATE
	echo "{% block content %}" >> $TEMPLATE
	echo "" >> $TEMPLATE
	echo "{% end %}" >> $TEMPLATE

	echo "Properly installed $PLUGIN to $PDIR; edit $PFILE now."
else
	echo "$PLUGIN already exists in $CLASS"

	if [ ! -f "$PFILE" ]; then
		echo "Plugin is not proper.  $PFILE must exist."
	else
		echo "Plugin is properly installed."
	fi
fi

exit 0