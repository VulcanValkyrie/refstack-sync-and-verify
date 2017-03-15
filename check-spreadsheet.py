#!/usr/bin/python3

import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib2
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')


def get_size():
    ct = 1
    with open("resultsworksheet.csv") as read:
    	for line in read:
                if line:
          	    col_a = line.split(",")[0]
                    col_b = line.split(",")[-1]
                    if col_a != '' or col_b !='':
                        ct = ct + 1
    return ct


def get_csv():
    filename = 'resultsworksheet.csv'
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(spreadsheet.get_all_values())
    return filename  # deal with the case of muliple worksheets later


def split_entry(guideline, refstack_link, ticket_link, lic_date):
    guide2 = guideline.split()[1]
    guideline = guideline.split()[0]
    if len(refstack_link.split()) ==2:
	rs_link2 = refstack_link.split()[1]
    else:
        rs_link2 = refstack_link
    refstack_link = refstack_link.split()[0]
    if len(ticket_link.split()) == 2:
        tiklink2 = ticket_link.split()[1]
    else:
        tiklink2 = ticket_link
    ticket_link = ticket_link.split()[0]
    if len(lic_date.split()) == 2:    
	date2 = lic_date.split()[1]
    else:
	date2 = lic_date
    lic_date = lic_date.split()[0]
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

def parsefile(data):
    span = 20
    fields =20ata.split(",")
    entries = [",".join(fields[i:i+span]) for i in range(0, len(fields), span)]
    return entries

def process_spreadsheet(filename):
    linect = 0  # this is the counter which keeps track of the line
    entries = []
    with open(filename, 'r') as f:
        data = f.read().replace('\r', ',').replace('\n', '  ')
        #data = f.read().strip()
        entries = parsefile(data)
        for x in entries:
            x = x.replace("^M", "")
            if x.split(" , ")[0] and x.split(",")[1]:
                '''if x.split(",")[0] == '' or x.split(",")[0] == ' ' or x.split(",")[0] == '1':
                    x = x.split(",", 1)[1]
                if x.split(",")[1] == '' or x.split(",")[1] == ' ' or x.split(",")[1] == '1':
                    x = x.split(",", 1)[1]
	        if x.split(",")[2] == '' or x.split(",")[2] == ' ' or x.split(",")[2] == '1':
                    x = x.split(",", 1)[1]
                if x.split(",")[3] == '' or x.split(",")[3] == ' ' or x.split(",")[3] == '1':
                    x = x.split(",", 1)[1]
                if x.split(",")[4] == '' or x.split(",")[4] == ' ' or x.split(",")[4] == '1':
                    x = x.split(",", 1)[1]'''
                linect = linect + 1
                print(x + "\n")
            	company_name = x.split(',')[0]; print("company name " + company_name)
            	prod_name = x.split(',')[1]; print("product name " + prod_name)
                print("\n\n")
            	'''_type = line.split(',')[2]
            	region = line.split(',')[3]
            	guideline = line.split(',')[4]
            	component = line.split(',')[5]
            	reported_rel = line.split(',')[6]
            	passed_rel = line.split(',')[7]
            	federated = line.split(',')[8]
            	refstack_link = line.split(',')[9]
            	ticket_link = line.split(',')[10]
            	lic_date = line.split(',')[12]
            	upd_status = line.split(',')[13]
            	contact = line.split(',')[14]
            	lic_link = line.split(',')[15]
            	active = line.split(',')[16]
            	if(len(guideline) > 9):  # if there is more than one link:
            	    # split the relevant fields
                	guideline, guide2, refstack_link, rs_link2, ticket_link,\
                    	tiklink2, lic_date, date2 = split_entry(guideline,
                    	                                        refstack_link,
                        	                                    ticket_link,
                        	                                    lic_date)
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

                	# now update the existing row to the new short form
                	spreadsheet.update_acell("E" + str(linect), guideline)
                	spreadsheet.update_acell("J" + str(linect), refstack_link)
                	spreadsheet.update_acell("K" + str(linect), ticket_link)
                	spreadsheet.update_acell("M" + str(linect), lic_date)
                	spreadsheet.update_acell(
                    	"P" + str(linect), "this is the row we split")
            	api_link = fix_link(refstack_link)
            	ref_status = link_chk(api_link, linect)
            	if not ref_status:
                	print("the test result associated with the product " +
                      	      prod_name + " and the guideline " + guideline +
                      	      " is broken, or does not exist. please review")
		'''

print("UPDATE PROGRESS:")
print("connecting to spreadsheet...")
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    'gcreds.json', scope)
doc_id = "1HFWqIUmb1gQYhqFptgrgKiTGicmq4ZKsGIdt9F6vnus"
client = gspread.authorize(credentials)
spreadsheet = client.open_by_key(doc_id).worksheet('Sheet1')
filename = get_csv();
rows = get_size()
print("resizing spreadsheet...")
print("yes, this does take forever...")
spreadsheet.resize(rows)
print("retrieviing spreadsheet...")
print("processing and updating spreadsheet...\n")
process_spreadsheet(filename)
print("\n")
