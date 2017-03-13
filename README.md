# refstack-sync-and-verify
working repository for a script that syncs and verifies a spreadsheet and a
MySQL contain refstack results

re: dependencies- this script requires a mysql db, the ability and the ability
to access google spread via their native auth. real docs to come; just getting
the basics set up.

note: for the time being, I am disregarding the line length requirement of
pep-8. I will remedy that soon, but for the time being, I am leaving it as is

//////////////////////////Commit History & Progress///////////////////////////

* 3/10/17: 
  - Initial commit. Much to clean up, much to streamline. More soon
    current state: parses and loads spreadsheet into db with no duplicate
    entries.
  - Cleaned up pep-8 formatting, minor item ID matching debug
* 3/11/17
  - refactor for more sensible code flow, implemented functionality
    to update an existing database.
    * still a bit of debugging to do on this; not yet in fully working
      state
* 3/12/17
  - accounted for the databases' returning None in place of a tuple.


//////////////////////Current Status & Functionality///////////////////////////

* populates db if db does not exist
* updates db based on existing records that have been changed

////////////////////////////Coming Soon//////////////////////////////////////

* link checking
* adding new single/multiple entries into an existing database
