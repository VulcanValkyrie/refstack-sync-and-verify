#!/usr/bin/python3

# creates mysql db for the handling of refstack vendor data
from sqlalchemy import *

db = create_engine(
    'mysql:///<user>:<password>@localhost/refstack_vendordata.db', echo=False)
metadata = MetaData(db)

company = Table('company', metadata,
                Column('id', Integer),
                Column('name', String(80)))

contact = Table('contact', metadata,
                Column('id', Integer),
                Column('company_id', String(36)),
                Column('name', String(80)),
                Column('email', String(80)))

product = Table('product', metadata,
                Column('id', String(36)),
                Column('name', String(80)),
                Column('type', Integer),
                Column('_release', String(36)),
                Column('federated', Integer),
                Column('company_id', String(36)),
                Column('_update', Integer))

result = Table('result', metadata,
               Column('id', String(36)),
               Column('tik_id', String(36)),
               Column('guideline', String(25)),
               Column('_product_id_', String(36)),
               Column('refstack', String(250)),
               Column('flagged', Integer))

ticket = Table('table', metadata,
               Column('id', String(36)),
               Column('tik_link', String(250)),
               Column('product_id', String(36)))

license = Table('license', metadata,
                Column('id', Integer),
                Column('result_id', String(36)),
                Column('link', String(250)),
                Column('type', Integer),
                Column('date', String(36)))

metadata.create_all()
