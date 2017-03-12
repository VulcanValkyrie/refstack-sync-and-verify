# refstack-sync-and-verify
working repository for a script that syncs and verifies a spreadsheet and a
MySQL contain refstack results

re: dependencies- this script requires a mysql db, the ability and the ability
to access google spread via their native auth. real docs to come; just getting
the basics set up.

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
