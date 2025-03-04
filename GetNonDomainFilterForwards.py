#!/usr/bin/env python3
"""
# Purpose: For Gmail User(s), list/delete all filters that forward email outside of a list of specified domains
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get filters, if you don't want all users, replace all users with your user selection in the command below
#  $ Example: gam config auto_batch_min 1 redirect csv ./filters.csv multiprocess all users print filters
# 2: From that list of filters, output a CSV file that lists the filters that forward email outside of the specified domains.
#  $ python3 GetNonDomainFilterForwards.py filters.csv outsidefilters.csv
# 3: Inspect outsidefilters.csv, verify that it makes sense and then proceed
# 4: If desired, delete the filters
#  $ gam csv ./outsidefilters.csv gam user "~User" delete filter "~id"
"""

import csv
import re
import sys

# Substitute your domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

FORWARD_DOMAIN = re.compile(r"^forward .*@(.*)$")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

inputCSV = csv.DictReader(inputFile, quotechar=QUOTE_CHAR)
outputCSV = csv.DictWriter(outputFile, inputCSV.fieldnames, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

for row in inputCSV:
  v = row.get('forward', '')
  if v:
    mg = FORWARD_DOMAIN.match(v)
    if mg and mg.group(1) not in DOMAIN_LIST:
      outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
