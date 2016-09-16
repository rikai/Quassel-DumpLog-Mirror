# Quassel DumpLog Mirror

This is a simple mirror of http://pastebin.com/rxcK6BmV

These scripts were originally written by their respective authors and postgresql support was added by TecknoJock

* **quasseltool.py** - This is the core database handling module, required for both versions of dump log.
Def cursor needs to be updated with your credentials for the postgresql quassel db in order to use.

* **dumpalllogs.py** - This module dumps all buffers of a particular user. Each buffer will have its own file and will be separated in to folders according to Network Name. Supports appending based on most recent timestamp in log file.

* **dumplog.py** - The original module updated to postgresql. Now supports appending to a buffer based on most recent timestamp in log file.
