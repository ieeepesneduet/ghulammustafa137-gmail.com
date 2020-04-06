from flask import Flask, render_template, request, jsonify, session,redirect,url_for
from sqlalchemy import create_engine, exc,func
from sqlalchemy.orm import load_only,noload
from models import *
from sqlalchemy.orm import sessionmaker
from os import environ
from random import randint
from bcrypt import checkpw


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 - 1
app.secret_key = b'\x01Jt\xbc!E5k\x8b]\xe1\xdd0p\xb7Q'
db = create_engine(environ['DATABASE_URL'])
Session = sessionmaker(bind=db)


def file_type(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower()


def randomStringGenerator():
    allStr = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    randStr = [0, 1, 2, 3, 4]
    for i in randStr:
        randStr[i] = allStr[randint(0, 61)]
    return ''.join(randStr)


@app.route('/candidatearea/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'GET':
        return render_template('CandidateArea/index.html',isReg=True,title='IEEE Registration')
    else:
        firstName = request.form['firstName']
        email = request.form['email']
        phoneNumber = request.form['phoneNumber']
        cnic = request.form['cnic']
        year = request.form['year']
        domain = request.form['domain']
        discipline = request.form['discipline']
        about = request.form['about']
        association = request.form['association']
        why = request.form['why']
        achievements = request.form['achievements']
        image = request.files['image']
        if firstName and email and phoneNumber and len(phoneNumber) == 11 and cnic and len(
                cnic) == 13 and year and domain and discipline and about and association and why and achievements and image:
            fileType = file_type(image.filename)
            if fileType and fileType in ALLOWED_EXTENSIONS:
                sessionDB = Session()
                while True:
                    randStr = randomStringGenerator()
                    data = sessionDB.query(Registration).get(randStr)
                    if data is None:
                        break

                application = Registration(randStr, firstName, email, phoneNumber, cnic, year, domain, discipline,
                                           about, association, why, achievements)
                imageInstance = Imagestore(image.read())
                application.imagestore = imageInstance
                sessionDB.add(application)
                try:
                    sessionDB.commit()
                except exc.IntegrityError:
                    sessionDB.rollback()
                    sessionDB.close()
                    return jsonify(err='email or/and cnic already registered')
                sessionDB.close()
                return jsonify(id=randStr)
            else:
                return jsonify(err='Please upload a .jpg/.png image')
        else:
            return jsonify(err='Your form is incomplete')


@app.route('/candidatearea/status', methods=['GET', 'POST'])
def status():
    if request.method == 'GET':
        return render_template('CandidateArea/status.html',isReg=False,title='Registration Status')
    else:
        if request.is_json:
            sessionDB = Session()
            data = sessionDB.query(Registration).options(noload('imagestore')).get(request.get_json()['id'])
            if data is None:
                sessionDB.close()
                return jsonify(err='Invalid ID')
            json = jsonify(a=data.name, b=data.year, c=data.email, d=data.phone_number, e=data.cnic, f=data.domain,
                           g=data.discipline, h=data.about, i=data.association, j=data.why, k=data.achievements,
                           l=data.status)
            sessionDB.close()
            return json
        else:
            return jsonify(err='Error parsing data')


class ValErr(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


@app.route('/team/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'email' in session:
            return redirect(url_for('home'))
        return render_template('Team/login.html',title='Login')
    else:
        email = request.form['email']
        password = request.form['password']
        if email and password:
            sessionDB = Session()
            try:
                data = sessionDB.query(Admin).get(email)
                if data is None:
                    raise ValErr('Wrong email entered')
                if not checkpw(password.encode('utf-8'), data.password):
                    raise ValErr('Wrong password entered')
                sessionDB.close()
                session['email'] = email
                return redirect(url_for('home'))
            except ValErr as err:
                sessionDB.close()
                return render_template('Team/login.html',msg=err.message,title='Login')
        else:
            return render_template('Team/login.html',msg='Email and/or password empty',title='Login')


@app.route('/team/home')
def home():
    if 'email' in session:
        return render_template('Team/home.html',isHome=True,title='Home')
    else:
        return redirect(url_for('login'))


@app.route('/team/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/team/chart')
def chart():
    sessionDB = Session()
    data = sessionDB.query(Registration.year,func.count(Registration.year)).group_by(Registration.year).all()
    sessionDB.close()
    yearDict = {}
    for year in data:
        yearDict[year[0]] = year[1]
    return jsonify(yearDict)


@app.route('/team/candidate/<string:year>/loadmore',methods=['POST'])
def loadMore(year):
    try:
        if not 'email' in session:
            raise ValErr('you need to login to load more records')
        if not request.is_json:
            raise ValErr('Invalid request json')
        reqData = request.get_json()
        if not ('offset' in reqData and 'next' in reqData):
            raise ValErr('missing data in request')
        sessionDB = Session()
        dataList = []
        if year == 'All':
            for application in sessionDB.query(Registration).options(load_only('name','email','phone_number','discipline','year')).offset(reqData['offset']).limit(reqData['next']):
                dataList.append({'name': application.name, 'email': application.email,'phone_number': application.phone_number,'year':application.year,'discipline':application.discipline})
        else:
            for application in sessionDB.query(Registration).options(load_only('name','email','phone_number','discipline')).filter(Registration.year == year).offset(reqData['offset']).limit(reqData['next']):
                dataList.append({'name': application.name, 'email': application.email,'phone_number': application.phone_number,'discipline':application.discipline})
        sessionDB.close()
        return jsonify(dataList)
    except ValErr as err:
        return jsonify(err=err.message)


@app.route('/team/candidate/<string:year>')
def candidate(year):
    if 'email' in session:
        sessionDB = Session()
        if year=='All':
            dataCount = sessionDB.query(func.count(Registration.id)).scalar()
            data = sessionDB.query(Registration).options(load_only('name','email','phone_number','discipline','year')).limit(10).all()
        else:
            dataCount = sessionDB.query(func.count(Registration.id)).filter(Registration.year == year).scalar()
            data = sessionDB.query(Registration).options(load_only('name','email','phone_number','discipline')).filter(Registration.year == year).limit(10).all()
        sessionDB.close()
        return render_template('Team/candidate.html',year=year,numCandidates=dataCount,candidates=data)

    else:
        return render_template('Team/login.html',msg='You need to login first to access this area')




if __name__ == '__main__':
    app.run()
