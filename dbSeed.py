from sqlalchemy import create_engine
from os import environ
from models import *


db = create_engine(environ['DATABASE_URL'])
base.metadata.create_all(db)

db.dispose()

