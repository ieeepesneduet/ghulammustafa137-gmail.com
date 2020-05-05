from bcrypt import hashpw,gensalt
from sqlalchemy import create_engine
from os import environ
from models import *
from sqlalchemy.orm import sessionmaker


db = create_engine(environ['DATABASE_URL'])
Session = sessionmaker(bind=db)
base.metadata.create_all(db)

admins = [{'email':'ali@gmail.com','password':'qwerty','head':True},{'email':'waqas@gmail.com','password':'noyoubloody','head':False}]

session = Session()
for admin in admins:
    hash = hashpw(admin['password'].encode('utf-8'),gensalt())
    session.add(Admin(admin['email'],hash,admin['head']))

session.commit()
session.close()

db.dispose()

