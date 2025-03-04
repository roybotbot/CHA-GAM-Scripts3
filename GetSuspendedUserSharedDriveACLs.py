#!/usr/bin/env python3
"""
# Purpose: Get all shared drive ACLs for a list of suspended users from a CSV file;
#    the user's primary email and aliases are checked
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Prepare a CSV file with a list of suspended user email addresses and aliases
#  $ gam redirect csv ./SuspendedUsers.csv print users query "isSuspended=True" fields primaryemail aliases
# 2: Get Shared Drive ACLs
#  $ gam config csv_output_header_drop_filter "User" redirect csv ./SharedDriveACLs.csv print shareddriveacls fields id,emailaddress,role,type
# 3: From that list of ACLs, output a CSV file with headers "id,name,createdTime,permissionId,role,emailAddress"
#    that lists the Shared Drive id, name and createdTime, permissionId, role and email address for the specified users
#  $ python3 GetSuspendedUserSharedDriveACLs.py SharedDriveACLs.csv SuspendedUserSharedDriveACLS.csv SuspendedUsers.csv
"""

import csv
import re
import sys

# The header in the CSV file that contains the user email addresses
USER_HEADER = 'primaryEmail'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

ALIASES_N = re.compile(r"aliases.(\d+)")
PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

userSet = set()
inputFile = open(sys.argv[3], 'r', encoding='utf-8')
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  user = row['primaryEmail'].lower()
  if user:
    userSet.add(user)
  for k, v in iter(row.items()):
    mg = ALIASES_N.match(k)
    if mg and v:
      userSet.add(v.lower())
inputFile.close()

outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
outputCSV = csv.DictWriter(outputFile, ['id', 'name', 'createdTime', 'permissionId', 'role', 'emailAddress'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

inputFile = open(sys.argv[1], 'r', encoding='utf-8')

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v == 'user':
      permissions_N = mg.group(1)
      if row.get(f'permissions.{permissions_N}.deleted', '') == 'True':
        continue
      emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
      if emailAddress in userSet:
        outputCSV.writerow({'id': row['id'],
                            'name': row['name'],
                            'createdTime': row['createdTime'],
                            'permissionId': f'id:{row[f"permissions.{permissions_N}.id"]}',
                            'role': row[f'permissions.{permissions_N}.role'],
                            'emailAddress': emailAddress})

inputFile.close()
outputFile.close()
