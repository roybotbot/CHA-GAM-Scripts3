#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User, get all drive file ACLs except those indicating the user as owner
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Use print filelist to get selected ACLs
#    Syntax: gam <UserTypeEntity> print filelist [anyowner|(showownedby any|me|others)]
#			[query <QueryDriveFile>] [fullquery <QueryDriveFile>] [select <DriveFileEntity>|orphans] [depth <Number>] [showparent]
#    For a full description of print filelist, see: https://github.com/taers232c/GAMADV-XTD/wiki/Users-Drive-Files
#    Example: gam redirect csv ./filelistperms.csv user testuser@domain.com print filelist id title permissions owners.emailaddress,mimetype pm not role owner em pmfilter
# 2: From that list of ACLs, output a CSV file with headers "Owner,driveFileId,driveFileTitle,permissionIds"
#    that lists the driveFileIds and permissionIds for all ACLs except those indicating the user as owner
#    (n.b., driveFileTitle is not used in the next step, it is included for documentation purposes)
#  $ python3 GetUserNonOwnerDrivePermissions.py filelistperms.csv deleteperms.csv
# 3: Inspect deleteperms.csv, verify that it makes sense and then proceed
# 4: If desired, delete the ACLs
#    Parallel, faster:
#  $ gam csv ./deleteperms.csv gam user "~Owner" delete permissions "~driveFileId" "~permissionIds"
#    Serial, cleaner output:
#  $ gam csvkmd users deleteperms.csv keyfield Owner subkeyfield driveFileId datafield permissionIds delimiter "," delete permissions csvsubkey driveFileId csvdata permissionIds
"""

import csv
import re
import sys

FILE_NAME = 'name'
ALT_FILE_NAME = 'title'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, ['Owner', 'driveFileId', 'driveFileTitle', 'mimeType', 'permissionIds'],
                           lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  permissionIds = []
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if v != 'user' or row[f'permissions.{permissions_N}.role'] != 'owner' or row.get(f'permissions.{permissions_N}.emailAddress', '') != row['owners.0.emailAddress']:
        permissionIds.append(row[f'permissions.{permissions_N}.id'])
  if permissionIds:
    outputCSV.writerow({'Owner': row['owners.0.emailAddress'],
                        'driveFileId': row['id'],
                        'driveFileTitle': row.get(FILE_NAME, row.get(ALT_FILE_NAME, 'Unknown')),
                        'mimeType': row['mimeType'],
                        'permissionIds': ','.join(permissionIds)})

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
