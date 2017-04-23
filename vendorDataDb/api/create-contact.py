#!/usr/bin/python3.5
import argparse
import pymysql
import sys
import create


def create_contact(cursor, db, name, email):
    if not dupChk("contact", "name", name):
        query = "INSERT INTO company(name, email) VALUES('%s', '%s')" % (
            name, email)
        cursor.execute(query)
        db.commit()
    else:
        print(name + "already exists within the database.")

def process_flags(results):
    if results.name is None or results.name is " ":
        print("No valid contact name provided. Exiting process.")
        sys.exit()
    else:
        name = results.name
    if results.email is None or results.name is " ":
        email = "No Valid email on file."
    else:
        email = results.email
    return name, email


def main():
    db, cursor, parser = create.connect()
    parser.add_argument("-n", "--name", type=str,
                        action="store", required=True, help="Contact Name")
    parser.add_argument("-m", "--mail", type=str,
                        action="store", required=True, help="Contact Email")
    results = parser.parse_args()
    name, email = process_flags(results)
    create_contact(cursor, db, name, email)


main()
