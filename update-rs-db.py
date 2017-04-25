#!/usr/bin/python3.5
import urllib.request
import urllib.error
import time
import sys
import subprocess
import requests
import argparse


def process_flags(result):
    if result.filename is None or not result.filename:
        infile = "toadd.csv"
    else:
        infile = result.filename
    if result.server is None or not result.server:
        server = "refstack.openstack.org"
    else:
        server = result.server
    if result.token is None or not result.token or result.token is " ":
        print("cannot authenticate without a token.")
        sys.exit()
    else:
        token = result.token
    return infile, server, token


def convertLink(server, testId):
    if testId is " " or server is " ":
        return None
    apiLink = "https://" + server + "/api/v1/results/" + str(testId)
    return apiLink


def getData(entry):
    if entry[9] is not "" and entry[9] is not " ":
        refstackLink = entry[9]
        testId = refstackLink.split("/")[-1]
    else:
        refstackLink = None
        testId = None
    if entry[4] is not "" and entry[4] is not " ":
        guideline = entry[4]
    else:
        guideline = None
    if entry[5] is not "" and entry[5] is not " ":
        target = entry[5]
    else:
        target = None
    return testId, guideline, target


def linkChk(link):
    print("checking result with a test ID of: " + link.split("/")[-1])
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


def updateResult(apiLink, testId, server, target, guideline):
    resp = requests.post(apiLink + '/meta/shared', data='true')
    resp = requests.post(apiLink + '/meta/guideline', data=guideline)
    resp = requests.post(apiLink + '/meta/target', data=target)
    print("test result updated. Verifying.\n")
    resp = requests.put(apiLink, data={'verification_status': 1})


def main():
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    parser.add_argument("--file", "-f", metavar='f', type=str,
                        action="store", dest="filename", default="toadd.csv")
    parser.add_argument("--server", "-s", metavar='s',
                        type=str, action="store", dest="server")
    parser.add_argument("--token", "-t", metavar="t", type=str,
                        action="store", dest="token", required=True)
    result = parser.parse_args()
    infile, server, token = process_flags(result)
    with open(infile) as f:
        try:
            authcmd = " curl -k --header \"Authorization: Bearer \"" + \
                token + "\"\" " + server + "/v1/profile"
            authcmd = authcmd.split()
            response = subprocess.Popen(
                authcmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result = str(response.communicate())
            if "Found" not in result or "404" in result:
                print("Authentication Failure. Exiting.")
                sys.exit()
        except Exception as err:
            print("cannot authenticate to RefStack API: " + str(err))
            sys.exit()
        time.sleep(2)
        print("\n")
        for line in f:
            entry = []
            entry = line.split(",")
            testId, guideline, target = getData(entry)
            if testId is None or guideline is None or target is None:
                print("Cannot update & verify test result due to missing data.\n")
            else:
                apiLink = convertLink(server, testId)
                if linkChk(apiLink):
                    print("link is valid. Updating.")
                    updateResult(apiLink, testId, server, target, guideline)
                else:
                    print("the test result " + testId +
                          " cannot be verified due to a broken link.\n")


main()
