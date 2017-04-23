# refstack-sync-and-verify
working repository for a script that syncs and verifies a spreadsheet and a
MySQL contain refstack results

re: dependencies - this script requires a mysql db, the ability and the ability
to access google spread via their native auth. real docs to come
just getting
the basics set up.


//////////////////////////////////// Current Status & Functionality /////////////////////////////

* vendorDataDb/sync-db.py
  - creates and populates db if db does not exist
  - updates db based on existing records that have been changed
  - adds new records for product pairs that have been recently added to the spreadsheet
  - checks links and flags test results whose links are broken / nonexistent
  - pushes entries with updated flags and comments back to the spreadsheet.
vendorDatadb/vendorData.sql
  - database schema
* check-spreadsheet.py
  - checks links
  - reformats lines with multiple entries for the sake of easier updatability
  - prints warnings that broken links need checking
  - refreshes spreadsheet as it checks line
  - toggles update flag, leaves a reminder to check the result link for entries where links
        are broken
* update-rs-db.py
  - checks (without revealing vendor data) whether there is a match between a spreadsheet
    entry and a product entry in your db
  - if there is a match:
    * verifies the validity of the refstack result link
    * updates relevant fields in the internal db based on spreadsheet data
    * if all info is valid, change test status to verified
  - HAS BEEN SUBMITTED AS A REFSTACK PATCH FOR FURTHER TESTING. you can view this patch at
    https://review.openstack.org/#/c/452518/
* contents of vendorDataDb/api dir:
  - the beginnings of a CRUD api for the internal vendor data db. Obviously not complete or unified,
    but base functionality is working
 
