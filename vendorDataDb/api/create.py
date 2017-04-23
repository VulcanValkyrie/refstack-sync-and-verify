#!/usr/bin/python3.5
import pymysql
import argparse


def dupChk(table, keytype, keyval, cursor):
    query = "SELECT COUNT(*) FROM %s WHERE %s = '%s'"%(table, keytype, keyval)              
    cursor.execute(query)
    rowcount = cursor.rowcount                                                              
    if rowcount != 0:                                                                       
        return True                                                                         
    else:
        return False                                                                        

def process_flags(results):
    if results.table is None:                                                               
        table = "N/A"                                                                       
    else:
        table = results.table
    return table                                                           

def connect():
    db = pymysql.connect("<vendordata server db>", "<user>", "<password>", "vendorData")
    cursor = db.cursor()
    parser = argparse.ArgumentParser()               
    return db, cursor, parser


