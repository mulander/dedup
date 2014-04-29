#!/usr/bin/env python2.7

import os
import sys
import stat
import hashlib

BUFSIZE=8*1024

# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0 and num > -1024.0:
            return "%6.1f%6s" % (num, x)
        num /= 1024.0
    return "%6.1f%6s" % (num, 'TB')

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

    def report(self):
        wasting_space = filter(lambda e: e.wasted() > 0, self._entries.values())
        return sorted(wasting_space, key=lambda e: -e.wasted())

    def wasted(self):
        wasted = 0
        for entry in self._entries.values():
            wasted += entry.wasted()
        return wasted

class FileEntry(object):
    """A seen file"""
    def __init__(self, root, target):
        self._path = os.path.join(root, target)
        self._size = os.stat(self._path).st_size
        m = hashlib.md5()
        with open(self._path, 'rb') as f:
            while True:
                content = f.read(BUFSIZE)
                if not content:
                    break
                m.update(content)
        self._csum = m.hexdigest()
        self._duplicates = []

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

    def wasted(self):
        return self._size * len(self._duplicates)

    def duplicate(self, fileEntry):
        self._duplicates.append(fileEntry.path())

    def __str__(self):
        return "%s wasted by duplicates of %s:\n%s" % (sizeof_fmt(self.wasted()), self._path, '\n'.join(self._duplicates))

def dedup(target):
    keeper = FileKeeper()

    print 'Searching for duplicates in %s' % target
    for root, dirs, files in os.walk(target):
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
                    seen.duplicate(target)
    return keeper

def report(keeper):
    for entry in keeper.report():
        print
        print entry

    print
    print "%s wasted in total" % sizeof_fmt(keeper.wasted())

if __name__ == '__main__':
    target = sys.argv[1]
    keeper = dedup(target)
    report(keeper)