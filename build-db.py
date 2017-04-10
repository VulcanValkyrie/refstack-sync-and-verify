#!/usr/bin/python3

#creates mysql db for the handling of refstack vendor data
from sqlalchemy import *

def buildDb():
    db = create_engine('mysql:///root:password@172.17.0.2/vendordata.db', echo=False)
    metadata = MetaData(db)
    #now we create the "company" table
    company = Table('company', metadata,
        Column('id', Integer),
        Column('name', String(80)))
    #company.create()
    contact = Table('contact', metadata, 
        Column('id', Integer),
        Column('company_id', String(36)),
        Column('name', String(80)),
        Column('email', String(80)))
    #contact.create()
    product = Table('product', metadata,
        Column('id', String(36)),
        Column('name', String(80)),
        Column('type', Integer),
        Column('_release', String(36)),
        Column('federated', Integer),
        Column('company_id', String(36)),
        Column('_update', Integer))
    #product.create()
    result = Table('result', metadata, 
        Column('id', String(36)),
        Column('tik_id', String(36)),
        Column('guideline', String(25)), 
        Column('_product_id_', String(36)), 
        Column('refstack', String(250)),
        Column('flagged', Integer))
    #result.create()
    ticket = Table('table', metadata,
        Column('id', String(36)),
        Column('tik_link', String(250)),
        Column('product_id', String(36)))
    #ticket.create()
    license = Table('license', metadata,
        Column('id', Integer),
        Column('result_id', String(36)),
        Column('link', String(250)),
        Column('type', Integer),
        Column('date', String(36)))
    #license.create()
    metadata.create_all()

