#!/usr/bin/env python2.7

import os
import sys
import stat
import hashlib

target = sys.argv[1]

print 'Searching for duplicates in %s' % target

class FileKeeper(object):
    """Maintains a list of known files"""
    def __init__(self):
        self._entries = {}

    def seen(self, target):
        # checksum check
        return target.checksum() in self._entries

    def add(self, target):
        self._entries[target.checksum()] = target

    def get(self, target):
        return self._entries[target.checksum()]

class FileEntry(object):
    """A seen file"""
    def __init__(self, root, target):
        self._path = os.path.join(root, target)
        self._size = os.stat(self._path).st_size
        content = open(self._path).read()
        self._csum = hashlib.md5(content).hexdigest()
        #print self

    def checksum(self):
        return self._csum

    def size(self):
        return self._size

    def path(self):
        return self._path

    def identical(self, fileEntry):
        me = open(self._path).read()
        him= open(fileEntry.path()).read()
        return me == him

    def __str__(self):
        return "path=%s\nsize=%s\ncsum=%s\n\n" % (self._path, self._size, self._csum)

keeper = FileKeeper()

for root, dirs, files in os.walk(target):
    print root
    for f in files:
        target = FileEntry(root, f)
        if not keeper.seen(target):
            keeper.add(target)
        else:
            seen = keeper.get(target)
            if seen.size() != target.size() \
             or not seen.identical(target):
                keeper.add(target)
            else:
                print "%s is a duplicate of:\n%s" % (f, seen)