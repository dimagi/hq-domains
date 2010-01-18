#!/bin/sh

rm -rf /tmp/web
cp -R ../../web /tmp

#
# Get rid of cruft
#
rm -rf /tmp/web/.git # Just want to send over the code - not the history
find /tmp/web -name "settings_confidential.py" -delete
find /tmp/web -name "ToDo.txt" -delete
find /tmp/web -name "*.pyc" -delete
find /tmp/web -name .DS_Store -delete
find /tmp/web -name "*~" -delete

#
# If we don't cd here, the /tmp path is kept in the tar
#
cd /tmp
tar -cjf /tmp/web.tar.bz2 web
rm -rf /tmp/web

