from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sqlalchemy import create_engine, exc, func
from sqlalchemy.orm import load_only, noload, joinedload
from models import *
from sqlalchemy.orm import sessionmaker
from os import environ
from random import randint
from bcrypt import checkpw
from flask_sslify import SSLify
from base64 import b64encode

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
sslify = SSLify(app)
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
        return render_template('CandidateArea/index.html', isReg=True, title='IEEE Registration')
    else:
        firstName = request.form.get('firstName')
        email = request.form.get('email')
        phoneNumber = request.form.get('phoneNumber')
        cnic = request.form.get('cnic')
        year = request.form.get('year')
        domain = request.form.get('domain')
        discipline = request.form.get('discipline')
        about = request.form.get('about')
        association = request.form.get('association')
        why = request.form.get('why')
        achievements = request.form.get('achievements')
        image = request.files.get('image')
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
        return render_template('CandidateArea/status.html', isReg=False, title='Registration Status')
    else:
        if request.is_json:
            sessionDB = Session()
            data = sessionDB.query(Registration).options(noload('imagestore')).get(request.get_json()['id'])
            if data is None:
                json = jsonify(err='Invalid ID')
            else:
                if(data.status):
                    json = jsonify(a=data.name, b=data.year, c=data.email, d=data.phone_number, e=data.cnic,
                                   f=data.domain,
                                   g=data.discipline, h=data.about, i=data.association, j=data.why, k=data.achievements,
                                   l=data.status,m=data.interview.scores[0],n=data.interview.scores[1],o=data.interview.scores[2],p=data.interview.remarks)
                else:
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
        return render_template('Team/login.html')
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
                return render_template('Team/login.html', msg=err.message)
        else:
            return render_template('Team/login.html', msg='Email and/or password empty')


@app.route('/team/home')
def home():
    if 'email' in session:
        sessionDB = Session()
        data = sessionDB.query(Registration.year, func.count(Registration.year)).group_by(Registration.year).all()
        sessionDB.close()
        yearDict = {}
        for year in data:
            yearDict[year[0]] = year[1]
        return render_template('Team/home.html', title='Home', page='home', data=yearDict)
    else:
        return redirect(url_for('login'))


@app.route('/team/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/team/candidates/<string:year>/loadmore', methods=['POST'])
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
            for application in sessionDB.query(Registration).options(
                    load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
                Registration.reviewed == False,Registration.status==False).offset(reqData['offset']).limit(
                reqData['next']):
                dataList.append(
                    [application.name,application.email,application.phone_number,
                      application.discipline,application.year])
        else:
            for application in sessionDB.query(Registration).options(
                    load_only('name', 'email', 'phone_number', 'discipline')).filter(Registration.year == year,
                                                                                     Registration.reviewed == False,Registration.status==False).offset(
                reqData['offset']).limit(reqData['next']):
                dataList.append(
                    [application.name,application.email,application.phone_number,
                     application.discipline])
        sessionDB.close()
        return jsonify(dataList)
    except ValErr as err:
        return jsonify(err=err.message)


@app.route('/team/candidates/<string:year>')
def candidates(year):
    if 'email' in session:
        sessionDB = Session()
        if year == 'All':
            dataCount = sessionDB.query(func.count(Registration.id)).filter(Registration.reviewed == False,Registration.status==False).scalar()
            data = sessionDB.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
                Registration.reviewed == False,Registration.status==False).limit(10).all()
        else:
            dataCount = sessionDB.query(func.count(Registration.id)).filter(Registration.year == year,
                                                                            Registration.reviewed == False,Registration.status==False).scalar()
            data = sessionDB.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline')).filter(Registration.year == year,
                                                                                 Registration.reviewed == False,Registration.status==False).limit(
                10).all()
        sessionDB.close()
        return render_template('Team/candidates.html', year=year, numCandidates=dataCount, candidates=data,
                               title=year + ' Year Candidates')
    else:
        return redirect(url_for('login'))


@app.route('/team/candidates/candidate/turnin', methods=['GET', 'POST'])
def turnin():
    if request.method == 'GET':
        if 'email' in session and 'appId' in session:
            sessionDB = Session()
            data = sessionDB.query(Registration).options(joinedload('imagestore'),
                                                         load_only('name', 'email', 'phone_number', 'year', 'domain',
                                                                   'discipline', 'about', 'association', 'why',
                                                                   'achievements')).filter(
                Registration.id == session['appId'],Registration.reviewed==False,Registration.status==False).scalar()
            image = b64encode(data.imagestore.data).decode("utf-8")

            sessionDB.close()
            return render_template('Team/interviewArea.html', data=data, page='interview_area', title='Interview Area',
                                   image=image)
        else:
            return redirect(url_for('login'))
    else:
        try:
            if not 'email' in session:
                raise ValErr('you need to login to turn in')
            if 'appId' in session:
                raise ValErr(
                    "You have not turned out the previous application.Click <a href='/team/candidates/candidate/turnin'>here</a> to go to that form and either turn it out or click don't want to interview")
            if not request.is_json:
                raise ValErr('Invalid request json')
            reqData = request.get_json()
            if not 'email' in reqData:
                raise ValErr('missing data in request')
            sessionDB = Session()
            data = sessionDB.query(Registration).options(load_only('id')).filter(
                Registration.email == reqData['email'],Registration.reviewed==False,Registration.status==False).scalar()
            if data is None:
                sessionDB.close()
                raise ValErr('no such record exists')
            if not data.interview is None:
                sessionDB.close()
                raise ValErr('This user has already been turned in')
            data.interview = Interview()
            session['appId'] = data.id
            sessionDB.commit()
            sessionDB.close()
            return jsonify()
        except ValErr as err:
            return jsonify(err=err.message)


@app.route('/team/candidates/candidate/turnout', methods=['GET', 'POST'])
def turnout():
    if request.method == 'GET':
        if 'appId' in session and 'email' in session:
            sessionDB = Session()
            data = sessionDB.query(Interview).filter(Interview.reg_id == session.get('appId')).scalar()
            sessionDB.delete(data)
            sessionDB.commit()
            sessionDB.close()
            session.pop('appId', None)
        return jsonify()
    else:
        if 'appId' in session and 'email' in session:
            experience = request.form.get('experience')
            interview = request.form.get('interview')
            potential = request.form.get('potential')
            remarks = request.form.get('remarks')
            if experience and interview and potential and remarks:
                sessionDB = Session()
                data = sessionDB.query(Interview).filter(Interview.reg_id == session.get('appId')).update(
                    {'scores': [experience,interview,potential],
                     'remarks': remarks})
                if data == 1:
                    sessionDB.query(Registration).filter(Registration.id == session.get('appId'),Registration.status==False,Registration.reviewed==False).update({'reviewed': True})
                    sessionDB.commit()
                    json = jsonify()
                else:
                    json = jsonify(err='This applicant was stuck in interview process')
                sessionDB.close()
                session.pop('appId', None)
                return json
            else:
                return jsonify(err='Incomplete form submitted')
        else:
            return jsonify(err='login to submit this form')
        

@app.route('/team/completed', methods=['GET', 'POST'])
def completed():
    if request.method == 'GET':
        if 'email' in session:
            sessionDB = Session()
            dataCount = sessionDB.query(func.count(Registration.id)).filter(Registration.reviewed == True,Registration.status==False).scalar()
            data = sessionDB.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
                Registration.reviewed == True,Registration.status==False).limit(10).all()
            sessionDB.close()
            return render_template('Team/interview_completed.html', numCandidates=dataCount, candidates=data,
                                   title='Completed Interviews', year=True, page='interview_completed')
        return redirect(url_for('login'))
    else:
        try:
            if not 'email' in session:
                raise ValErr('You need to login to load more')
            if not request.is_json:
                raise ValErr('Invalid request json')
            reqData = request.get_json()
            if not ('offset' in reqData and 'next' in reqData):
                raise ValErr('missing data in request')
            sessionDB = Session()
            dataList = []
            for application in sessionDB.query(Registration).options(
                    load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
                Registration.reviewed == True,Registration.status==False).offset(reqData['offset']).limit(
                reqData['next']):
                dataList.append(
                    [application.name,application.email,application.phone_number,
                     application.year,application.discipline])
            sessionDB.close()
            return jsonify(dataList)
        except ValErr as err:
            return jsonify(err=err.message)


@app.route("/team/candidate/stuck", methods=['POST'])
def stuck():
    if 'email' in session:
        email = request.form.get('email')
        if email:
            sessionDB = Session()
            data = sessionDB.query(Registration).join(Registration.interview).filter(Registration.email == email,
                                                                                     Registration.reviewed == False,Registration.status==False).scalar()
            if data is None:
                sessionDB.close()
                return jsonify(err='No such applicant exists')
            sessionDB.delete(data.interview)
            sessionDB.commit()
            sessionDB.close()
            return jsonify(msg='Success.Now you should be able to interview applicant again')
        return jsonify(err='no email submitted')
    return jsonify(err='login to submit email')


@app.route("/team/completed/<string:e>", methods=['GET', 'POST'])
def candidateDetails(e):
    if request.method == 'GET':
        if 'email' in session:
            sessionDB = Session()
            data = sessionDB.query(Registration).options(joinedload(Registration.interview),
                                                         joinedload(Registration.imagestore)).filter(
                Registration.email == e, Registration.reviewed == True,Registration.status==False).scalar()
            sessionDB.close()
            if data is None:
                return redirect(url_for('completed'))
            image = b64encode(data.imagestore.data).decode("utf-8")
            return render_template('Team/interview_details.html', data=data, page='interview_area',
                                   title='Interview Details', image=image)
        else:
            return redirect(url_for('login'))
    else:
        experience = request.form.get('experience')
        interview = request.form.get('interview')
        potential = request.form.get('potential')
        remarks = request.form.get('remarks')
        if experience and interview and potential and remarks:
            sessionDB = Session()
            data = sessionDB.query(Interview).filter(Interview.reg_id == e).update(
                {'scores': [experience, interview, potential], 'remarks': remarks})
            sessionDB.commit()
            sessionDB.close()
            if data == 1:
                return jsonify()
            else:
                return jsonify(err='Update Failed.No such applicant exists')
        else:
            return jsonify(err='Incomplete form submitted')


@app.route("/team/completed/release/all",methods=['GET'])
def releaseAll():
    if 'email' in session:
        sessionDB = Session()
        sessionDB.query(Registration).filter(Registration.reviewed==True,Registration.status==False).update({'status':True})
        sessionDB.commit()
        sessionDB.close()
    return redirect(url_for('completed'))


if __name__ == '__main__':
    app.run()
