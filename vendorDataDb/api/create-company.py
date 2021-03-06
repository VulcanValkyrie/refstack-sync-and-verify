#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import api


def create_company(cursor, db, company_name):
    if not api.dupChk("company", "name", company_name, cursor):
        query = "INSERT INTO company(name) VALUES('%s')" % (company_name)
        cursor.execute(query)
    else:
        print("The company " + company_name +
              " already exists within the database.")
    db.commit()


def process_flags(results):
    if results.name is None or results.name is " ":
        print("No valid contact name provided. Exiting process.")
        sys.exit()
    else:
        name = results.name
    return name


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-n", "--name", type=str,
                        action="store", required=True, help="Company Name")
    results = parser.parse_args()
    name = process_flags(results)
    create_company(cursor, db, name)
    db.close()


main()
