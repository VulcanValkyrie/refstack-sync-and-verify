# refstack-sync-and-verify
working repository for a script that syncs and verifies a spreadsheet and a
MySQL contain refstack results

re: dependencies- this script requires a mysql db, the ability and the ability
to access google spread via their native auth. real docs to come; just getting
the basics set up.

note: for the time being, I am disregarding the line length requirement of
pep-8. I will remedy that soon, but for the time being, I am leaving it as is

////////////////////////////////////////Commit History & Progress/////////////////////////////////////////////

* 3/10/17: 
  - Initial commit. Much to clean up, much to streamline. More soon
    current state: parses and loads spreadsheet into db with no duplicate
    entries.
  - Cleaned up pep-8 formatting, minor item ID matching debug
* 3/11/17
  - refactor for more sensible code flow, implemented functionality
    to update an existing database.
* 3/12/17
  - accounted for the databases' returning None in place of a tuple.
* 3/13/17
  - implemented check that allows us to push to the database entries that
    did not already exist.
* 3/14/17
  - implemented a check to make sure a result's link exists/is
    functional
  - implemented a "flag result" function to flag results with broken links for
    review
  - began refactor of existing code. Separated out the functionality of querying
    for company and product id, as well as converting federated and license_update
    fields from the human-readable string format to the tinyint format used by
    mysql to represent booleans
* 3/15/17-early 3/16/17
  - added a script which reformats a test results spreadsheet for greater
    readability, as well as checking links to make sure they are all valid
* 3/17/17
  - debugged linkchecking functionality, got the file to write to csv, tried to get
    update file upload functionality working
* 3/18/17
  - tried to debug csv upload, then when it turned out that that gspread functionality
    is either broken or deprecated, updated script to wipe the spreadsheet and readd
    the newly updated entries as they are checked. this proved to be successful
* 3/19/17
  - updated script to toggle the update flag, as well as adding a note that tells the
    reader to check the results link, given that it is not working
* 3/20/17
  - cleaned up check-spreadsheet script for push to refstack repo for further testing
* 3/21/17
  - started refactor of sync-db script for better handling of edge cases and greater
    processing speed

////////////////////////////////////Current Status & Functionality//////////////////////////////////////////////

* sync-db.py
  - populates db if db does not exist
  - updates db based on existing records that have been changed
  - adds new records for product pairs that have been recently added to the spreadsheet
  - checks links and flags test results whose links are broken/nonexistent
* check-spreadsheet.py
  - checks links
  - (attempts to) reformat lines with multiple entries for the sake of easier updatability
  - prints warnings that broken links need checking
  - refreshes spreadsheet as it checks line
  - toggles update flag, leaves a reminder to check the result link for entries where links
    arre broken
  - pushed to refstack repo for more rigorous testing.

////////////////////////////////////////////////Coming Soon///////////////////////////////////////////////////////

*  planning to refactor for increased simplicity/less code replication
* "pull entry" function that gathers entries from the contents of the DB
