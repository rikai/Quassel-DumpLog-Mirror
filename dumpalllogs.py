#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2008 Ramon Klass <tier@schokokeks.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, see <http://www.gnu.org/licenses/>.

"""Description:
    dumplog.py dumps Quassel logs to files suitable for pisg (irc statistics generator)

Usage:
    dumplog.py [-d dbfile] -u user [-n network] [-c channel] [-o logfile]
    
    anything except -u is optional, default dbfile is ~/.quassel/quassel-storage.sqlite
    if any options are missing, an appropriate action is executed.

Examples:
    "dumplog.py -u somebody" lists all networks the user somebody is on
    "dumplog.py -u somebody -n Freenode" lists all buffers on network Freenode for user somebody"""

from optparse import OptionParser
import os.path
import quasseltool
import codecs
import sys
import re

reload(sys)  
sys.setdefaultencoding('utf8')

class Consolecounter:
    def __init__(self, head=None, tail=None):
        self.started = False
        self.head = head
        self.tail = tail

    def set_max(self, num):
        if not self.started:
            self.num = num
            self.numlen = len(str(num))

    def start(self):
        if not self.started:
            self.i = 0
            if not self.head is None:
                sys.stdout.write(self.head)
            for x in xrange(self.numlen):
                sys.stdout.write("  ")
            sys.stdout.write(" ")
            sys.stdout.flush()
            self.started = True
    
    def next(self):
        if self.started:
            self.i += 1
            for x in xrange(self.numlen):
                sys.stdout.write("\b\b")
            sys.stdout.write("\b")
            sys.stdout.write(str(self.i).rjust(self.numlen, " "))
            sys.stdout.write("/")
            sys.stdout.write(str(self.num))
            sys.stdout.flush()
            if self.i >= self.num:
                if not self.tail is None:
                    sys.stdout.write(self.tail)
                    sys.stdout.flush()
def last_line(in_file, block_size=1024, ignore_ending_newline=True):
    suffix = ""
    in_file.seek(0, os.SEEK_END)
    in_file_length = in_file.tell()
    seek_offset = 0

    while(-seek_offset < in_file_length):
        # Read from end.
        seek_offset -= block_size
        if -seek_offset > in_file_length:
            # Limit if we ran out of file (can't seek backward from start).
            block_size -= -seek_offset - in_file_length
            if block_size == 0:
                break
            seek_offset = -in_file_length
        in_file.seek(seek_offset, os.SEEK_END)
        buf = in_file.read(block_size)

        # Search for line end.
        if ignore_ending_newline and seek_offset == -block_size and buf[-1] == '\n':
            buf = buf[:-1]
        pos = buf.rfind('\n')
        if pos != -1:
            # Found line end.
            return buf[pos+1:] + suffix

        suffix = buf + suffix

    # One-line file.
    return suffix
class App():
    def __init__(self):
        self._init_opts()
        self._run()
    
    def _init_opts(self):
        parser = OptionParser(usage="%prog [-d DB] [-u USER] [-n NETWORK] [-c CHANNEL] [-o OUT]", version="%prog 0.0.1", description="""Quassel Logfile dumper currently exports mirc logs suitable for pisg. Default for DB is ~/.quassel/quassel-storage.sqlite. Run without options for more info""")
        parser.add_option("-d", "--db", action="store", type="string", default="", help="DB file to use")
        parser.add_option("-u", "--user", action="store", type="string", default="", help="quassel username")
        parser.add_option("-n", "--network", action="store", type="string", default="", help="IRC network")
        parser.add_option("-c", "--channel", action="store", type="string", default="", help="IRC channel/quassel buffer")
        parser.add_option("-o", "--out", action="store", type="string", default="", help="output file")
        (self.opts, self.args) = parser.parse_args()
    
    def _run(self):
        self.log = quasseltool.Logutil()
        #try:
        #    
        #    if self.opts.db == "":
        #        dbname = "(defaults)"
        #    else:
        #        dbname = self.opts.db
        #    print "FATAL: Unable to open db file %s"%os.path.expanduser(dbname)
        #    print "if it is somewhere else, use the -d FILE option"
        #    sys.exit(1)
        if self.opts.user == "":
            print "No user specified. Available options are:"
            for user in self.log.get_users():
                print user
            print "\nUse -u USER to choose one"
            sys.exit(0)
        if not self.log.is_user(self.opts.user):
            print "FATAL: User %s does not exist in DB"%self.opts.user
            sys.exit(1)
        if self.opts.out == "":
            print "No outfile specified. use -o filepath to do so.\nFiles will be overwritten if it exists"
            sys.exit(0)
        for network in self.log.get_networks(self.opts.user):
            self.opts.network = network
            for channel in self.log.get_buffers(self.opts.user, self.opts.network):
                self.opts.channel = channel
                if channel == "":
                    channel = "Buffer"
                try:
                    os.stat(self.opts.out + network)
                except:
                    os.mkdir(self.opts.out + network)
                channel = re.sub(">", "", channel)
                filename = os.path.expanduser(self.opts.out  + network + '/' + channel + ".log")
                if os.path.isfile(filename):
                    exists = True
                else:
                    exists = False
                outfile = codecs.open(filename, "a+", "iso8859_15", errors="replace")
                if exists:
                    #read time and date on last line of file so that the entire buffer wont have to be dumped again and can instead just be appended.
                    lastline = unicode(last_line(outfile))
                    time= re.search("\A\[\d{2}-\w{3}-\d{4} \d{2}:\d{2}:\d{2}\]",lastline)
                    if time:
                        time = time.group(0)[1:-1]+u".999"
                #outfile = codecs.open(filename, "wb", "utf-8")
                sys.stdout.write("Writing Logfile %s of channel %s on network %s for user %s... "%(filename, self.opts.channel, self.opts.network, self.opts.user))
                sys.stdout.flush()
                counter = Consolecounter("", "\nDone\n")
                self.log.getlog(self.opts.user, self.opts.network, self.opts.channel, outfile, counter=counter, log=self.log, time=time,)
                outfile.close()

if __name__ == "__main__":
    App()
