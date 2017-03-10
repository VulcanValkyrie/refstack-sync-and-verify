#!/usr/lib/python3

import csv
import gspread
import pymysql
import subprocess
from oauth2client.service_account import ServiceAccountCredentials


def get_csv():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'gcreds.json', scope)
    doc_id = "<doc id>"
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(doc_id)
    for i, worksheet in enumerate(spreadsheet.worksheets()):
        # filename = 'results_worksheet' + str(i) + '.csv' if many
        filename = 'results_worksheet.csv'
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(worksheet.get_all_values())
        return filename  # deal with the case of muliple worksheets later


def empty_chk():
    db = pymysql.connect("<db host>", "<user>", "<password>", "<db>")
    cursor = db.cursor()
    results = cursor.execute("""SELECT * from product limit 1""")
    if not results:
        return 1
    else:
        return 0


def split_entry(guideline, refstack_link, ticket_link, lic_date):
    guide2 = guideline.split()[1]
    guideline = guideline.split()[0]
    rs_link2 = refstack_link.split()[1]
    refstack_link = refstack_link.split()[0]
    tiklink2 = ticket_link.split()[1]
    ticket_link = ticket_link.split()[0]
    date2 = lic_date.split()[1]
    lic_date = lic_date.split()[0]
    return guideline, guide2, refstack_link, rs_link2, ticket_link, tiklink2, lic_date, date2


def pop_db(filename):  # first separate off a line, then push each line to its relevant place in the db
    # first going to open up the file we created when we pulled from the database
    # and chop it up to get the info
    with open(filename, 'r') as f:
        # check if db is empty
        status = empty_chk()
        for line in f:
            company_name = line.split(',')[0]
            prod_name = line.split(',')[1]
            # deal with type in later iterations
            # same with region
            guideline = line.split(',')[4]
            # deal with component later
            reported_rel = line.split(',')[6]
            passed_rel = line.split(',')[7]
            federated = line.split(',')[8]
            refstack_link = line.split(',')[9]
            ticket_link = line.split(',')[10]
            lic_date = line.split(',')[12]
            upd_status = line.split(',')[13]
            contact = line.split(',')[14]
            lic_link = line.split(',')[15]
            # deal with active later
            # before i do anything else, i am going to check to see
            # if we need to split some lines
            if not prod_name or "Company Name" in company_name:
                continue
            if(len(guideline) > 9):
                print ("this line needs to be split")
                guideline, guide2, refstack_link, rs_link2, ticket_link, tiklink2, lic_date, date2 = split_entry(
                    guideline, refstack_link, ticket_link, lic_date)
                if status == 1:
                    add_entry(company_name, prod_name, guide2, reported_rel, passed_rel,
                              federated, rs_link2, tiklink2, date2, upd_status,
                              contact, lic_link)
            if status == 1:
                # push data to db
                add_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
                          federated, refstack_link, ticket_link, lic_date, upd_status,
                          contact, lic_link)


def dup_chk(cursor, table, specifier):
    if "company" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM company WHERE name = %s GROUP BY Name", (specifier,))
    if "contact" in table:
        cursor.execute(
            "SELECT email, COUNT(*) FROM contact WHERE email = %s GROUP BY Name", (specifier,))
    if "product" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM product WHERE name = %s GROUP BY Name", (specifier,))
    if "ticket" in table:
        cursor.execute(
            "SELECT tik_link, COUNT(*) FROM ticket WHERE tik_link = %s GROUP BY tik_link", (specifier,))
    if "result" in table:
        cursor.execute(
            "SELECT refstack, COUNT(*) FROM result WHERE refstack = %s GROUP BY refstack", (specifier,))
    if "license" in table:
        cursor.execute(
            "SELECT result_id, COUNT(*) FROM license WHERE result_id = %s GROUP BY result_id", (specifier))
    row_count = cursor.rowcount
    if row_count == 0:
        return False
    return True


def add_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
              federated, refstack_link, ticket_link, lic_date, upd_status,
              contact, lic_link):
    if 'yes' in federated:
        fed = 1
    else:
        fed = 0
    if 'yes' in upd_status:
        upd = 1
    else:
        upd = 0
    db = pymysql.connect("localhost", "root", "password", "refstack_status")
    cursor = db.cursor()
    if not (dup_chk(cursor, "company", company_name)):
        cursor.execute("INSERT INTO company(NAME) VALUES('%s')" %
                       (company_name))
        db.commit()
    cursor.execute(
        "SELECT id FROM company WHERE name = '%s' IS NOT NULL LIMIT 1" % (company_name))
    company_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "contact", contact)):
        cursor.execute("INSERT INTO contact(email, company_id) VALUES('%s', '%d')" % (
            contact, company_id))
    if not(dup_chk(cursor, "product", prod_name)):
        cursor.execute("INSERT INTO product(name,  _release, federated, company_id, _update) VALUES('%s', '%s', '%d', '%d', '%d')" % (
            prod_name, reported_rel, fed, company_id, upd))
    cursor.execute("SELECT id from product WHERE name = '%s' AND _release = '%s' IS NOT NULL" % (
        prod_name, reported_rel))
    product_id = cursor.fetchone()[0]
    if not dup_chk(cursor, "ticket", ticket_link) and not ' ' in ticket_link:
        cursor.execute("INSERT INTO ticket(tik_link, product_id) VALUES('%s', '%s')" % (
            ticket_link, product_id))
    cursor.execute("SELECT id FROM ticket WHERE tik_link = '%s' AND product_id = '%d' IS NOT NULL" % (
        ticket_link, product_id))
    tik_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "result", refstack_link)) and refstack_link:
        cursor.execute("INSERT INTO  result(refstack, tik_id, guideline, _product_id_) VALUES('%s','%d', '%s', '%d')" % (
            refstack_link, tik_id, guideline, product_id))
    cursor.execute("SELECT id FROM result WHERE refstack = '%s' IS NOT NULL AND _product_id_ = '%d' IS NOT NULL" % (
        refstack_link, product_id))
    result_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "license", result_id)):
        cursor.execute("INSERT INTO license(result_id, date) VALUES('%d', '%s')" % (
            result_id, lic_date))
    db.commit()


filename = get_csv()
pop_db(filename)
