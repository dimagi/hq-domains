#!/usr/bin/env python

# Stolen from http://code.activestate.com/recipes/499305/

import sys, os, glob, tempfile
from django.core.management import execute_manager

import os, fnmatch

def locate(pattern='*.fixture.???', root='/Users/ross/web'):
    '''Locate all files matching supplied filename pattern in and below
    supplied root directory.'''
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)

for f in locate():
    num = f.split('.')[-1]
    if int(num) > 10:
        print "Removing", f
        os.remove(f)

