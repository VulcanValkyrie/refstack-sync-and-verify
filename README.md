# refstack-sync-and-verify
working repository for a script that syncs and verifies a spreadsheet and a
MySQL contain refstack results

re: dependencies - this script requires a mysql db, the ability and the ability
to access google spread via their native auth. real docs to come
just getting
the basics set up.

note: for the time being, I am disregarding the line length requirement of
pep - 8. I will remedy that soon, but for the time being, I am leaving it as is

//////////////////////////////////////// Commit History & Progress ////////////////////////////////////////////

* 3/10/17:
    - Initial commit. Much to clean up, much to streamline. More soon
        current state: parses and loads spreadsheet into db with no duplicate
        entries.
    - Cleaned up pep - 8 formatting, minor item ID matching debug
* 3/11/17
    - refactor for more sensible code flow, implemented functionality
        to update an existing database.
* 3/12/17
    - accounted for the databases' returning None in place of a tuple.
* 3/13/17
    - implemented check that allows us to push to the database entries that
        did not already exist.
* 3/14/17
    - implemented a check to make sure a result's link exists / is
        functional
    - implemented a "flag result" function to flag results with broken links for
        review
    - began refactor of existing code. Separated out the functionality of querying
        for company and product id, as well as converting federated and license_update
        fields from the human - readable string format to the tinyint format used by
        mysql to represent booleans
* 3/15/17 - early 3/16/17
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
    - cleaned up check - spreadsheet script for push to refstack repo for further testing
* 3/21/17
    - started refactor of sync - db script for better handling of edge cases and greater
        processing speed
* 3/24/17
    - removed header lines from input, debugged ticket data entry. still buggy. This is
        still buggy
        when I search for the appropriate id number, the search returns 0.
* 3/25/17
    - simplified code through reorganization. simplifying in an attempt to reduce edge
        cases and therefore room for db addition error. this is a result of anomalies in
        refstack result addition process
* 3/27/17
    - eliminated bug which caused the script to fail in the endeavor of pushing very
        very incomplete entries back into the database.
* 3/28/17-3/31/17
    - created new (but similar) script for the internal refstack db specifically that checks to
      see if there is data in the internal refstack server that the script is being run against,
      then if that data exists, verifies the validity of the result link, updates a few fields
      in the internal db, and then updates the "verified" field in the "test" field
    - this can likely be expanded (if needed) to check whether the product has passed testing for
      the specified guideline

//////////////////////////////////// Current Status & Functionality /////////////////////////////

* sync-db.py
  - populates db if db does not exist
  - updates db based on existing records that have been changed
  - adds new records for product pairs that have been recently added to the spreadsheet
  - checks links and flags test results whose links are broken / nonexistent
  - pushes entries with updated flags and comments back to the spreadsheet.
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

////////////////////////////////////////Coming Soon ///////////////////////////////////////////////

* sync-db.py
  - planning to refactor for increased simplicity / less code replication(IN PROGRESS)
  - set up a deployment script for the internal vendor licensing db that sync-db interacts
    with
  - make go in docker
* check-spreadsheet.py
  - no new planned features. This portion of the project is likely complete.
* update-rs-db.py
  - ensure that all features are working correctly.
  - perhaps verify that the result has passed testing for its associated guideline?
