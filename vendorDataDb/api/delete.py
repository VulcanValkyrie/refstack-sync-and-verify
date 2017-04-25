#!/usr/bin/python3.5
import pymysql
import argparse
import api

def delete(table, keytype, keyval, cursor, db):
    query = "SELECT * from %s WHERE %s = '%s'" % (table, keytype, keyval)
    result = cursor.execute(query)
    if result is not None and result is not 0:
        results = cursor.fetchall()
        print("Results found: ")
        print(results)
        confirm = input("are you sure you want to remove this record from the db? [y/N]")
        if confirm is 'y' or confirm is 'Y':
           query = "DELETE FROM %s WHERE %s = '%s'" % (table, keytype, keyval)
           cursor.execute(query)
           print("Entry deleted.")
           db.commit()

    else: 
        print("No such entry exists.")

def process_flags(results):
    if results.table is None:
        table = "N/A"
    else:
        table = results.table
    if results.keytype is None:
        keytype = "N/A"
    else:
        keytype = results.keytype
    if results.keyvalue is None:
        keyval = "N/A"
    else:
        keyval = results.keyvalue
    return table, keytype, keyval


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-t", "--table", type=str, action="store", required=True, help="table to search for the desired data")
    parser.add_argument("-kt", "--keytype", type=str, action="store", required=True, help="attribute to search by")
    parser.add_argument("-kv", "--keyvalue", type=str, action="store", required=True, help="attribute value") 
    results = parser.parse_args()
    table, keytype, keyval = process_flags(results)
    delete(table, keytype, keyval, cursor, db)
    db.close()
main()
