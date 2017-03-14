#!/usr/lib/python3.5

import csv
import gspread
import pymysql
import subprocess
from oauth2client.service_account import ServiceAccountCredentials


def get_csv():
    scope = ['https://spreadsheets.google.com/feeds']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        '<credentials json file>', scope)
    doc_id = "<document id>"
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(doc_id)
    for i, worksheet in enumerate(spreadsheet.worksheets()):
        filename = 'results_worksheet.csv'
        with open(filename, 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(worksheet.get_all_values())
        return filename  # deal with the case of muliple worksheets later


def empty_chk(cursor):
    results = cursor.execute("""SELECT * from product limit 1""")
    if not results:
        return True
    else:
        return False


def split_entry(guideline, refstack_link, ticket_link, lic_date):
    guide2 = guideline.split()[1]
    guideline = guideline.split()[0]
    rs_link2 = refstack_link.split()[1]
    refstack_link = refstack_link.split()[0]
    tiklink2 = ticket_link.split()[1]
    ticket_link = ticket_link.split()[0]
    date2 = lic_date.split()[1]
    lic_date = lic_date.split()[0]
    return guideline, guide2, refstack_link, rs_link2, ticket_link, tiklink2,\
        lic_date, date2


def get_entry(line):
    company_name = line.split(',')[0]
    prod_name = line.split(',')[1]
    # deal with type later(?)
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
    return company_name, prod_name, guideline, reported_rel, passed_rel,\
        federated, refstack_link, ticket_link, lic_date, upd_status,\
        contact, lic_link


def pop_db(filename):
    if not prod_name in company_name:
        return None
    if(len(guideline) > 9):
        print ("this line needs to be split")
        guideline, guide2, refstack_link, rs_link2, ticket_link,\
            tiklink2, lic_date, date2 = split_entry(
                guideline, refstack_link, ticket_link, lic_date)
        add_entry(company_name, prod_name, guide2, reported_rel,
                  passed_rel, federated, rs_link2, tiklink2, date2,
                  upd_status, contact, lic_link)
        # push data to db
    add_entry(company_name, prod_name, guideline, reported_rel,
              passed_rel, federated, refstack_link, ticket_link,
              lic_date, upd_status, contact, lic_link)


def dup_chk(cursor, table, specifier):
    if "company" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM company WHERE name = '%s' GROUP BY name" % (specifier))
    if "contact" in table:
        cursor.execute(
            "SELECT email, COUNT(*) FROM contact WHERE email = '%s' GROUP BY email" % (specifier,))
    if "product" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM product WHERE name = '%s' GROUP BY name" % (specifier,))
    if "ticket" in table:
        cursor.execute(
            "SELECT tik_link, COUNT(*) FROM ticket WHERE tik_link = '%s' GROUP BY tik_link" % (specifier,))
    if "result" in table:
        cursor.execute(
            "SELECT refstack, COUNT(*) FROM result WHERE refstack = '%s' GROUP BY refstack" % (specifier,))
    if "license" in table:
        cursor.execute(
            "SELECT result_id, COUNT(*) FROM license WHERE result_id = '%s' GROUP BY result_id" % (specifier))
    row_count = cursor.rowcount
    if row_count == 0:
        return False
    return True


def push_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
               federated, refstack_link, ticket_link, lic_date, upd_status,
               contact, lic_link, cursor, db):
    if 'yes' in federated:
        fed = 1
    else:
        fed = 0
    if 'yes' in upd_status:
        upd = 1
    else:
        upd = 0
    if not (dup_chk(cursor, "company", company_name)):
        cursor.execute("INSERT INTO company(NAME) VALUES('%s')" %
                       (company_name))
    cursor.execute(
        "SELECT id FROM company WHERE name = '%s'" % (company_name))
    company_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "contact", contact)):
        cursor.execute("INSERT INTO contact(email, company_id) VALUES('%s', '%d')" % (
            contact, company_id))
    if not(dup_chk(cursor, "product", prod_name)):
        cursor.execute("INSERT INTO product(name,  _release, federated, company_id, _update) VALUES('%s', '%s', '%d','%d', '%d')" % (
            prod_name, reported_rel, fed, company_id, upd))
    cursor.execute("SELECT id from product WHERE name='%s' AND _release='%s' IS NOT NULL" % (
        prod_name, reported_rel))
    product_id = cursor.fetchone()[0]
    if not dup_chk(cursor, "ticket", ticket_link) and ' 'not in ticket_link:
        cursor.execute("INSERT INTO ticket(tik_link, product_id) VALUES('%s','%s')" % (
            ticket_link, product_id))
    cursor.execute("SELECT id FROM ticket WHERE tik_link='%s' AND product_id='%d' IS NOT NULL" % (
        ticket_link, product_id))
    tik_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "result", refstack_link)) and refstack_link:
        cursor.execute("INSERT INTO  result(refstack, tik_id, guideline, product_id_) VALUES('%s', '%d', '%s', '%d')" % (
                       refstack_link, tik_id, guideline, product_id))
    cursor.execute("SELECT id FROM result WHERE refstack='%s' IS NOT NULL AND _product_id_='%d' IS NOT NULL" % (refstack_link,
                                                                                                                product_id))
    result_id = cursor.fetchone()[0]
    if not(dup_chk(cursor, "license", result_id)):
        cursor.execute("INSERT INTO license(result_id, date) VALUES('%d', '%s')" % (
            result_id, lic_date))
    db.commit()


def update_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
                 federated, refstack_link, ticket_link, lic_date,  contact,
                 lic_link, cursor, db):
    cursor.execute("SELECT id from product WHERE name='%s'" % (prod_name))
    product_id = cursor.fetchone()
    if product_id is not None:
        product_id = product_id[0]
    cursor.execute("SELECT id from company WHERE name='%s'" % (company_name))
    company_id = cursor.fetchone()
    if not "None" in company_id:
        company_id = company_id[0]
    # guideline table updates
    cursor.execute(
        "SELECT guideline FROM result WHERE guideline ='%s'" % (guideline))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not guideline in to_chk:
            cursor.execute("UPDATE result SET guideline = '%s' WHERE product_id_ = '%s' AND refstack = '%s'" % (
                guideline, product_id, refstack_link))
    cursor.execute("SELECT refstack FROM result WHERE guideline = '%s' AND _product_id_ = '%s'" % (
        guideline, product_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not refstack_link in to_chk:
            cursor.execute("UPDATE result SET refstack = '%s' WHERE product_id_ = '%s' AND guideline = '%s'" % (
                refstack_link, product_id, guideline))
    # now we update our contact table
    cursor.execute(
        "SELECT email FROM contact WHERE company_id ='%s'" % (company_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not contact in to_chk:
            cursor.execute("UPDATE contact SET email = '%s' WHERE company_id = '%s'" % (
                contact, company_id))
    # now update the product table
    cursor.execute("SELECT _release FROM product WHERE company_id ='%s' AND name = '%s'" % (
        company_id, prod_name))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not reported_rel in to_chk:
            cursor.execute("UPDATE product SET _release ='%s' WHERE company_id = '%s' and name = '%s'" % (
                reported_rel, company_id, prod_name))
    cursor.execute("SELECT federated FROM product WHERE company_id ='%s' AND name = '%s'" % (
        company_id, prod_name))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if "yes" in federated:
            federated = 1
        else:
            federated = 0
        if to_chk != federated:
            cursor.execute("UPDATE product SET federated ='%s' WHERE company_id = '%s' and name = '%s'" % (
                federated, company_id, prod_name))
    # now update the ticket table
    cursor.execute(
        "SELECT tik_link FROM ticket WHERE product_id ='%s'" % (product_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not ticket_link in to_chk:
            cursor.execute("UPDATE ticket SET tik_link = '%s' WHERE product_id = '%s'" % (
                ticket_link, product_id))
    # get a result link
    cursor.execute(
        "SELECT id FROM result WHERE _product_id_ ='%s'" % (product_id))
    result_id = cursor.fetchone()
    if result_id is not None:
        result_id = result_id[0]
    # lastly, update the license table
    cursor.execute(
        "SELECT link FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if to_chk and not lic_link in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE product_id = '%s'" % (
                lic_link, product_id))
    cursor.execute(
        "SELECT date FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if not lic_date in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE product_id = '%s'" % (
                lic_date, product_id))
    db.commit()


def new_chk(company_name, prod_name, cursor):
    # this checks to see if the entry already exists. If it does not, the
    # function returns a status of true, as in "entry is new"
    cursor.execute(
        "SELECT COUNT(*) FROM company WHERE name = '%s'" % (company_name))
    company = cursor.fetchone()[0]
    cursor.execute(
        "SELECT COUNT(*) FROM product WHERE name = '%s'" % (prod_name))
    product = cursor.fetchone()[0]
    if company == 1 and product == 1:
        return True
    else:
        return False


filename = get_csv()
db = pymysql.connect("<MySQL db server>", "<user>", "<password>", "MySQL db")
cursor = db.cursor()
empty_db = empty_chk(cursor)
with open(filename) as r:
    next(r)
    for line in r:
        company_name, prod_name, guideline, reported_rel, passed_rel,\
            federated, refstack_link, ticket_link, lic_date, upd_status,\
            contact, lic_link = get_entry(line)
        new_entry = new_chk(company_name, prod_name, cursor)
        # if the db is empty, of if this entry does not exist, push entry
        if empty_db or new_entry:
            push_entry(company_name, prod_name, guideline, reported_rel,
                       passed_rel, federated, refstack_link, ticket_link,
                       lic_date, upd_status, contact, lic_link, cursor, db)
        else:
            # now let's update existing entries
            update_entry(company_name, prod_name, guideline, reported_rel,
                         passed_rel, federated, refstack_link, ticket_link,
                         lic_date, contact, lic_link, cursor, db)
