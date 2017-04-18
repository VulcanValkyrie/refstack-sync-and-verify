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


def linkInDb(link):
    testId = link.split('/')[-1]
    matches = requests.get(
        'https://refstack.openstack.org/v1/results/' + testId)
    if matches == '<Response [404]>':
        print("no match found in db for result id " + testId)
        return False
    return True


def getTestId(link):
    testId = link.split('/')[-1]
    return testId


def processLink(line, server):
    if not line[0]:  # or not line[1]:
        return False, None
    links = []
    update = False
    refstack_link = line[9]
    apiLinks = fixLink(refstack_link)
    if apiLinks is None:
        print("No links found for the cloud associated with the company " +
              line[0] + " on the provided spreadsheet.")
        return False, None
    for link in apiLinks:
        resultsStatus = linksChk(link)
        if not resultsStatus:
            #print("Result is broken or does not exist")
            update = False
        linkMatch = linkInDb(link)
        if not linkMatch:
            #print("there is no such result in your db")
            update = False
        testId = getTestId(link)
        if testId is None:
            update = False
        #print("updating shared")
        resp = requests.post(
            "http://" + server + '/v1/results/' + testId + '/meta/shared', data='true')
        guideline = line[4]
        if guideline and guideline != "" and guideline != " ":
            #print("updating guideline")
            resp = requests.post(
                "http://" + server + '/v1/results/' + testId + '/meta/guideline', data=guideline)
        targetProgram = line[5]
        if targetProgram and targetProgram != "" and targetProgram != " ":
            #print("updating target program")
            resp = requests.post(
                "http://" + server + '/v1/results/' + testId + '/meta/target', data=targetProgram)
        if testId is None or not update or update != True:
            update = False
        else:
            return True, testId
    if update == False:
        print("There is no link associated with the company " +
              line[0] + " in your database.")
    return update, testId


def splitLine(line):
    entry = []
    entry = line.split(",")
    return entry


def main():
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    parser.add_argument("--file", "-f", metavar='f', type=str,
                        action="store", dest="filename", default="toadd.csv")
    parser.add_argument("--server", "-s", metavar='s', type=str, action="store",
                        dest="server", default="https://refstack.openstack.org/v1/results/")
    result = parser.parse_args()
    if result.filename is None or not result.filename:
        infile = "toadd.csv"
    else:
        infile = result.filename
    if result.server is None or not result.server:
        server = "https://refstack.openstack.org"
    else:
        server = result.server
    with open(infile) as f:
        for line in f:
            entry = []
            entry = splitLine(line)
            verify, testId = processLink(entry, server)
            if verify:
                print("marking the product data associated with the company " +
                      entry[0] + " as verified")
                resp = requests.put(
                    "http://" + server + '/v1/results/' + testId, data={'verification_status': 1})
            else:
                print("the entry associated with the company " +
                      entry[0] + " cannot be verified.\n")


main()
