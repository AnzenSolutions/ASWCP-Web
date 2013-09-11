ASWCP Web Panel
===============

ASWCP ("Anzen Solutions Web Control Panel") is a web-based control panel to manage multiple 
servers at once.  JavaScript is used heavily.

The primary development was focused on remote SSH, but other features have been implemented as well 
to varying degrees.  To add a server install the daemon and go to "API" in the web panel then click 
"click here" link to open up the challenge window.  Follow the directions and within seconds you'll 
be able to access the server from the panel.

Installation
-------------
To install the web panel an install script has been done to make the process 
easier for the end user.  Simply run the following command:
```wget -O - -o /dev/null https://raw.github.com/AnzenSolutions/ASWCP/master/web/install.sh | sh -```

This will download and pass the script to your shell.  After that, just make the appropriate 
edits to ".config" in the directory and run the server.py script.

What Is GateOne?
----------------
GateOne is a Python-developed SSH proxy service.  In short it allows you to access a machine's SSH service via 
the web.  While there is a lot of software out there that does this, GateOne was the easiest to 
customize and work with ultimately.

Why Redis?
----------
ASWCP requires some information constantly (usually from the database), but such requests are 
more often reads than writes.  Reading the database each time one of these requests are made 
makes no sense (performance or logic wise).  Redis is used to cache this data.

Redis is also used to cache command requests instead of storing them in the database.  It didn't 
make sense to store these requests in the database just to be a temporary storage when Redis does 
this type of thing for us easier and faster.  Unless you're looking to work with a lot of servers 
then the performance gain will most likely not be noticable, but once you do reach that point it'll 
be more than welcomed.

Why PostgreSQL?
---------------
In short, it's more resource efficient than MySQL, easier to manage and work with and what we use 
for our projects.  SQLite is also supported but not to a great degree yet.
