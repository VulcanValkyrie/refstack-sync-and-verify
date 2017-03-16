#!/usr/bin/python3

import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib2
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')


def split_entry(guideline, refstack_link, ticket_link, lic_date):
    guide2 = guideline.replace("\n", " ").replace("\r", " ").split()[1]
    guideline = guideline.replace("\n", " ").replace("\r", " ").split()[0]
    if len(refstack_link.split()) >=2:
	rs_link2 = refstack_link.replace("\n", " ").replace("\r", " ").split()[1]
    else:
        rs_link2 = refstack_link
    refstack_link = refstack_link.replace("\n", " ").replace("\r", " ").split()[0]
    if len(ticket_link.split()) >= 2:
        tiklink2 = ticket_link.replace("\n", " ").replace("\r", " ").split()[1]
    else:
        tiklink2 = ticket_link
    ticket_link = ticket_link.replace("\n", " ").replace("\r", " ").split()[0]
    if len(lic_date.split()) >= 2:    
	date2 = lic_date.replace("\n", " ").replace("\r", " ").split()[1]
    else:
	date2 = lic_date
    lic_date = lic_date.replace("\n", " ").replace("\r", " ").split()[0]
    return guideline, guide2, refstack_link, rs_link2, ticket_link, tiklink2,\
        lic_date, date2


def link_chk(link, linect):  # returns true if valid page and false if not
    if(linect == 1):
        return True  # not an error, header row
    if link == '' or not link:  # ignores if empty field
        return False
    try:
        response = urllib2.urlopen(link)
        if response.geturl() != link:  # returns false if redirected
            return False
        else:
            return True
    except urllib2.HTTPError as err:  # meant to catch 404s, etc.
        return False


def fix_link(link):
    if " " in link or not link or link == '':
        return None
    try:
        base_domain = link.split('/')[2]
        test_id = link.split('/')[-1]
        newurl = "https://" + str(base_domain) + "/api/v1/results/" + str(test_id)
        return newurl
    except Exception:
        return None

def process_spreadsheet(data):
    linect = 0  # this is the counter which keeps track of the line
    for x in data:
    	#print(data)
	if x[0] and x[1]:
        	linect = linect + 1
        	company_name = x[0]; #print("NOW CHECKING: company name " + company_name)
        	prod_name = x[1];#print("product name " + prod_name)
        	_type = x[2]
        	region = x[3]
        	guideline = x[4]
        	component = x[5]
        	reported_rel = x[6]
        	passed_rel = x[7]
        	federated = x[8]
        	refstack_link = x[9]
        	ticket_link = x[10]
                marketp_link = x[11]
        	lic_date = x[12]
        	upd_status = x[13]
        	contact = x[14]
                notes = x[15]
        	lic_link = x[16]
        	active = x[17]
                public = x[18]
        	if(len(guideline) > 9):  # if there is more than one link:
        	# split the relevant fields
        	    #print ("the line associated with "+ company_name +"\'sproduct "+ prod_name + " needs to be split")
                    #guidelines = []; ref_link = []
                    #tik_link = [];   license_date = [];
                    guideline, guide2, refstack_link, rs_link2, ticket_link,\
        	    tiklink2, lic_date, date2 = split_entry(guideline,
        	                                            refstack_link,
        	                                            ticket_link,
        	                                            lic_date)
                    #guidelines, ref_link, tik_link, license_date = split_entry(guideline,
                    #                                                           refstack_link,
                    #                                                           ticket_link,
                    #                                                          lic_date)
        	    api_link2 = fix_link(rs_link2)
        	    ref_status = link_chk(api_link, linect)
        	    # now we add the new fields to the spreadsheet as a new row.
        	    spreadsheet.append_row([company_name, prod_name, _type, region,
                    	                    guideline, component, reported_rel,
                    		            passed_rel, federated, rs_link2,
                         	                tiklink2, date2, upd_status, "this is\
                        	                the new split row", contact, lic_link])
            	    if not ref_status:
                	print("the test result associated with the product " +
                	      prod_name + " and the guideline " + guideline +
                	      " is broken, or does not exist. please review")

            	#now update the existing row to the new short form
            	spreadsheet.update_acell("E" + str(linect), guideline)
            	spreadsheet.update_acell("J" + str(linect), refstack_link)
            	spreadsheet.update_acell("K" + str(linect), ticket_link)
            	spreadsheet.update_acell("M" + str(linect), lic_date)
            	spreadsheet.update_acell("P" + str(linect), "this is the row we split")
                api_link = fix_link(refstack_link)
                ref_status = link_chk(api_link, linect)
	        if not ref_status:
        	    print("the test result associated with the product " +
                          prod_name + " and the guideline " + guideline +
                          " is broken, or does not exist. please review")
	

print("UPDATE PROGRESS:")
print("connecting to spreadsheet...")
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'gcreds.json', scope)
doc_id = "<google spreadsheet id>"
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key(doc_id).worksheet('Sheet1')
data = spreadsheet.get_all_values() 
rows = len(data)
print("resizing spreadsheet...")
#print("yes, this does take forever...")
spreadsheet.resize(rows)
#print("retrieviing spreadsheet...")
#print("processing and updating spreadsheet...\n")
process_spreadsheet(data)
print("\n")
