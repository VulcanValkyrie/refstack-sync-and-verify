#!/usr/bin/python3.5
import pymysql
import argparse
import urllib.error
import urllib.request


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
    if results.table is None:
        table = "N/A"
    else:
        table = results.table
    return table


def linkChk(link):
    if link is None or not link:
        return False
    try:
        if " " in link:
            return False
        response = urllib.request.urlopen(link)
        if response.geturl() == link:
            return True
    except urllib.error.HTTPError as err:
        return False


def connect():
    db = pymysql.connect("<MySQL db server>", "<username>",
                         "<password>", "vendorData")
    cursor = db.cursor()
    parser = argparse.ArgumentParser()
    return db, cursor, parser


def getCompanyId(cursor, company):
    if company is None or company is " ":
        sys.exit()
    query = "SELECT id FROM company where name = '%s'" % (company)
    companyId = cursor.execute(query)
    if companyId is None or companyId is 0 or companyId is "":
        print("No matching organization found. Exiting.")
        sys.exit()
    else:
        companyId = companyId[0]
    return companyId


def getProductId(cursor, name):
    if name is None or name is " ":
        sys.exit()
    query = "SELECT id FROM company where name = '%s'" % (name)
    productId = cursor.execute(query)
    if productId is None or productId is 0:
        print("No matching product Id found. Exiting.")
        sys.exit()
    else:
        productId = productId[0]
    return productId
