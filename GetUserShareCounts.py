#!/usr/bin/env python3
"""
# Purpose: For a Google Drive User(s), output a CSV file showing the share type counts for files shared by the user(s)
# Note: This script can use GAM7 or Advanced GAM:
#       https://github.com/GAM-team/GAM                                                                                                                               
#	https://github.com/taers232c/GAMADV-XTD3
# Customize: Set DOMAIN_LIST to the list of domains you consider internal Set LINK_FIELD and LINK_VALUE.
# Python: Use python or python3 below as appropriate to your system; verify that you have version 3
#  $ python -V   or   python3 -V
#  Python 3.x.y
# Usage:
# 1: Get ACLs for all files, if you don't want all users, replace all users with your user selection in the command below
#  $ Example: gam config auto_batch_min 1 redirect csv ./filelistperms.csv multiprocess all users print filelist fields id,name,owners.emailaddress,basicpermissions
# 2: From that list of ACLs, output a CSV file with headers:
#      Owner - email address of file owner
#      Total - total files owned by Owner
#      Shared - number of files shared
#      Shared External - number of files shared publically (anyone) or to a domain/group/user where the domain is not in DOMAIN_LIST
#      Shared Internal - number of files shared to a domain/group/user where the domain is in DOMAIN_LIST
#      anyone - number of shares to anyone
#      anyoneWithLink - number of shares to anyone with a link
#      externalDomain - number of shares to an external domain
#      externalDomainWithLink - number of shares to an external domain with a link
#      internalDomain - number of shares to an internal domain
#      internalDomainWithLink - number of shares to an internal domain with a link
#      externalGroup - number of shares to an external group
#      internalGroup - number of shares to an internal group
#      externalUser - number of shares to an internal user
#      internalUser - number of shares to an internal user
#      deletedGroup - number of shares to a deleted group
#      deletedUser - number of shares to a deleted user
#  $ python3 GetUserShareCounts.py filelistperms.csv usersharecounts.csv
"""

import csv
import re
import sys

# Substitute your internal domain(s) in the list below, e.g., DOMAIN_LIST = ['domain.com',] DOMAIN_LIST = ['domain1.com', 'domain2.com',]
DOMAIN_LIST = ['domain.com',]

# For GAMADV-XTD3 with drive_v3_native_names = false
#LINK_FIELD = 'withLink'
#LINK_VALUE = 'True'
# For GAMADV-XTD/GAMADV-XTD3 with drive_v3_native_names = true
LINK_FIELD = 'allowFileDiscovery'
LINK_VALUE = 'False'

QUOTE_CHAR = '"' # Adjust as needed
LINE_TERMINATOR = '\n' # On Windows, you probably want '\r\n'

def incrementCounter(counter):
  if not counterSet[counter]:
    userShareCounts[owner][counter] += 1
    counterSet[counter] = True

TOTAL_COUNTER = 'Total'
SHARED_COUNTER = 'Shared'
SHARED_EXTERNAL_COUNTER = 'Shared External'
SHARED_INTERNAL_COUNTER = 'Shared Internal'
HEADERS = [
  'Owner',
  TOTAL_COUNTER, SHARED_COUNTER, SHARED_EXTERNAL_COUNTER, SHARED_INTERNAL_COUNTER,
  'anyone', 'anyoneWithLink',
  'externalDomain', 'externalDomainWithLink',
  'internalDomain', 'internalDomainWithLink',
  'externalGroup', 'internalGroup',
  'externalUser', 'internalUser',
  'deletedGroup', 'deletedUser',
  ]
zeroCounts = {
  TOTAL_COUNTER: 0, SHARED_COUNTER: 0, SHARED_EXTERNAL_COUNTER: 0, SHARED_INTERNAL_COUNTER: 0,
  'anyone': 0, 'anyoneWithLink': 0,
  'externalDomain': 0, 'externalDomainWithLink': 0,
  'internalDomain': 0, 'internalDomainWithLink': 0,
  'externalGroup': 0, 'internalGroup': 0,
  'externalUser': 0, 'internalUser': 0,
  'deletedGroup': 0, 'deletedUser': 0,
  }
COUNT_CATEGORIES = {
  'anyone': {False: 'anyone', True: 'anyoneWithLink'},
  'domain': {False: {False: 'externalDomain', True: 'externalDomainWithLink'}, True: {False: 'internalDomain', True: 'internalDomainWithLink'}},
  'group': {False: 'externalGroup', True: 'internalGroup'},
  'user': {False: 'externalUser', True: 'internalUser'},
  'deleted': {'group': 'deletedGroup', 'user': 'deletedUser'},
  }
PERMISSIONS_N_TYPE = re.compile(r"permissions.(\d+).type")

if (len(sys.argv) > 2) and (sys.argv[2] != '-'):
  outputFile = open(sys.argv[2], 'w', encoding='utf-8', newline='')
else:
  outputFile = sys.stdout
outputCSV = csv.DictWriter(outputFile, HEADERS, lineterminator=LINE_TERMINATOR, quotechar=QUOTE_CHAR)
outputCSV.writeheader()

if (len(sys.argv) > 1) and (sys.argv[1] != '-'):
  inputFile = open(sys.argv[1], 'r', encoding='utf-8')
else:
  inputFile = sys.stdin

userShareCounts = {}
for row in csv.DictReader(inputFile, quotechar=QUOTE_CHAR):
  owner = row['owners.0.emailAddress']
  userShareCounts.setdefault(owner, zeroCounts.copy())
  counterSet = {TOTAL_COUNTER: False, SHARED_COUNTER: False, SHARED_EXTERNAL_COUNTER: False, SHARED_INTERNAL_COUNTER: False}
  for k, v in iter(row.items()):
    mg = PERMISSIONS_N_TYPE.match(k)
    if mg and v:
      permissions_N = mg.group(1)
      if row[f'permissions.{permissions_N}.role'] == 'owner':
        incrementCounter(TOTAL_COUNTER)
      else:
        incrementCounter(SHARED_COUNTER)
        if v == 'anyone':
          incrementCounter(SHARED_EXTERNAL_COUNTER)
          userShareCounts[owner][COUNT_CATEGORIES[v][row[f'permissions.{permissions_N}.{LINK_FIELD}'] == LINK_VALUE]] += 1
        else:
          domain = row.get(f'permissions.{permissions_N}.domain', '').lower()
          if not domain and v in ['user', 'group']:
            if row.get(f'permissions.{permissions_N}.deleted') == 'True':
              userShareCounts[owner][COUNT_CATEGORIES['deleted'][v]] += 1
              continue
            emailAddress = row[f'permissions.{permissions_N}.emailAddress'].lower()
            domain = emailAddress[emailAddress.find('@')+1:]
          internal = domain in DOMAIN_LIST
          incrementCounter([SHARED_EXTERNAL_COUNTER, SHARED_INTERNAL_COUNTER][internal])
          if v == 'domain':
            userShareCounts[owner][COUNT_CATEGORIES[v][internal][row[f'permissions.{permissions_N}.{LINK_FIELD}'] == LINK_VALUE]] += 1
          else: # group, user
            userShareCounts[owner][COUNT_CATEGORIES[v][internal]] += 1
for owner, counts in sorted(iter(userShareCounts.items())):
  row = {'Owner': owner}
  row.update(counts)
  outputCSV.writerow(row)

if inputFile != sys.stdin:
  inputFile.close()
if outputFile != sys.stdout:
  outputFile.close()
