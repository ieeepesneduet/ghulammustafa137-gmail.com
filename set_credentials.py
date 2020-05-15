from bcrypt import hashpw,gensalt
from sqlalchemy import create_engine
from os import environ
from models import *
from sqlalchemy.orm import sessionmaker


db = create_engine(environ['DATABASE_URL'])
Session = sessionmaker(bind=db)

admins = [{'email':'ali@gmail.com','password':'qwerty','head':True},{'email':'waqas@gmail.com','password':'noyoubloody','head':False}]

session_db = Session()
session_db.query(Admin).delete()
for admin in admins:
    hash = hashpw(admin['password'].encode('utf-8'),gensalt())
    session_db.add(Admin(admin['email'],hash,admin['head']))

session_db.commit()
session_db.close()

db.dispose()