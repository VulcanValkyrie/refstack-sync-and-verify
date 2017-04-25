#!/usr/bin/python3.5
import pymysql
import argparse
import sys
import api


def process_flags(cursor, results):
    if not results.ticket or results.ticket is " ":
        print("No valid ticket link provided. Exiting process.")
        sys.exit()
    else:
        ticket = results.ticket
        tikId = ticket.split("/")[-1]
    if not results.productName or results.productName is " ":
        print("No valid product provided. Exiting process.")
        sys.exit()
    else:
        productName = results.productName
        productId = api.getProductId(cursor, productName)
    return ticket, tikId, productId


def create_ticket(cursor, db, tik_link, tikId, productId):
    if not api.dupChk("ticket", "tik_link", tik_link, cursor):
        query = "INSERT INTO ticket(id, tik_link, product_id) VALUES('%s', '%s', '%d')" % (
            tikId, tik_link, productId)
        cursor.execute(query)
        db.commit()
    else:
        print("The ticket associated with the ID " + tikId + " already exists")


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-t", "--ticket", type=str,
                        action="store", required=True, help="Ticket Link")
    parser.add_argument("-p", "--productName", type=str,
                        action="store", required=True, help="Product Name")
    results = parser.parse_args()
    tik_link, tikId, productId = process_flags(cursor, results)
    create_ticket(cursor, db, tik_link, tikId, productId)
    db.close()


main()
