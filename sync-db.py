#!/usr/bin/python35
import csv
import gspread
import pymysql
import subprocess
import urllib2
from oauth2client.service_account import ServiceAccountCredentials
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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
        return company_name, prod_name, _type, region, guideline, component,\
            reported_rel, passed_rel, federated, refstack_link, ticket_link,\
            marketp_link, lic_date, upd_status, contact, lic_link, active, public


def pop_db(filename):
    if prod_name not in company_name:
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


def getCompanyId(cursor, company_name):
    cursor.execute("SELECT id FROM company WHERE name = '%s'" % (company_name))
    company_id = cursor.fetchone()
    if company_id is not None:
        company_id = company_id[0]
    return company_id


def getProductId(cursor, product_name):
    cursor.execute("SELECT id FROM company WHERE name = '%s'" % (product_name))
    product_id = cursor.fetchone()
    if product_id is not None:
        product_id = product_id[0]
    return product_id


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


def push_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
               federated, refstack_link, ticket_link, lic_date, upd_status,
               name, email, lic_link, cursor, db):
    federated = fedChk(federated)
    upd_status = updateLicenseChk(upd_status)
    if not (dup_chk(cursor, "company", company_name)):
        cursor.execute("INSERT INTO company(NAME) VALUES('%s')" %
                       (company_name))
    cursor.execute(
        "SELECT id FROM company WHERE name = '%s'" % (company_name))
    company_id = getCompanyId(cursor, company_name)
    if company_id is None:
        return
    if not(dup_chk(cursor, "contact", contact)):
        cursor.execute("INSERT INTO contact(name, email, company_id) VALUES('%s', '%s', '%d')" % (
            name, email, company_id))
    if not(dup_chk(cursor, "product", prod_name)):
        cursor.execute("INSERT INTO product(name,  _release, federated, company_id, _update) VALUES('%s', '%s', '%d','%d', '%d')" % (
            prod_name, reported_rel, federated, company_id, upd_status))
    product_id = getProductId(cursor, prod_name)
    if product_id is None:
        return
    if not dup_chk(cursor, "ticket", ticket_link) and ' 'not in ticket_link:
        cursor.execute("INSERT INTO ticket(tik_link, product_id) VALUES('%s','%s')" % (
            ticket_link, product_id))
    cursor.execute("SELECT id FROM ticket WHERE tik_link='%s' AND product_id='%d' IS NOT NULL" % (
        ticket_link, product_id))
    tik_id = cursor.fetchone()
    if tik_id is not None:
        tik_id = tik_id[0]
    if not(dup_chk(cursor, "result", refstack_link)) and refstack_link:
        cursor.execute("INSERT INTO  result(refstack, tik_id, guideline, _product_id_) VALUES('%s', '%d', '%s', '%d')" % (
                       refstack_link, tik_id, guideline, product_id))
    cursor.execute("SELECT id FROM result WHERE refstack='%s' IS NOT NULL AND _product_id_='%d' IS NOT NULL" % (refstack_link,
                                                                                                                product_id))
    result_id = cursor.fetchone()
    if result_id is not None:
        result_id = result_id[0]
        if not(dup_chk(cursor, "license", result_id)):
            cursor.execute("INSERT INTO license(result_id, date) VALUES('%d', '%s')" % (
                result_id, lic_date))
    db.commit()


def flag_result(db, cursor, refstack_link, prod_name):
    product_id = getProductId(cursor, prod_name)
    cursor.execute("UPDATE result SET flagged = 1 WHERE refstack = '%s' AND _product_id_ = '%s'" % (
        refstack_link, product_id))
    db.commit()


def update_entry(company_name, prod_name, guideline, reported_rel, passed_rel,
                 federated, refstack_link, ticket_link, lic_date,  name, email,
                 lic_link, cursor, db):
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
    cursor.execute("SELECT refstack FROM result WHERE guideline = '%s' AND _product_id_ = '%s'" % (
        guideline, product_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if refstack_link not in to_chk:
            cursor.execute("UPDATE result SET refstack = '%s' WHERE _product_id_ = '%s' AND guideline = '%s'" % (
                refstack_link, product_id, guideline))
    # now we update our contact table
    cursor.execute(
        "SELECT email FROM contact WHERE company_id ='%s'" % (company_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:  
        to_chk = to_chk[0]
        if email not in to_chk:
            cursor.execute("UPDATE contact SET email = '%s' WHERE company_id = '%s'" % (
                email, company_id))
    cursor.execute(
        "SELECT name FROM contact WHERE company_id ='%s'" %(company_id))
    to_chk = cursor.fetchone()
    if to_chk is not None and to_chk[0] is not None:
        to_chk = to_chk[0]
        if name not in to_chk:
            cursor.execute("UPDATE contact SET name = '%s' WHERE company_id = '%s'" %(name, company_id))
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
    cursor.execute(
        "SELECT tik_link FROM ticket WHERE product_id ='%s'" % (product_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if ticket_link not in to_chk:
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
        if to_chk and lic_link not in to_chk:
            cursor.execute("UPDATE license SET link = '%s' WHERE product_id = '%s'" % (
                lic_link, product_id))
    cursor.execute(
        "SELECT date FROM license WHERE result_id ='%s'" % (result_id))
    to_chk = cursor.fetchone()
    if to_chk is not None:
        to_chk = to_chk[0]
        if lic_date not in to_chk:
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

def splitContact(contact):
   fields = []
   #print contact
   if not contact:
       return None
   fields = contact.split("<")
   #print fields
   return fields

def fixLinks(link):
    links = []
    newurls = []
    if " " in link or not link:  # making sure this is an actual link
        return None
    links = link.replace("\n", " ").replace("\r", " ").split(" ")
    for x in links:
        base_domain = link.split('/')[2]
        test_id = link.split('/')[-1]
        newurl = "https://" + str(base_domain) + \
            "/api/v1/results/" + str(test_id)
        newurls.append(newurl)
    return newurls


def link_exists(links):
    if not links:  # handles empty fields
        return False
    for x in links:
        try:
            response = urllib2.urlopen(x)
            #if(response.geturl() == x):  # returns false if redirect
            #    status = False
	    #print("redirected")
            #else:
            return True
        except urllib2.HTTPError as err:  # should catch any error codes
            print("error: " + err)
            status = False
    return status



#filename = get_csv()
db = pymysql.connect("<MySQL db server>", "<user>",
                     "<password>", "<MySQL db name>")
cursor = db.cursor()
scope = ['https://spreadsheets.google.com/feeds']
ServiceAccountCredentials.from_json_keyfile_name('<google credentials json file>', scope)
doc_id = "<google spreadsheet doc id>"
client = gspread.authorize(credentials)
doc = client.open_by_key(doc_id)
spreadsheet = doc.worksheet('current')
data = spreadsheet.get_all_values()
rows = len(data)
empty_db = empty_chk(cursor)
for line in data:
    company_name, prod_name, _type, region, guideline, component,\
        reported_rel, passed_rel, federated, refstack_link, ticket_link,\
        marketp_link, lic_date, upd_status, contact, lic_link, active, public = get_entry(line)
    contact_data = []    
    contact_data = splitContact(contact)
    if contact_data is not None:
        if contact_data[0]:
            name  = contact_data[0]
        else:
            name = "no name on file"
        if len(contact_data) >= 1:
            email = contact_data[-1]
        else:
            email = "no email on file"
    else:
        name = "no name on file"
        email = "no email on file"
    if company_name is None or prod_name is None:
        continue
    new_entry = new_chk(company_name, prod_name, cursor)
    #if the db is empty, of if this entry does not exist, push entry
    if empty_db or new_entry and "Company" not in company_name:
        #print("pushing entry for the product: " + prod_name)
        push_entry(company_name, prod_name, guideline, reported_rel,
                   passed_rel, federated, refstack_link, ticket_link,
                   lic_date, upd_status, name, email, lic_link, cursor, db)
    else:
        #print("updating entry for the product: " + prod_name)
        update_entry(company_name, prod_name, guideline, reported_rel,
                     passed_rel, federated, refstack_link, ticket_link,
                     lic_date, name, email, lic_link, cursor, db)
    # now that we have made sure that our database is up to date, let's
    # make sure our result link is actually valid
    if refstack_link is not None:
        api_links = []
        api_links = fixLinks(refstack_link)
        if not link_exists(api_links):
            print("The refstack result link for product " + prod_name +
                  " and guideline " + guideline + " is broken."
                  + " Please review this entry and try again.")
        flag_result(db, cursor, refstack_link, prod_name)
