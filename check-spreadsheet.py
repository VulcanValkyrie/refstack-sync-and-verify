#!/usr/bin/python3

import time
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import urllib2
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')

def split_entry(guideline, component, passed_rel, reported_rel):
    guidelines =[]; components = []; passed_rels = []; reported_rels = []
    guidelines = guideline.replace("\n", " ").replace("\r", " ").split(" ")
    components = component.replace("\n", " ").replace("\r", " ").split(" ")
    passed_rels = passed_rel.replace("\n", " ").replace("\r", " ").split(" ")
    reported_rels = reported_rel.replace("\n", " ").replace("\r", " ").split(" ")
    return guidelines, components, passed_rels, reported_rels

def links_chk(links, linect):  # returns true if valid page and false if not
     if links is None or not links:
        return False
     if linect == 0: #handles the header
        return True 
     status = False
     for x in links: 
        try:
            if " " in x:
                status = False
            response = urllib2.urlopen(x)
            if response.geturl() == x:  # returns true if the link works
                status = True
    	except urllib2.HTTPError as err:  # meant to catch 404s, etc.
           status = False
     return status

def fix_link(link):
    links = []; newurls = []
    if " " in link or not link or link == '':
        return None
    links = link.replace("\n", " ").replace("\r", " ").split(" ")
    for x in links:
        try: 
           base_domain = x.split('/')[2]
           test_id = x.split('/')[-1]
           newurl = "https://" + str(base_domain) + "/api/v1/results/" + str(test_id)
           
           newurls.append(newurl)
        except Exception:
            return None
    return newurls

def process_spreadsheet(data, spreadsheet):
    linect = 1  # this is the counter which keeps track of the line
    spreadsheet.clear()
    for x in data:
        linect = linect + 1;
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
                guidelines =[]; components = []; api_links = []
                passed_rels = [];   reported_rels = [] ;
                # check all results asociated with a product to make
                # sure at least one of the links is valid
                api_links = fix_link(refstack_link)
                ref_status = links_chk(api_links, linect)
                #now we add the new fields to the spreadsheet as a new row.
                if not ref_status and linect != 1 and linect != 0:
                    print("the test result associated with the product " +
                          prod_name + " on line " +  str(linect) + " is broken,"+
                          " or nonexistent. please check and update the link")
	            notes = notes + "; This link is broken or nonexistent. Please update the refstack result links associated with this product."
                    upd_status = "yes"
                guidelines, components, passed_rels, reported_rels, = split_entry(guideline,
		                                         	                  component,
                                                                                  passed_rel,
								                  reported_rel)
		for w, x, y, z in zip(guidelines, components, passed_rels, reported_rels):
		    spreadsheet.append_row([company_name, prod_name, _type, region, w, x, y, z,
                                        federated, refstack_link, ticket_link, marketp_link,
                                        lic_date, upd_status, contact, notes, lic_link,
                                        active, public])  


print("UPDATE PROGRESS:")
print("connecting to spreadsheet...")
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '<google credentials json file>', scope)
doc_id = "<google spreadsheet Id>"
client = gspread.authorize(credentials)
doc  =  client.open_by_key(doc_id)
spreadsheet = doc.worksheet('<spreadsheet name>')
data = spreadsheet.get_all_values() 
rows = len(data)
print("resizing spreadsheet...")
#print("yes, this does take forever...")
spreadsheet.resize(1)
print ("checking and updating spreadsheet")
updated = process_spreadsheet(data, spreadsheet)
print("\n")
