#!/usr/bin/python3.5
import argparse
import pymysql
import sys
import api

def create_contact(cursor, db, name, email, companyId):
    if not api.dupChk("contact", "name", name, cursor):
        query = "INSERT INTO contact(name, email, company_id) VALUES('%s', '%s', '%s')" % (name, email, companyId)
        cursor.execute(query)
    else:
        print(name + "already exists within the database.")
    db.commit() 

def process_flags(results, cursor):
    if results.name is None or results.name is " ":
        print("No valid contact name provided. Exiting process.")
        sys.exit()
    else:
        name = results.name
    if results.mail is None or results.mail is " ":
        email = "No Valid email on file."
    else:
        email = results.mail
    if results.company is not None and results.company is not " ":
        companyName = results.company
        companyId = api.getCompanyId(cursor, companyName)
    return name, email, companyId


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-n", "--name", type=str, action="store", required=True, help="Contact Name")
    parser.add_argument("-m", "--mail", type=str, action="store", required=True, help="Contact Email")
    parser.add_argument("-c", "--company", type=str, action="store", required=True, help="Affiliated Company Name")
    results = parser.parse_args()
    name, email, companyId = process_flags(results, cursor)
    create_contact(cursor, db, name, email, companyId)
    db.close()

main()
