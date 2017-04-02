#######################################################################
#                           update-rs-db.py                           #
#######################################################################

This document contains some details that are neccessary to know to be
successful in the usage of the script update-rs-db.py.

The script beins by checking to see if your local refstack database
contains any of the products documented in a google spreadsheet. The
columns in this spreadsheet are, in this order:
 - Company Name
 - Product Name
 - Type (Distribution, Public, or Private)
 - Region
 - Guideline
 - Component (Compute, Platform, or Storage
 - Reported Release
 - Passed Release
 - Federated identity (yes/no)
 - Refstack Link
 - Zendesk Link
 - Marketplace Link
 - License Date
 - Update Product (yes/no)
 - Contacts
 - Notes
 - License Link
 - Active (1 or 0)
 - Public (1 or 0)

This data is stored in a Google spreadsheet, and therefore must be
accessed via Google's API. In order to access this, we must set up a
service account, and share the spreadsheet to that service account.
Instructions on how to go through the process of setting this for
usage with the gspread library can be found at:
http://gspread.readthedocs.io/en/latest/oauth2.html

After you have set up your service account, be sure to sub in the
details related to the auth process in place of the angle-bracket-
enclosed versions currently in the script. The field you need to
modify here is "<google api credential json file>".

The other fields that must be modified are:
 - "<google spreadsheet document id>", which can be found in the URL
    of the spreadsheet in question,
 - "<spreadsheet name>",
 - "<refstack server>", which is the server that contains your
    refstack-db. In many cases, this is the localhost you are running
    the script on,
 - "<user>", which is the user refstack uses to access to MySQL db
 - and "<password>".

If a corresponding Product is found in the local refstack database, the
script then proceeds to check all RefStack links stored by the Spreadsheet.
If one of them is valid, the script saves the test ID.

It then uses that test ID to update the internal db using refstack's built
in RESTful api.

Lastly, if at least one of the links has proven to be valid, we will
then use the same RESTful api, and test ID to update the verification_status
field associated with that test result.

