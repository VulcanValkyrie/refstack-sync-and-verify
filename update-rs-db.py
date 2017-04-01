#!/usr/bin/python35

from oauth2client.service_account import ServiceAccountCredentials
import urllib2
import gspread
import pymysql
import re
import subprocess
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
    cursor.execute("SELECT id FROM product WHERE name = '%s'"%(productName))
    productId = cursor.fetchone()
    if productId is None:
        print ("No product associated with the given name was found")
        return None
    else:
        productId = productId[0]
    cursor.execute("SELECT id from product_version WHERE product_id = '%s'"%(productId))
    productVersionId = cursor.fetchone()
    if productVersionId is None:
        print("No product version associated with the given name was found")
        return None
    else:
        productVersionId = productVersionId[0]
    cursor.execute("SELECT id from test WHERE product_version_id = '%s'"%(productVersionId))
    testId = cursor.fetchone()
    if testId is None:
        print("No test associated with the given name was found")
        return None
    else:
        testId = testId[0]
    	return testId
    

def processLink(line, linect, cursor):
    if not line[0] or not line[1] or linect == 2:
        return False, None
    links = []
    refstack_link = line[9]
    apiLinks = fixLink(refstack_link)
    for link in apiLinks:
        resultsStatus = linksChk(apiLinks)
        if not resultsStatus:
            return False, None
        linkMatch = linkinDb(apiLinks, cursor)
        if not linkMatch:
            return False, None
    # now that we have verified that the link exists
    # get the related testId
    testId = getTestId(line[1])
    #next, we will update the our local refstack db  
    command = "POST /v1/results/testId/meta/shared request body: 'true'"
    subprocess.run(
    guideline = line[4]
    if guideline and guideline != "" and guideline != " ":
        POST /v1/results/testId/meta/guideline  request body: guideline
 
    targetProgram = line[5]
    if targetProgram and targetProgram != "" and targetProgram != " ":
       POST /v1/results/testId/meta/target request body: targetProgram
    #now return the related test ID
    if testId is None:
        return False, None
    else:
         return True, testId
          

#connect to the internal refstack db
db = pymysql.connect("localhost", "<user>", "<password>", "refstack")
cursor = db.cursor()
#connect to the spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '<google api credentials json file>', scope)
doc_id = "<google spreadsheet id>"
client = client.open_by_key(doc_id)
spreadsheet = doc.worksheet('<spreadsheet name>')
#now get our dataset
data = spreadsheet.get_all_values()
#now check each entry
linect = 0
for entry in data:
    linect = linect + 1
    #check if the data in this line can be verified
    verify, testId = processLink(line, linect, cursor)
    if verify: 
        PUT /v1/results/testId request body:{verification_status: 1} 


