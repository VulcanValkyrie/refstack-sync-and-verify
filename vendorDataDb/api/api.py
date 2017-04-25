#!/usr/bin/python3.5
import pymysql
import argparse
import urllib.error
import urllib.request
import sys


def dupChk(table, keytype, keyval, cursor):
    query = "SELECT EXISTS(SELECT 1 FROM %s WHERE %s = '%s')" % (
        table, keytype, keyval)
    cursor.execute(query)
    rowcount = cursor.fetchall()
    rowcount = rowcount[0][0]
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
    try:
        db = pymysql.connect("<MySQL db server>", "<user>",
                             "<password>", "vendorData")
    except Exception as err:
        print("could not connect to database.")
        print(err)
        sys.exit()
    cursor = db.cursor()
    parser = argparse.ArgumentParser()
    return db, cursor, parser


def getCompanyId(cursor, company):
    if company is None or company is " ":
        sys.exit()
    query = "SELECT id FROM company where name = '%s'" % (company)
    cursor.execute(query)
    companyId = cursor.fetchone()
    if companyId is None or companyId is 0 or companyId is "":
        print("No matching organization found. Exiting.")
        sys.exit()
    else:
        companyId = companyId
    return companyId


def getProductId(cursor, name):
    if name is None or name is " ":
        sys.exit()
    query = "SELECT id FROM product where name = '%s'" % (name)
    cursor.execute(query)
    productId = cursor.fetchone()
    if productId is None or productId is 0:
        print("No matching product Id found. Exiting.")
        sys.exit()
    else:
        productId = productId[0]
    return productId
