import sys

if sys.version < 3:
    iteritems = dict.iteritems
else:
    iteritems = dict.items

