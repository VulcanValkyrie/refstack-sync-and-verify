#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import api


def process_flags(cursor, results):
    if not results.license - link or results.license - link is " ":
        print("No valid license link provided. Exiting process.")
        sys.exit()
    else:
        licenseLink = results.license - link
        _id = licenseLink.split("/")[-1]
    if not results.type or results.type is " ":
        _type = "NULL"
    else:
        _type = results.type
    if not results.date or results.date is " ":
        print("No valid date provided. Exiting process.")
        sys.exit()
    else:
        _date = results.date
    if not results.result - id or results.result - id is " ":
        print("No viable result ID provided. Exiting Process")
        sys.exit()
    else:
        if not api.linkChk("https://refstack.openstack.org/api/v1/results/" + results.result - id):
            print("This is not a valid result, and, as such, cannot be used for licensing purposes. Exiting process.")
            sys.exit()
        elif not dupChk("result", "id", results.result - id, cursor):
            print("The result with an ID of " + results.result - id +
                  " is not recorded in the database. Please add this result and try again.")
            sys.exit()
        else:
            resultId = results.result - id
    return _id, licenseLink, resultId, _type, _date


def create_license(cursor, db, _id, licenseLink, resultId, _type, _date):
    if not dupChk("license", "id", _id):
        query = "INSERT INTO license(id, _link, result_id, _type, _date) VALUES('%s', '%s', '%s', '%s', '%s')" % (
            _id, licenseLink, resultId, _type, _date)
        cursor.execute(query)
        db.commit()
    else:
        print("The license associated with the license id " +
              _id + " already exists within the database.")


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-l", "--license-link", type=str,
                        action="store", required=True, help="License link")
    parser.add_argument("-t", "--type", type=str,
                        action="store", help="product type")
    parser.add_argument("-d", "--date", type=str,
                        action="store", required=True, help="License Date")
    parser.add_argument("-r", "--result-id", type=str, action="store",
                        required=True, help="Passing result ID associated with this license")
    results = parser.parse_args()
    _id, licenseLink, resultId, _type, _date = process_flags(cursor, result)
    create_license(cursor, db, _id, licenseLink, resultId, _type, _date)
    db.close()


main()
