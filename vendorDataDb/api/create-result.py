#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import api


def process_flags(cursor, results):
    if not results.resultLink or results.resultLink is " ":
        print("No RefStack result link provided. Exiting.")
        sys.exit()
    else:
        if api.linkChk(results.resultLink):
            resultlink = results.resultLink
            _id = resultlink.split("/")[-1]
        else:
            print("Cannot add broken result link. Exiting.")
            sys.exit()
    if not results.productName or results.productName is " ":
        print("No product name provided. Exiting.")
        sys.exit()
    else:
        productname = results.productName
        productId = api.getProductId(cursor, productname)
    if not results.ticketLink or results.ticketLink is " ":
        tikId = "NULL"
    else:
        tik_link = results.ticketLink
        tikId = tik_link.split("/")[-1]
    if not results.guideline or results.guideline is " ":
        guideline = "NULL"
    else:
        guideline = results.guideline
    return _id, resultlink, productId, tikId, guideline


def create_result(cursor, db, _id, refstack, productId, tikId, guideline):
    if not api.dupChk("result", "id", _id, cursor):
        query = "INSERT INTO result(id, tik_id, guideline, _product_id_, refstack) VALUES('%s', '%s', '%s', '%d', '%s')" % (
            _id, tikId, guideline, productId, refstack)
        cursor.execute(query)
        db.commit()
    else:
        print("The result associated with the ID " + _id + " already exists")


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-r", "--resultLink", type = str,
                        action = "store", required = True, help = "Refstack result link")
    parser.add_argument("-p", "--productName", type = str, action = "store",
                        required = True, help = "Product associated with this set of test results")
    parser.add_argument("-t", "--ticketLink", type = str,
                        action = "store", help = "Associated ticket link")
    parser.add_argument("-g", "--guideline", type = str,
                        action = "store", help = "Associated Defcore guideline")
    results=parser.parse_args()
    _id, refstack, productId, tikId, guideline=process_flags(cursor, results)
    create_result(cursor, db, _id, refstack,
                  productId, tikId, guideline)
    db.close()

main()
