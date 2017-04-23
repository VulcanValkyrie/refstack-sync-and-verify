#!/usr/bin/python35
import gspread
import pymysql
import subprocess
import urllib.request
import urllib.error
import sys
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import *


def emptyChk(cursor):
    results = cursor.execute("""SELECT * from product limit 1""")
    if not results:
        return True
    else:
        return False


def newChk(company_name, prod_name, cursor):
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


def getCompanyId(cursor, company_name):
    cursor.execute("SELECT id FROM company WHERE name = '%s'" % (company_name))
    company_id = cursor.fetchone()
    if company_id is not None:
        company_id = company_id[0]
    else:
        company_id = 0
    return company_id


def getProductId(cursor, product_name):
    cursor.execute("SELECT id FROM product WHERE name = '%s'" % (product_name))
    product_id = cursor.fetchone()
    if product_id is not None:
        product_id = product_id[0]
    else:
        product_id = 0
    return product_id


def getTikId(ticket_link):
    if ticket_link and ticket_link != "":
        tik_id = ticket_link.split("/")[-1]
    else:
        tik_id = "N/A"
    return tik_id


def splitEntry(guideline, component, passed_rel, reported_rel):
    guidelines = []
    components = []
    passed_rels = []
    reported_rels = []
    guidelines = guideline.replace("\n", " ").replace("\r", " ").split()
    components = component.replace("\n", " ").replace("\r", " ").split()
    passed_rels = passed_rel.replace("\n", " ").replace("\r", " ").split()
    reported_rels = reported_rel.replace("\n", " ").replace("\r", " ").split()
    return guidelines, components, passed_rels, reported_rels


def linksChk(links, linect):
    if links is None or not links:
        return False
    if linect == 2:
        return True  # not an error, just not a link
    status = False
    for x in links:
        try:
            if " " in x:
                status = False
            response = urllib.request.urlopen(x)
            if response.geturl() == x:
                status = True
        except urllib2.error.HTTPError as err:
            status = False
    return status


def fixLink(link):
    links = []
    newurls = []
    if " " in link or not link or link == '':
        return None
    links = link.replace("\n", " ").replace("\r", " ").split(" ")
    for x in links:
        try:
            baseDomain = x.split('/')[2]
            testId = x.split('/')[-1]
            newurl = "https://" + str(baseDomain) + \
                "/api/v1/results/" + str(testId)
            newurls.append(newurl)
        except Exception:
            continue
    return newurls


def splitTiks(ticket_link):
    links = []
    links = ticket_link.replace("\n", " ").replace("\r", " ").split()
    return links


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


def pushEntry(company_name, prod_name, guideline, reported_rel, passed_rel, result_links,
              federated, _type, ticket_link, lic_date, upd_status, lic_link, cursor, db):
    federated = fedChk(federated)
    upd_status = updateLicenseChk(upd_status)
    if not dupChk("company", "name", company_name, cursor):
        cursor.execute("INSERT INTO company(NAME) VALUES('%s')" %
                       (company_name))
    db.commit()
    cursor.execute(
        "SELECT id FROM company WHERE name = '%s'" % (company_name))
    company_id = getCompanyId(cursor, company_name)
    if company_id is None:
        return
    if "Priv" in _type:
        newtype = 2
    elif "Publ" in _type:
        newtype = 1
    else:
        newtype = 0
    if not dupChk("product", "name", prod_name, cursor):
        cursor.execute("INSERT INTO product(name,  _release, federated, company_id, _update, _type) VALUES('%s', '%s', '%d','%d', '%d', '%d')"
                       % (prod_name, reported_rel, federated, company_id, upd_status, newtype))
    db.commit()
    product_id = getProductId(cursor, prod_name)
    if product_id is None:
        return
    tickets = []
    tickets = splitTiks(ticket_link)
    for link in tickets:
        if not dupChk("ticket", "tik_link", ticket_link, cursor):
            if ticket_link is not None:
                _id = link.split("/")[-1]
            else:
                _id = "N/A"
            cursor.execute("INSERT INTO ticket(id, tik_link, product_id) VALUES('%s', '%s','%s')" % (
                _id, link, product_id))
    db.commit()
    if lic_link is not None and lic_link:
        if lic_date is None:
            lic_date = "no date on file"
        for link in result_links:
            if link:
                result_id = link.split("/")[-1]
            cursor.execute("INSERT INTO license(result_id, _link, _type, _date) VALUES('%s', '%s', '%d', '%s')" %
                           (result_id, lic_link, newtype, lic_date))
    db.commit()


def pushContacts(names, emails, company_id):
    for x, y in zip(names, emails):
        if not(dupChk("contact", "email", str("<" + y + ">"), cursor)) and "no name on record" not in x and x != '' and x != " ":
            cursor.execute("INSERT INTO contact(name, email, company_id) VALUES('%s', '%s', '%d')" % (
                x, y, company_id))


def updateEntry(company_name, prod_name, guideline, reported_rel, passed_rel,
                federated, refstack_link, ticket_link, lic_date, lic_link, cursor, db):
    product_id = getProductId(cursor, prod_name)
    company_id = getCompanyId(cursor, company_name)
    # guideline table updates
    cursor.execute(
        "SELECT guideline FROM result WHERE guideline ='%s'" % (guideline))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if guideline not in to_chk:
            cursor.execute("UPDATE result SET guideline = '%s' WHERE _product_id_ = '%s' AND refstack = '%s'" % (
                guideline, product_id, refstack_link))
    # now we update our contact table
    cursor.execute(
        "SELECT name FROM contact WHERE company_id ='%s'" % (company_id))
    to_chk = cursor.fetchone()
    if to_chk is not None and to_chk[0] is not None:
        to_chk = to_chk[0]
    # now update the product table
    cursor.execute("SELECT _release FROM product WHERE company_id ='%s' AND name = '%s'" % (
        company_id, prod_name))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if reported_rel not in to_chk:
            cursor.execute("UPDATE product SET _release ='%s' WHERE company_id = '%s' and name = '%s'" % (
                reported_rel, company_id, prod_name))
    cursor.execute("SELECT federated FROM product WHERE company_id ='%s' AND name = '%s'" % (
        company_id, prod_name))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
    federated = fedChk(federated)
    if to_chk != federated:
        cursor.execute("UPDATE product SET federated ='%s' WHERE company_id = '%s' and name = '%s'" % (
            federated, company_id, prod_name))
    cursor.execute(
        "SELECT id FROM result WHERE _product_id_ ='%s'" % (product_id))
    result_id = cursor.fetchone()
    if result_id is not None:
        result_id = result_id[0]
    cursor.execute(
        "SELECT _link FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if to_chk and lic_link not in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE product_id = '%s'" % (
                lic_link, product_id))
    cursor.execute(
        "SELECT _date FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None and dupChk("license", "result_id", result_id, cursor):
        to_chk = to_chk[0]
        if lic_date not in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE id = '%s'" % (
                lic_date, product_id))
    db.commit()


def fedChk(federated):
    if 'yes' in federated:
        return 1
    else:
        return 0


def updateLicenseChk(upd_status):
    if 'yes' in upd_status:
        return 1
    else:
        return 0


def get_entry(line):
    company_name = line[0]
    prod_name = line[1]
    _type = line[2]
    region = line[3]
    guideline = line[4]
    component = line[5]
    reported_rel = line[6]
    passed_rel = line[7]
    federated = line[8]
    refstack_link = line[9]
    ticket_link = line[10]
    marketp_link = line[11]
    lic_date = line[12]
    upd_status = line[13]
    contact = line[14]
    notes = line[15]
    lic_link = line[16]
    active = line[17]
    public = line[18]
    company_name = company_name.replace("\n", " ").replace("\r", " ")
    return company_name, prod_name, _type, region, guideline, component,\
        reported_rel, passed_rel, federated, refstack_link, ticket_link,\
        marketp_link, lic_date, upd_status, contact, notes, lic_link, active, public


def pushResult(link, tik_id, guideline, product_id):
    if tik_id is None:
        tik_id = 0
    if product_id is None:
        product_id = 0
    if not dupChk("result", "refstack", link, cursor):
        if link is not None:
            _id = link.split("/")[-1]
        else:
            _id = "N/A"
        cursor.execute("INSERT INTO result(id, refstack, tik_id, guideline, _product_id_) VALUES('%s', '%s', '%s', '%s', '%d')" % (
            _id, link, tik_id, guideline, product_id))


def pushResults(api_links, tik_id, guideline, product_id):
    for link in api_links:
        pushResult(link, tik_id, guideline, product_id)


def splitContact(contact):
    fields = []
    entry = []
    names = []
    emails = []
    fields = contact.replace("\n", " ").replace("\r", " ").split(">")
    for x in fields:
        entry = x.split("<")
        try:
            name = entry[0]
            if ", " in name:
                name = name.split(", ")[1]
        except Exception:
            name = "no name on record"
        names.append(name)
        try:
            email = entry[1]
        except Exception:
            email = "no email on file"
        emails.append(email)
    return names, emails


def processEntry(entry, db, cursor, linect, dbStatus):
    # get data fields
    company_name, prod_name, _type, region, guideline, component,\
        reported_rel, passed_rel, federated, refstack_link, ticket_link,\
        marketp_link, lic_date, upd_status, contact, notes, lic_link, active, public = get_entry(
            entry)
    if company_name and company_name is not "" and "DISTRIBUTIONS" not in company_name and "PRIVATE" not in prod_name and "PUBLIC" not in prod_name and "LEADS" not in company_name and "IN PROGRESS" not in prod_name and "HOSTED" not in company_name and "PUBLIC" not in company_name and "Product" not in prod_name:
        api_links = []
        guidelines = []
        components = []
        passed_rels = []
        reported_rels = []
        # split entries
        guidelines, components, passed_rels, reported_rels = splitEntry(
            guideline, component, passed_rel, reported_rel)
        pushStatus = True
        api_links = fixLink(refstack_link)
        if not linksChk(api_links, linect):
            print("The link associated with the product " + prod_name + " and the guideline " + guideline +
                  " is broken, or does not exist. please check and update this field in the spreadsheet")
            notes = notes + "; this link is broken or does not exist. please check and update this field."
            upd_status = "yes"
            pushStatus = False
        if not guidelines or not components or not passed_rels or not reported_rels:
            if not guidelines:
                guidelines = [' ']
            if not components:
                components = [' ']
            if not passed_rels:
                passed_rels = [' ']
            if not reported_rels:
                reported_rels = [' ']
        # else:
        for w, x, y, z in zip(guidelines, components, passed_rels, reported_rels):
            # update spreadsheet
            spreadsheet.append_row([company_name, prod_name, _type, region,
                                    w, x, y, z, federated, refstack_link,
                                    ticket_link, marketp_link, lic_date,
                                    upd_status, contact, notes, lic_link,
                                    active, public])
            if dbStatus or newChk(company_name, prod_name, cursor) and "Company" not in company_name:
                pushEntry(company_name, prod_name, w, z, y, federated, z, _type,
                          ticket_link, lic_date, upd_status, lic_link, cursor, db)
            else:
                updateEntry(company_name, prod_name, w, z, y, federated, api_links, ticket_link,
                            lic_date, lic_link, cursor, db)
        if pushStatus:  # we do this later to ensure that we will have the appropriate product_id and ticket_id in the db
            product_id = getProductId(cursor, prod_name)
            tik_id = getTikId(ticket_link)
            company_id = getCompanyId(cursor, company_name)
            names = []
            emails = []
            names, emails = splitContact(contact)
            pushContacts(names, emails, company_id)
            pushResults(api_links, tik_id, guideline, product_id)
            db.commit()


# connect to spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '<google credentials json file>', scope)
docId = "<Google Spreadsheet Document ID>"
client = gspread.authorize(credentials)
doc = client.open_by_key(docId)
spreadsheet = doc.worksheet("OpenStack Powered Worksheet (Barcelona)")
# connect to MySQL database
print("connecting to MySQL")
db = pymysql.connect("<MySQL db server>", "<user>", "<password>")
cursor = db.cursor()
exists = cursor.execute(
    "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = 'vendorData'")
if exists == 0:
    print("db 'vendorData' does not exist. creating now")
    with open("vendorData.sql") as r:
        for line in r:
            cursor.execute(line)
else:
    cursor.execute("USE vendorData")
dbStatus = emptyChk(cursor)
# get data from spreadsheet
data = spreadsheet.get_all_values()
print("resizing spreadsheet")
spreadsheet.resize(2)
spreadsheet.clear()
linect = 0
for entry in data:
    linect = linect + 1
    processEntry(entry, db, cursor, linect, dbStatus)
