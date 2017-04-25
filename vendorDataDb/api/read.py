#!/usr/bin/python3.5
import pymysql
import argparse
import api

def read(table, keytype, keyval, cursor):
    query ="SELECT * FROM %s WHERE %s  = '%s'" % (table, keytype, keyval)
    #print(query)
    result = cursor.execute(query)
    if result is not None and result is not 0:
         results = cursor.fetchall()
         print(results)
    else:
        print(keytype + " " + keyval + " not found")


def dupChk(table, keytype, keyval, cursor):
    query = "SELECT COUNT(*) FROM %s WHERE %s = '%s'"%(table, keytype, keyval)
    cursor.execute(query)
    rowcount = cursor.rowcount
    if rowcount != 0:
        return True
    else:
        return False


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
    read(table, keytype, keyval, cursor)
     
main()
