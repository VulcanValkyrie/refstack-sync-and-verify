#!/usr/bin/python3.5
import argparse
import pymysql
import sys
import api


def process_flags(results):
    if results.name is None or results.name is " ":
        print("No valid product name provided. Exiting process.")
        sys.exit()
    else:
        name = results.name
    if not results.product - type or results.product - type is None or results.product - type is " ":
        _type = "NULL"
    else:
        _type = results.product - type
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
        companyId = api.getCompanyId(cursor, company)
    return name, _type, release, federated, companyId


def create_product(cursor, db, name, _type, release, federated, companyId):
    if not dupChk("product", "name", name):
        query = "INSERT INTO product(name, _type, _release, federated, company_id, _updated) VALUE('%s', '%d', '%s', '%d', '%d', '%d')" % (
            product_name, int(_type), _release, int(federated), int(company_id), int(update))
        cursor.execute(query)
        db.commit()
    else:
        print("The Product " + name + " already exists within the database")


def main():
    db, cursor, parser = api.connect()
    parser.add_argument("-n", "--n", type=str, action="store",
                        required=True, help="Product Name")
    parser.add_argument("-t", "--product-type", type=int, action="store",
                        help="Product Type: 0 = distribution, 1 = public, 2 = private")
    parser.add_argument("-r", "--release", type=str,
                        action="store", help="Product Name")
    parser.add_argument("-f", "--federated", type=int,
                        action="store", help="Federated Identity")
    parser.add_argument("-c", "--company", type=str, action="store",
                        required=True, help="Associated Company")
    results = parser.parse_args()
    name, _type, release, federated, companyId = process_flags(results)
    create_product(cursor, db, name, _type, release, federated, companyId)


main()
