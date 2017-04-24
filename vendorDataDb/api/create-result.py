#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import api


def process_flags(cursor, results):
    if not results.result - link or results.result - link is " ":
        print("No RefStack result link provided. Exiting.")
        sys.exit()
    else:
        if api.linkChk(results.result - link):
            resultlink = results.result - link
            _id = resultlink.split(",")[-1]
        else:
            print("Cannot add broken result link. Exiting.")
            sys.exit()
    if not results.product - name or results.product - name is " ":
        print("No product name provided. Exiting.")
        sys.exit()
    else:
        productname = results.result - link
        productId = api.getProductId(cursor, name)
    if not results.ticket - link or results.ticket - link is " ":
        tikID = "NULL"
    else:
        tik_link = results.ticket - link
        tikId = tik_link.split("/")[-1]
    if not results.guideline or results.guideline is " ":
        guideline = "NULL"
    else:
        guideline = results.guideline
    return _id, resultlink, productId, tikId, guideline


def create_result(cursor, db, _id, result, refstack, productId, tikId, guideline):
    if not dupChk("result", "id", _id):
        query = "INSERT INTO result(id, tik_id, guideline, _product_id_, refstack) VALUES('%s', '%s', '%s', '%d', '%s')" % (
            _id, tikId, guideline, productId, refstack)
        cursor.execute(query)
        db.commit()
    else:
        print("The result associated with the ID " + _id + "already exists")


def main():
    db, cursor, parser = api.connect)
    parser.add_argument("-r", "--result-link", type = str,
                        action = "store", required = True, help = "Refstack result link")
    parser.add_argument("-p", "--product-name", type = str, action = "store",
                        required = True, help = "Product associated with this set of test results")
    parser.add_argument("-t", "--ticket-link", type = str,
                        action = "store", help = "Associated ticket link")
    parser.add_argument("-g", "--guideline", type = str,
                        action = "store", help = "Associated Defcore guideline")
    results=parser.parse_args()
    _id, refstack, productId, tikId, guideline=process_flags(cursor, results)
    create_result(cursor, db, _id, result, refstack,
                  productId, tikId, guideline)
    db.close()
