#!/usr/bin/python35
import gspread
import pymysql
import subprocess
import urllib2
import sys
from oauth2client.service_account import ServiceAccountCredentials
reload(sys)
sys.setdefaultencoding('utf-8')


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


def getTikId(ticket_link, product_id):
    cursor.execute("SELECT id FROM ticket WHERE tik_link = '%s' AND product_id= '%s'" % (
        ticket_link, product_id))
    tik_id = cursor.fetchone()
    if tik_id is not None:
        tik_id = tik_id[0]
    else:
        tik_id = 0
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
            response = urllib2.urlopen(x)
            if response.geturl() == x:
                status = True
        except urllib2.HTTPError as err:
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


def dupChk(cursor, table, specifier):
    if "company" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM company WHERE name = '%s' GROUP BY name" % (specifier))
    if "contact" in table:
        cursor.execute(
            "SELECT email, COUNT(*) FROM contact WHERE email = '%s' GROUP BY email" % (specifier))
    if "product" in table:
        cursor.execute(
            "SELECT name, COUNT(*) FROM product WHERE name = '%s' GROUP BY name" % (specifier))
    if "ticket" in table:
        cursor.execute(
            "SELECT tik_link, COUNT(*) FROM ticket WHERE tik_link = '%s' GROUP BY tik_link" % (specifier))
    if "result" in table:
        cursor.execute(
            "SELECT refstack, COUNT(*) FROM result WHERE refstack = '%s' GROUP BY refstack" % (specifier))
    if "license" in table:
        cursor.execute(
            "SELECT result_id, COUNT(*) FROM license WHERE result_id = '%s' GROUP BY result_id" % (specifier))
    row_count = cursor.rowcount
    if row_count == 0:
        return False
    return True


def pushEntry(company_name, prod_name, guideline, reported_rel, passed_rel,
              federated, _type, ticket_link, lic_date, upd_status, lic_link, cursor, db):
    federated = fedChk(federated)
    upd_status = updateLicenseChk(upd_status)
    if not dupChk(cursor, "company", company_name):
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
    if not(dupChk(cursor, "product", prod_name)):
        cursor.execute("INSERT INTO product(name,  _release, federated, company_id, _update, type) VALUES('%s', '%s', '%d','%d', '%d', '%d')" %
                       (prod_name, reported_rel, federated, company_id, upd_status, newtype))
    db.commit()
    product_id = getProductId(cursor, prod_name)
    if product_id is None:
        return
    tickets = []
    tickets = splitTiks(ticket_link)
    for link in tickets:
        if not dupChk(cursor, "ticket", ticket_link):
            cursor.execute("INSERT INTO ticket(tik_link, product_id) VALUES('%s','%s')" % (
                link, product_id))
    db.commit()


def pushContacts(names, emails, company_id):
    for x, y in zip(names, emails):
        if not(dupChk(cursor, "contact", str(x + " <" + y + ">"))) and "no name on record" not in x and x != '' and x != " ":
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
    # now update the ticket table
    # get a result id
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
        if to_chk and lic_link not in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE product_id = '%s'" % (
                lic_link, product_id))
    cursor.execute(
        "SELECT date FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
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
    if not dupChk(cursor, "result", link):
        cursor.execute("INSERT INTO result(refstack, tik_id, guideline, _product_id_) VALUES('%s', '%d', '%s', '%d')" % (
            link, tik_id, guideline, product_id))


def pushResults(api_links, tik_id, guideline, product_id):
    for link in api_links:
        pushResult(link, tik_id, guideline, product_id)


def splitContact(contact):
    fields = []
    entry = []
    names = []
    emails = []
    # print contact
    fields = contact.replace("\n", " ").replace("\r", " ").split(">")
    for x in fields:
        entry = x.split("<")
        try:
            name = entry[0]
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
    if company_name and prod_name and company_name is not "" and prod_name is not "" and linect != 2:
        api_links = []
        guidelines = []
        components = []
        passed_rels = []
        reported_rels = []
        # split entries
        guidelines, components, passed_rels, reported_rels = splitEntry(
            guideline, component, passed_rel, reported_rel)
        # check links
        pushStatus = True
        api_links = fixLink(refstack_link)
        #print("link list: ")
        # print(api_links)
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
                pushEntry(company_name, prod_name, w, z, y, federated, _type,
                          ticket_link, lic_date, upd_status, lic_link, cursor, db)
            else:
                updateEntry(company_name, prod_name, w, z, y, federated, refstack_link, ticket_link,
                            lic_date, lic_link, cursor, db)
        if pushStatus:  # we do this later to ensure that we will have the appropriate product_id and ticket_id in the db
            product_id = getProductId(cursor, prod_name)
            tik_id = getTikId(ticket_link, product_id)
            company_id = getCompanyId(cursor, company_name)
            names = []
            emails = []
            names, emails = splitContact(contact)
            pushContacts(names, emails, company_id)
            pushResults(api_links, tik_id, guideline, product_id)


# connect to spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(< Google api credentials json file > , scope)
docId = <Google spreadsheet document id >
client = gspread.authorize(credentials)
doc = client.open_by_key(docId)
spreadsheet = doc.worksheet(< spreadsheet name > )
# connect to MySQL database
db = pymysql.connect("localhost", < user >, < password > , "refstack_vendor_data")
cursor = db.cursor()
dbStatus = emptyChk(cursor)
# get data from spreadsheet
data = spreadsheet.get_all_values()
# resize spreadsheet so we can begin our sync
# <- removed for now until we get basic functionality going
spreadsheet.resize(1)
spreadsheet.clear()
# process dataset
linect = 0
for entry in data:
    linect = linect + 1
    processEntry(entry, db, cursor, linect, dbStatus)
