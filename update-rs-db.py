#!/usr/bin/python3

import urllib.request
import urllib.error
import pymysql
import requests
import argparse


def linksChk(link):
    if link is None or not link:
        return False
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
    testId = link.split('/')[-1]
    matches = requests.get(
        'https://refstack.openstack.org/v1/results/' + testId)
    if matches == '<Response [404]>':
        print("no match found in db for result id " + testId)
        return False
    return True


def getTestId(productName, cursor):
    # i think this may be a thing that actually really needs to be querying
    # the local db, but i am not sure
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
        #print("No product version associated with the given name was found")
        return None
    else:
        productVersionId = productVersionId[0]
    cursor.execute(
        "SELECT id from test WHERE product_version_id = '%s'" % (productVersionId))
    testId = cursor.fetchone()
    if testId is None:
        #print("No test associated with the given name was found")
        return None
    else:
        testId = testId[0]
        return testId


def processLink(line, cursor):
    if not line[0]:  # or not line[1]:
        return False, None
    #print(line[0] + " is being processed")
    links = []
    refstack_link = line[9]
    apiLinks = fixLink(refstack_link)
    if apiLinks is None:
        print(
            "No links found for the cloud associated with the company " + line[0] + ".")
        return False, None
    for link in apiLinks:
        resultsStatus = linksChk(link)
        if not resultsStatus:
            print("Result is broken or does not exist")
            return False, None
        linkMatch = linkInDb(link, cursor)
        if not linkMatch:
            return False, None
    # now that we have verified that the link exists
    # get the related testId
    testId = getTestId(line[1], cursor)
    # next, we will update the our local refstack db
    if testId is None:
        return False, None
    print("updating shared")
    resp = requests.post(
        'https://refstack.openstack.org/v1/results/testId/meta/shared', data='true')
    guideline = line[4]
    if guideline and guideline != "" and guideline != " ":
        print("updating guideline")
        resp = requests.post(
            'https://refstack.openstack.org/v1/results/testId/meta/guideline', data=guideline)
    targetProgram = line[5]
    if targetProgram and targetProgram != "" and targetProgram != " ":
        print("updating target program")
        resp = requests.post(
            'https://refstack.openstack.org/v1/results/testId/meta/target', data=targetProgram)
    # now return the related test ID
    if testId is None:
        return False, None
    else:
        return True, testId


def splitLine(line):
    entry = []
    entry = line.split(",")
    return entry


def main():
    # connect to the internal refstack db
    db = pymysql.connect("localhost", < user > , < password > , "refstack")
    cursor = db.cursor()
    # connect to the sourcefile
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    parser.add_argument('--file', "-f", metavar='f', type=str,
                        action="store", dest="filename", default="toadd.csv")
    result = parser.parse_args()
    if result.filename is None or not result.filename:
        infile = "toadd.csv"
    else:
        infile = result.filename
    with open(infile) as f:
        for line in f:
            # check if the data in this line can be verified
            entry = []
            entry = splitLine(line)
            verify, testId = processLink(entry, cursor)
            if verify:
                #"PUT /v1/results/testId request body:{verification_status: 1}"
                print("marking product data as verified")
                resp = requests.put(
                    'https://refstack.openstack.org/v1/results/testId/', data={'verification_status': 1})
            else:
                print("This product cannot be verified.\n")
