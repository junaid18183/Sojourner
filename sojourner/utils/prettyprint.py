# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from prettytable import PrettyTable #https://code.google.com/p/prettytable/wiki/Tutorial
from prettytable import from_db_cursor

# +----------------------------------------------------------------------+
#http://code.activestate.com/recipes/578801-pretty-print-table-in-tabular-format/
# Pretty Print table in tabular format
def PrettyPrint(table, justify = "R", columnWidth = 0):
    # Not enforced but
    # if provided columnWidth must be greater than max column width in table!
    if columnWidth == 0:
        # find max column width
        for row in table:
            for col in row:
                width = len(str(col))
                if width > columnWidth:
                    columnWidth = width

    outputStr = ""
    for row in table:
        rowList = []
        for col in row:
            if justify == "R": # justify right
                rowList.append(str(col).rjust(columnWidth))
            elif justify == "L": # justify left
                rowList.append(str(col).ljust(columnWidth))
            elif justify == "C": # justify center
                rowList.append(str(col).center(columnWidth))
        outputStr += ' '.join(rowList) + "\n"
    return outputStr
# +----------------------------------------------------------------------+

