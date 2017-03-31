#!/usr/bin/python35

from oauth2client.service_account import ServiceAccountCredentials
import urllib2
import gspread
import pymysql
import re
reload(sys)
sys.setdefaultencoding('utf-8')
#this presumes the spreadsheet is up to date






def linksChk(links, linect):
    if links is None or not links:
        return False
    if linect == 2:
        return True #not an error, just not a link
    try:
        if " " in x:
            return False
        response = urllib2.urlopen(x)
        if response.geturl() == x:
            return True
    except urllib2.HTTPError as err:
        return False

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
            newurl = "https://"+str(baseDomain)+"/api/v1/results/"+str(testId)
            newurls.append(newurl)
        except Exception:
            continue
    return newurls

def linkInDb(links, cursor):
    matchCt = cursor.execute("SELECT COUNT(*) FROM results WHERE name = '%s'"%(link))
    if matchct != 0:
        return True
    return False
       
def getTestId(productName):
   productId =   

def processLink(line, linect, cursor):
    if not line[0] or not line[1] or linect == 2:
        return False
    links = []
    refstack_link = line[9]
    apiLinks = fixLink(refstack_link)
    for link in apiLinks:
        resultsStatus = linksChk(apiLinks)
        if not resultsStatus:
            return False
        linkMatch = linkinDb(apiLinks, cursor)
        if not linkMatch:
            return False
        # now that we have verified that the link exists
        # let's update some things
        test_id = getTestId(line[1])

#connect to the internal refstack db
db = pymysql.connect("<MySQL db server>", "<user>", "<password>", "refstack")
cursor = db.cursor()
#connect to the spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '<google api credentials json file', scope)
doc_id = "<doc_id>"
client = client.open_by_key(doc_id)
spreadsheet = doc.worksheet('current')
#now get our dataset
data = spreadsheet.get_all_values()
#now check each entry
linect = 0
for entry in data:
    linect = linect + 1
    #check if the data in this line can be verified
    verify = processLink(line, linect, cursor)


