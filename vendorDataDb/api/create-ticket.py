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
    if not results.product - name or results.product - name is " ":
        print("No valid product provided. Exiting process.")
        sys.exit()
    else:
        productName = results.product - name
        productId = getProductId(productName)
    return ticket, tikId, productId


def create_ticket(cursor, db, tik_link, tikId, productId):
    if not dupChk("ticket", "link", tik_link):
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
    parser.add_argument("-p", "--product-name", type=str,
                        action="store", required=True, help="Product Name")
    results = parser.parse_args()
    tik_link, tikId, productId = process_flags(cursor, results)
    create_contact(cursor, db, tik_link, tikId, productId)
    db.close()


main()
