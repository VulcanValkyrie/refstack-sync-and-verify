#!/usr/bin/python3.5
import pymysql
import argparse
import sys


def dupChk(table, keytype, keyval, cursor):
    query = "SELECT COUNT(*) FROM %s WHERE %s = '%s'" % (table,
                          keytype, keyval)
    cursor.execute(query)
    rowcount = cursor.rowcount
    if rowcount != 0:
        return True
    else:
        return False


def process_flags(results):
    if results.name is None:
        print("No company name listed. Exiting.")
        sys.exit()
    else:
        name = results.name
    return name


def create_company(cursor, company_name):
    if not dupChk("company", "name", company_name):
        query = "INSERT INTO company(name) VALUES('%s')" % (company_name)
        cursor.execute(query)
    else:
        print("The company " + company_name +
              " already exists within the database.")
    db.commit()


def main():
    db = pymysql.connect("<MySQL db server>", "<user>",
                         "<password>", "vendorData")
    cursor = db.cursor()
    parser = argparse.ArgumentParser("read an entry from the vendorData db")
    parser.add_argument("-n", "--name", type=str, action="store", required=True, help="Company Name"
    results=parser.parse_args()
    name=process_flags(results)
    create_company(cursor, name)

main()
