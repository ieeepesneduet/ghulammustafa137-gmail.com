from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sqlalchemy import create_engine, exc, func
from sqlalchemy.orm import load_only, noload, joinedload, sessionmaker
from models import *
from os import environ
from random import randint
from bcrypt import checkpw
from flask_sslify import SSLify
from base64 import b64encode
from functools import wraps

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


def random_string_generator():
    all_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    rand_str = [0, 1, 2, 3, 4]
    for i in rand_str:
        rand_str[i] = all_str[randint(0, 61)]
    return ''.join(rand_str)


class ValErr(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


def candidate_area(path, is_reg, title):
    def request_type(function):
        @wraps(function)
        def wrapper():
            if request.method == 'GET':
                return render_template(path, is_reg=is_reg, title=title)
            else:
                return func()

        return wrapper

    return request_type


def team_area(is_json):
    def email_check(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if 'email' in session:
                return func(*args, **kwargs)
            if is_json:
                return jsonify(err='login to access this area')
            return redirect(url_for('login'))

        return wrapper

    return email_check


def team_area2(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'email' in session:
            return func(*args, **kwargs)
        if request.method == 'POST':
            return jsonify(err='login to access this area')
        return redirect(url_for('login'))

    return wrapper




@app.route('/candidatearea/registration', methods=['GET', 'POST'])
@candidate_area('CandidateArea/index.html', is_reg=True, title='IEEE Registration')
def registration():
    name = request.form.get('name')
    email = request.form.get('email')
    phone_number = request.form.get('phoneNumber')
    cnic = request.form.get('cnic')
    year = request.form.get('year')
    domain = request.form.get('domain')
    discipline = request.form.get('discipline')
    about = request.form.get('about')
    association = request.form.get('association')
    why = request.form.get('why')
    achievements = request.form.get('achievements')
    image = request.files.get('image')
    if name and email and phone_number and len(phone_number) == 11 and cnic and len(
            cnic) == 13 and year and domain and discipline and about and association and why and achievements and image:
        file_type_image = file_type(image.filename)
        if file_type_image and file_type_image in ALLOWED_EXTENSIONS:
            session_db = Session()
            while True:
                rand_str = random_string_generator()
                data = session_db.query(Registration).get(rand_str)
                if data is None:
                    break

            appl = Registration(rand_str, name, email, phone_number, cnic, year, domain, discipline,
                                about, association, why, achievements)
            image_instance = Imagestore(image.read())
            appl.imagestore = image_instance
            session_db.add(appl)
            try:
                session_db.commit()
            except exc.IntegrityError:
                session_db.rollback()
                session_db.close()
                return jsonify(err='email or/and cnic already registered')
            session_db.close()
            return jsonify(id=rand_str)
        else:
            return jsonify(err='Please upload a .jpg/.png image')
    else:
        return jsonify(err='Your form is incomplete')


@app.route('/candidatearea/status', methods=['GET', 'POST'])
@candidate_area('CandidateArea/status.html', is_reg=False, title='Registration Status')
def status():
    if request.is_json:
        session_db = Session()
        data = session_db.query(Registration).options(noload('imagestore')).get(request.get_json()['id'])
        if data is None:
            json = jsonify(err='Invalid ID')
        else:
            if data.status:
                json = jsonify(a=data.name, b=data.year, c=data.email, d=data.phone_number, e=data.cnic,
                               f=data.domain,
                               g=data.discipline, h=data.about, i=data.association, j=data.why, k=data.achievements,
                               l=data.status, m=data.interview.scores[0], n=data.interview.scores[1],
                               o=data.interview.scores[2], p=data.interview.remarks)
            else:
                json = jsonify(a=data.name, b=data.year, c=data.email, d=data.phone_number, e=data.cnic,
                               f=data.domain,
                               g=data.discipline, h=data.about, i=data.association, j=data.why, k=data.achievements,
                               l=data.status)
        session_db.close()
        return json
    else:
        return jsonify(err='Error parsing data')


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
            session_db = Session()
            try:
                data = session_db.query(Admin).get(email)
                if data is None:
                    raise ValErr('Wrong email entered')
                if not checkpw(password.encode('utf-8'), data.password):
                    raise ValErr('Wrong password entered')
                session_db.close()
                session['email'] = email
                return redirect(url_for('home'))
            except ValErr as err:
                session_db.close()
                return render_template('Team/login.html', msg=err.message)
        else:
            return render_template('Team/login.html', msg='Email and/or password empty')


@app.route('/team/home', methods=['GET'])
@team_area(False)
def home():
    session_db = Session()
    data = session_db.query(Registration.year, func.count(Registration.year)).group_by(Registration.year).all()
    session_db.close()
    year_dict = {}
    for year in data:
        year_dict[year[0]] = year[1]
    return render_template('Team/home.html', title='Home', page='home', data=year_dict)


@app.route('/team/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/team/candidates/<string:year>/loadmore', methods=['POST'])
@team_area(True)
def load_more(year):
    if not request.is_json:
        return jsonify('Invalid request json')
    req_data = request.get_json()
    if not ('offset' in req_data and 'next' in req_data):
        return jsonify('missing data in request')
    session_db = Session()
    data_list = []
    if year == 'All':
        for appl in session_db.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
            Registration.reviewed == False, Registration.status == False).offset(req_data.get('offset')).limit(
            req_data.get('next')):
            data_list.append(
                [appl.name, appl.email, appl.phone_number,
                 appl.discipline, appl.year])
    else:
        for appl in session_db.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline')).filter(Registration.year == year,
                                                                                 Registration.reviewed == False,
                                                                                 Registration.status == False).offset(
            req_data.get('offset')).limit(req_data.get('next')):
            data_list.append(
                [appl.name, appl.email, appl.phone_number,
                 appl.discipline])
    session_db.close()
    return jsonify(data_list)


@app.route('/team/candidates/<string:year>', methods=['GET'])
@team_area(False)
def candidates(year):
    if year not in ['All', 'First', 'Second', 'Third', 'Fourth']:
        return redirect(url_for('home'))
    session_db = Session()
    if year == 'All':
        data_count = session_db.query(func.count(Registration.id)).filter(Registration.reviewed == False,
                                                                          Registration.status == False).scalar()
        data = session_db.query(Registration).options(
            load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
            Registration.reviewed == False, Registration.status == False).limit(10).all()
    else:
        data_count = session_db.query(func.count(Registration.id)).filter(Registration.year == year,
                                                                          Registration.reviewed == False,
                                                                          Registration.status == False).scalar()
        data = session_db.query(Registration).options(
            load_only('name', 'email', 'phone_number', 'discipline')).filter(Registration.year == year,
                                                                             Registration.reviewed == False,
                                                                             Registration.status == False).limit(
            10).all()
    session_db.close()
    return render_template('Team/candidates.html', year=year, numCandidates=data_count, candidates=data,
                           title=year + ' Year Candidates')


@app.route('/team/candidates/candidate/turnin', methods=['GET', 'POST'])
@team_area2
def turnin():
    if request.method == 'GET':
        if 'appId' in session:
            session_db = Session()
            data = session_db.query(Registration).options(joinedload('imagestore'),
                                                          load_only('name', 'email', 'phone_number', 'year', 'domain',
                                                                    'discipline', 'about', 'association', 'why',
                                                                    'achievements')).filter(
                Registration.id == session['appId'], Registration.reviewed == False,
                Registration.status == False).scalar()
            image = b64encode(data.imagestore.data).decode("utf-8")

            session_db.close()
            return render_template('Team/interviewArea.html', data=data, page='interview_area', title='Interview Area',
                                   image=image)
        else:
            return redirect(url_for('home'))
    else:
        if 'appId' in session:
            return jsonify(err=
                           "You have not turned out the previous application.Click <a "
                           "href='/team/candidates/candidate/turnin'>here</a> to go to that form and either turn "
                           "it out or click don't want to interview")
        if not request.is_json:
            return jsonify(err='Invalid request json')
        req_data = request.get_json()
        if 'email' not in req_data:
            return jsonify(err='missing data in request')
        session_db = Session()
        data = session_db.query(Registration).options(load_only('id')).filter(
            Registration.email == req_data.get('email'), Registration.reviewed == False,
            Registration.status == False).scalar()
        if data is None or data.interview is not None:
            session_db.close()
            return jsonify(err='This user has already been turned in')
        data.interview = Interview()
        session['appId'] = data.id
        session_db.commit()
        session_db.close()
        return jsonify()


@app.route('/team/candidates/candidate/turnout', methods=['GET', 'POST'])
@team_area(True)
def turnout():
    if request.method == 'GET':
        if 'appId' in session:
            session_db = Session()
            data = session_db.query(Interview).filter(Interview.reg_id == session.get('appId')).scalar()
            session_db.delete(data)
            session_db.commit()
            session_db.close()
            session.pop('appId', None)
        return jsonify()
    else:
        if 'appId' in session:
            experience = request.form.get('experience')
            interview = request.form.get('interview')
            potential = request.form.get('potential')
            remarks = request.form.get('remarks')
            if experience and interview and potential and remarks:
                session_db = Session()
                data = session_db.query(Interview).filter(Interview.reg_id == session.get('appId')).update(
                    {'scores': [experience, interview, potential],
                     'remarks': remarks})
                if data == 1:
                    session_db.query(Registration).filter(Registration.id == session.get('appId'),
                                                          Registration.status == False,
                                                          Registration.reviewed == False).update({'reviewed': True})
                    session_db.commit()
                    json = jsonify()
                else:
                    json = jsonify(err='This applicant was stuck in interview process')
                session_db.close()
                session.pop('appId', None)
                return json
            else:
                return jsonify(err='Incomplete form submitted')
        else:
            return jsonify(err='Oops something went wrong.Try interviewing the candidate again.')


@app.route('/team/completed', methods=['GET', 'POST'])
@team_area2
def completed():
    if request.method == 'GET':
        session_db = Session()
        data_count = session_db.query(func.count(Registration.id)).filter(Registration.reviewed == True,
                                                                          Registration.status == False).scalar()
        data = session_db.query(Registration).options(
            load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
            Registration.reviewed == True, Registration.status == False).limit(10).all()
        session_db.close()
        return render_template('Team/interview_completed.html', numCandidates=data_count, candidates=data,
                               title='Completed Interviews', year=True)
    else:
        if not request.is_json:
            return jsonify(err='Invalid request json')
        req_data = request.get_json()
        if not ('offset' in req_data and 'next' in req_data):
            return jsonify(err='missing data in request')
        session_db = Session()
        data_list = []
        for appl in session_db.query(Registration).options(
                load_only('name', 'email', 'phone_number', 'discipline', 'year')).filter(
            Registration.reviewed == True, Registration.status == False).offset(req_data.get('offset')).limit(
            req_data.get('next')):
            data_list.append(
                [appl.name, appl.email, appl.phone_number,
                 appl.year, appl.discipline])
        session_db.close()
        return jsonify(data_list)


@app.route("/team/candidate/stuck", methods=['POST'])
@team_area(True)
def stuck():
    email = request.form.get('email')
    if email:
        session_db = Session()
        data = session_db.query(Registration).join(Registration.interview).filter(Registration.email == email,
                                                                                  Registration.reviewed == False,
                                                                                  Registration.status == False).scalar()
        if data is None:
            session_db.close()
            return jsonify(err='No such applicant exists')
        session_db.delete(data.interview)
        session_db.commit()
        session_db.close()
        return jsonify()
    return jsonify(err='no email submitted')


@app.route("/team/completed/<string:e>", methods=['GET', 'POST'])
@team_area2
def candidate_details(e):
    if request.method == 'GET':
        session_db = Session()
        data = session_db.query(Registration).options(joinedload(Registration.interview),
                                                      joinedload(Registration.imagestore)).filter(
            Registration.email == e, Registration.reviewed == True, Registration.status == False).scalar()
        session_db.close()
        if data is None:
            return redirect(url_for('completed'))
        image = b64encode(data.imagestore.data).decode("utf-8")
        return render_template('Team/interview_details.html', data=data, page='interview_area',
                               title='Interview Details', image=image)
    else:
        experience = request.form.get('experience')
        interview = request.form.get('interview')
        potential = request.form.get('potential')
        remarks = request.form.get('remarks')
        if experience and interview and potential and remarks:
            session_db = Session()
            data = session_db.query(Interview).filter(Interview.reg_id == e).update(
                {'scores': [experience, interview, potential], 'remarks': remarks})
            session_db.commit()
            session_db.close()
            if data == 1:
                return jsonify()
            else:
                return jsonify(err='Update Failed.No such applicant exists')
        else:
            return jsonify(err='Incomplete form submitted')


@app.route("/team/completed/release/all", methods=['GET'])
@team_area(False)
def release_all():
    session_db = Session()
    session_db.query(Registration).filter(Registration.reviewed == True, Registration.status == False).update(
        {'status': True})
    session_db.commit()
    session_db.close()
    return redirect(url_for('completed'))


@app.route('/team/candidates/candidate/search', methods=['GET'])
@team_area(False)
def search_get():
    return render_template('Team/search.html', title='Search Page')


@app.route('/team/candidates/candidate/search/<string:e>', methods=['POST'])
@team_area(True)
def search(e):
    search_query = request.form.get('search')
    domain = request.form.get('domain')
    type_search = request.form.get('type')
    if search_query and domain and type_search and type_search in ['name', 'email', 'phone_number']:
        session_db = Session()
        data_list = []
        if e == 'records':
            data = session_db.query(Registration).options(
                load_only('name', 'email', 'discipline', 'phone_number', 'year')).filter(
                Registration.reviewed == False, Registration.status == False, Registration.domain == domain,
                func.lower(getattr(Registration, type_search)) == search_query.lower()).all()
            for appl in data:
                data_list.append(
                    [appl.name, appl.email, appl.phone_number,
                     appl.year, appl.discipline])
        elif e == 'suggestions':
            data = session_db.query(Registration).options(load_only(type_search)).filter(
                Registration.reviewed == False,
                Registration.status == False,
                Registration.domain == domain,
                getattr(Registration,
                        type_search).ilike(
                    "%" + search_query + "%")).all()
            for appl in data:
                data_list.append(getattr(appl, type_search))
        session_db.close()
        return jsonify(data_list)
    else:
        return jsonify(err='Incomplete form submitted')


if __name__ == '__main__':
    app.run()