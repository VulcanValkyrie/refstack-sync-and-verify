#!/usr/bin/python3

from oauth2client.service_account import ServiceAccountCredentials
#import urllib2
import urllib.request
import urllib.error
import gspread
import pymysql
import re
import sys
import subprocess
import requests
#from imp import reload
# reload(sys)
# sys.setdefaultencoding('utf-8')
# this presumes the spreadsheet is up to date


def linksChk(link, linect):
    if link is None or not link:
        return False
    if linect == 2:
        return True  # not an error, just not a link
    try:
        if " " in link:
            return False
        response = urllib.request.urlopen(link)
        if response.geturl() == link:
            return True
    except urllib.error.HTTPError as err:
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
            newurl = "https://" + str(baseDomain) + \
                "/api/v1/results/" + str(testId)
            newurls.append(newurl)
        except Exception:
            continue
    return newurls


def linkInDb(link, cursor):
    matchCt = cursor.execute(
        "SELECT COUNT(*) FROM results WHERE name = '%s'" % (link))
    if matchCt != 0:
        return True
    return False


def getTestId(productName):
    cursor.execute("SELECT id FROM product WHERE name = '%s'" % (productName))
    productId = cursor.fetchone()
    if productId is None:
        print ("No product associated with the name " +
               productName + " was found")
        return None
    else:
        productId = productId[0]
    cursor.execute(
        "SELECT id from product_version WHERE product_id = '%s'" % (productId))
    productVersionId = cursor.fetchone()
    if productVersionId is None:
        print("No product version associated with the given name was found")
        return None
    else:
        productVersionId = productVersionId[0]
    cursor.execute(
        "SELECT id from test WHERE product_version_id = '%s'" % (productVersionId))
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
    if apiLinks is None:
        return False, None
    for link in apiLinks:
        resultsStatus = linksChk(link, linect)
        if not resultsStatus:
            return False, None
        linkMatch = linkInDb(link, cursor)
        if not linkMatch:
            return False, None
    # now that we have verified that the link exists
    # get the related testId
    testId = getTestId(line[1])
    # next, we will update the our local refstack db
    # POST /v1/results/testId/meta/shared request body: 'true'
    resp = requests.post(
        'https://refstack.openstack.org/v1/results/testId/meta/shared', data='true')
    guideline = line[4]
    if guideline and guideline != "" and guideline != " ":
        #command = "POST /v1/results/testId/meta/guideline  request body: guideline"
        resp = requests.post(
            'https://refstack.openstack.org/v1/results/testId/meta/guideline', data=guideline)
    targetProgram = line[5]
    if targetProgram and targetProgram != "" and targetProgram != " ":
        #command = "POST /v1/results/testId/meta/target request body: targetProgram"
        resp = requests.post(
            'https://refstack.openstack.org/v1/results/testId/meta/target', data=targetProgram)
    # now return the related test ID
    if testId is None:
        return False, None
    else:
        return True, testId


# connect to the internal refstack db
db = pymysql.connect("<refstack server>", "<user>", "<password>", "refstack")
cursor = db.cursor()
# connect to the spreadsheet
scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name(
    '<google api credential json file>', scope)
docId = "<google spreadsheet document id>"
client = gspread.authorize(credentials)
doc = client.open_by_key(docId)
spreadsheet = doc.worksheet('<spreadsheet name>')
# now get our dataset
data = spreadsheet.get_all_values()
# now check each entry
linect = 0
for entry in data:
    linect = linect + 1
    # check if the data in this line can be verified
    verify, testId = processLink(entry, linect, cursor)
    if verify:
        #"PUT /v1/results/testId request body:{verification_status: 1}"
        resp = requests.put(
            'https://refstack.openstack.org/v1/results/testId/', data={verification_status: 1})
