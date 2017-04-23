#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import create


def create_company(cursor, db, company_name):
    if not dupChk("company", "name", company_name):
        query = "INSERT INTO company(name) VALUES('%s')" % (company_name)
        cursor.execute(query)
        db.commit()
    else:
        print("The company " + company_name +
              " already exists within the database.")


def process_flage(results):
    if results.name is None or results.name is " ":
        print("No valid contact name provided. Exiting process.")
        sys.exit()
    else:
        name - results.name
    return name


def main():
    db, cursor, parser = create.connect()
    parser.add_argument("-n", "--name", type=str,
                        action="store", required=True, help="Company Name")
    results = parser.parse_args()
    name = process_flags(results)
    create_company(cursor, db, name)


main()
