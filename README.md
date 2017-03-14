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
* 3/4/17
  - implemented a check to make sure a result's link exists/is
    functional
  - implemented a "flag result" function to flag results with broken links for
    review
  - began refactor of existing code. Separated out the functionality of querying
    for company and product id, as well as converting federated and license_update
    fields from the human-readable string format to the tinyint format used by
    mysql to represent booleans

////////////////////////////////////Current Status & Functionality//////////////////////////////////////////////

* populates db if db does not exist
* updates db based on existing records that have been changed
* adds new records for product pairs that have been recently added to the spreadsheet
* checks links and flags test results whose links are broken/nonexistent

////////////////////////////////////////////////Coming Soon///////////////////////////////////////////////////////

*  planning to refactor for increased simplicity/less code replication
* "pull entry" function that gathers entries from the contents of the DB
* "write to csv" functionality to populate a csv full of our updated results
* "push csv" functionality to return updated data to source, thus completing the sync
