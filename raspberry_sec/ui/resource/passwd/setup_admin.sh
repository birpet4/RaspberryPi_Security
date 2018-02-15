#!/bin/bash

# README:
#
# Run this script as root !
#

# Delete
chmod 700 passwd
rm passwd

# Create
python3.5 setup_admin.py

# Chmod
chmod 444 passwd