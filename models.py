from sqlalchemy import Column,String,Integer,Boolean
from sqlalchemy.ext.declarative import declarative_base
from os import environ

base = declarative_base()

class Registration(base):
    __tablename__ = 'registration'

    id = Column(Integer,primary_key=True)
    name = Column(String(32),nullable=False)
    email = Column(String(32),nullable=False,unique=True)
    phone_number = Column(String(11),nullable=False)
    cnic = Column(String(13),nullable=False,unique=True)
    year = Column(String(6),nullable=False)
    domain = Column(String(25),nullable=False)
    discipline = Column(String(30),nullable=False)
    about = Column(String,nullable=False)
    association = Column(String,nullable=False)
    why = Column(String,nullable=False)
    achievements = Column(String,nullable=True)
    status = Column(Boolean,default=False)

    def __init__(self,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.cnic = cnic
        self.year = year
        self.domain = domain
        self.discipline = discipline
        self.about = about
        self.association = association
        self.why = why
        self.achievements = achievements

if __name__ == '__main__':
    from sqlalchemy import create_engine
    db = create_engine(environ['DATABASE_URL'])
    base.metadata.create_all(db)
    db.dispose()

