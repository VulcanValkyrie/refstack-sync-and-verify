#!/usr/bin/python
import time
import sys
import subprocess
import requests
import argparse


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


def linkChk(link, token):
    print("checking result with a test ID of: " + link.split("/")[-1])
    if link is None or not link:
        return False
    try:
        if " " in link:
            return False
        response = requests.get(
            link, headers={'Authorization': 'Bearer' + token})
        if response.status_code is 200:
            return True
        else:
            return False
    except request.exceptions as err:
        print(err)
        return False


def updateResult(apiLink, testId, server, target, guideline, token):
    resp = requests.post(apiLink + '/meta/shared', headers={
                         'Authorization': 'Bearer' + token}, data='true')
    resp = requests.post(apiLink + '/meta/guideline', headers={
                         'Authorization': 'Bearer' + token}, data=guideline)
    resp = requests.post(apiLink + '/meta/target', headers={
                         'Authorization': 'Bearer' + token}, data=target)
    print("test result updated. Verifying.\n")
    resp = requests.put(apiLink, headers={
                        'Authorization': 'Bearer' + token}, data={'verification_status': 1})


def main():
    parser = argparse.ArgumentParser(
        "Update the internal RefStack db using a csv file")
    parser.add_argument("--file", "-f", metavar='f', type=str, action="store",
                        required=True, help="csv source for the data to use in updates")
    parser.add_argument(
        "--endpoint", "-e", metavar='s', type=str, action="store",
                        required=True, help="the base URL of the endpoint. ex: http://examplerefstack.com/v1")
    parser.add_argument("--token", "-t", metavar="t", type=str,
                        action="store", required=True, help="API auth token")
    result = parser.parse_args()
    infile = result.file
    endpoint = result.endpoint
    token = result.token
    with open(infile) as f:
        for line in f:
            entry = []
            entry = line.split(",")
            testId, guideline, target = getData(entry)
            if testId is None or guideline is None or target is None:
                print(
                    "Cannot update & verify test result due to missing data.\n")
            else:
                apiLink = os.join(endpoint, '/results/' + testId)
                if linkChk(apiLink, token):
                    print(
                        "Result link is valid. Updating the result with the ID " + testId + "\n")
                    updateResult(
                        apiLink, testId, server, target, guideline, token)
                else:
                    print("the test result " + testId +
                          " cannot be verified due to a broken result link.\n")


main()
