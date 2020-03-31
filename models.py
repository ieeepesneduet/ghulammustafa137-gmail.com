from sqlalchemy import Column,String,Boolean,LargeBinary,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from os import environ

base = declarative_base()

class Registration(base):
    __tablename__ = 'registration'

    id = Column(String(5),primary_key=True)
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
    imagestore = relationship("Imagestore", uselist=False, back_populates="registration")

    def __init__(self,id,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements):
        self.id = id
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


class Imagestore(base):
    __tablename__ = 'imagestore'

    reg_id = Column(String(5), ForeignKey('registration.id'),primary_key=True)
    data = Column(LargeBinary, nullable=False)
    registration = relationship("Registration", back_populates="imagestore")

    def __init__(self, data):
        self.data = data

if __name__ == '__main__':
    from sqlalchemy import create_engine
    db = create_engine(environ['DATABASE_URL'])
    base.metadata.create_all(db)
    db.dispose()

