#!/usr/bin/python3.5
import argparse
import pymysql
import sys
import api


def process_flags(cursor, results):
    if results.name is None or results.name is " ":
        print("No valid product name provided. Exiting process.")
        sys.exit()
    else:
        name = results.name
    if not results.product_type or results.product_type is None or results.product_type is " ":
        _type = -1
    else:
        _type = results.product_type
    if not results.release or results.release is None or results.release is " ":
        release = ""
    else:
        release = results.release
    if not results.federated or results.release is None or results.release is "0":
        federated = 0
    else:
        federated = 1
    if not results.company or results.company is None or results.company is " ":
        print("No valid company name provided. Exiting process")
        sys.exit()
    else:
        companyId = api.getCompanyId(cursor, results.company)
    return name, _type, release, federated, companyId


def create_product(cursor, db, name, _type, release, federated, companyId):
    if not api.dupChk("product", "name", name, cursor):
        query = "INSERT INTO product(name, _type, _release, federated, company_id) VALUE('%s', '%d', '%s', '%d', '%d')" % (
            name, int(_type), release, int(federated), int(companyId))
        cursor.execute(query)
        db.commit()
    else:
        print("The Product " + name + " already exists within the database")


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-n", "--name", type=str, action="store",
                        required=True, help="Product Name")
    parser.add_argument("-t", "--product_type", type=int, action="store",
                        help="Product Type: 0 = distribution, 1 = public, 2 = private")
    parser.add_argument("-r", "--release", type=str,
                        action="store", help="Product Name")
    parser.add_argument("-f", "--federated", type=int,
                        action="store", help="Federated Identity")
    parser.add_argument("-c", "--company", type=str, action="store",
                        required=True, help="Associated Company")
    results = parser.parse_args()
    name, _type, release, federated, companyId = process_flags(cursor, results)
    create_product(cursor, db, name, _type, release, federated, companyId)
    db.close()


main()
