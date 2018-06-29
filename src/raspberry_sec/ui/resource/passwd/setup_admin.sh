#!/bin/bash

# README:
#
# Run this script as root !
#

# Delete
if [ -e passwd ]
then
	chmod 700 passwd
	rm passwd
fi

# Create
python3 setup_admin.py

# Chmod
chmod 444 passwd
