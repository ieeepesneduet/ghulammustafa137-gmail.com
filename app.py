import shutil
from base64 import b64encode
from functools import wraps
from os import environ
from os import path
from random import randint
import smtplib
import ssl



import requests
from bcrypt import checkpw
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, Response
from flask_sslify import SSLify
from sqlalchemy import create_engine, exc
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import load_only, defer, joinedload, sessionmaker



from models import *


port = 465
sender_email = "recruitmentpesneduet@gmail.com"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
sslify = SSLify(app)
app.config['MAX_CONTENT_LENGTH'] = 1.5 * 1024 * 1024
app.secret_key = environ['SECRET_KEY'].encode('utf8')
db = create_engine(environ['DATABASE_URL'])
Session = sessionmaker(bind=db)
context = ssl.create_default_context()


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
                return function()

        return wrapper

    return request_type


def team_area(is_json):
    def email_check(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            if 'email' in session:
                return function(*args, **kwargs)
            if is_json:
                return jsonify(err='login to access this area')
            return redirect(url_for('login'))

        return wrapper

    return email_check


def team_area2(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'email' in session:
            return function(*args, **kwargs)
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
                                about, association, why, achievements= None if achievements.lower()=='nil' else achievements)
            image_instance = Imagestore(image.read(),file_type_image)
            appl.imagestore = image_instance
            session_db.add(appl)
            try:
                session_db.commit()
            except exc.IntegrityError:
                session_db.rollback()
                session_db.close()
                return jsonify(err='email or/and cnic already registered')
            session_db.close()
            SUBJECT = "IEEE PES RECRUITMENT"
            TEXT = f"""Hi {name},
            Your IEEE PES NED Recruitment Code is pes/20/{rand_str}.

            We wish you best of luck for your interview.

            Kind Regards,
            IEEE PES NEDUET"""

            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)
            with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
                server.login(sender_email, environ.get('GMAIL_PASSWORD'))
                server.sendmail(sender_email, email, message)
            requests.get(f'https://script.google.com/macros/s/{environ.get("GOOGLE_SHEETS_KEY")}/exec',
                         params={'name': name, 'email': email, 'year': year, 'discipline': discipline, 'domain': domain,
                                 'phoneNumber': phone_number, 'code': 'pes/20/' + rand_str, 'cnic': cnic})

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
        data = session_db.query(Registration).options(load_only('name','email','year','domain','status','selection_status','reviewed')).get(request.get_json()['id'])
        if data is None:
            session_db.close()
            return jsonify(err='Invalid ID')
        else:
            dict = {'a':data.name, 'b':data.year, 'c':data.email,'d':data.domain,'j':data.reviewed}
            if data.status:
                dict['h'] = 'selected' if data.selection_status == '1' else 'not selected'
                if data.interview.show_feedback:
                    dict['i'] = data.interview.remarks
        session_db.close()
        return jsonify(dict)
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
                session['head'] = data.head
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
    return render_template('Team/home.html', title='Home', page='home', data=year_dict ,is_head=session.get('head'))


@app.route('/team/logout')
def logout():
    session.pop('email', None)
    session.pop('head',None)
    return redirect(url_for('login'))


@app.route('/team/candidates/more', methods=['POST'])
@team_area(True)
def load_more():
    if not request.is_json:
        return jsonify(err='Invalid request json')
    req_data = request.get_json()
    if not ('offset' in req_data and 'next' in req_data and 'domain' in req_data):
        return jsonify(err='missing data in request')
    data_list = []
    session_db = Session()
    if req_data.get('selectionStatus') == '3':
        query = "select name,email,year,discipline,(interview.scores[1]::INTEGER + interview.scores[2]::INTEGER + interview.scores[3]::INTEGER) as total from registration join interview on registration.id=interview.reg_id where registration.reviewed=true and registration.selection_status='3' "
        dict = {'offset': req_data.get('offset'), 'limit': req_data.get('next')}
        if not req_data.get('domain') == 'All':
            query += "and registration.domain=:domain "
            dict['domain'] = req_data.get('domain')
        query += "order by total desc limit :limit offset :offset"
        data = session_db.execute(query,dict)
        for appl in data:
            data_list.append(list(appl))
    else:
        query = session_db.query(Registration).options(load_only('name','email','phone_number','year','discipline'))
        if 'year' in req_data:
            query = query.filter(Registration.reviewed == False,Registration.status == False)
            if not req_data.get('year') == 'All':
                query = query.filter(Registration.year == req_data.get('year'))
        elif req_data.get('selectionStatus') in ['1','2']:
            query = query.filter(Registration.reviewed == True,Registration.selection_status == req_data.get('selectionStatus'))
        if not req_data.get('domain') == 'All':
            query = query.filter(Registration.domain == req_data.get('domain'))
        query = query.offset(req_data.get('offset')).limit(req_data.get('next'))
        for appl in query.all():
            data_list.append([appl.name,appl.email,appl.year,appl.discipline,appl.phone_number])
    session_db.close()
    return jsonify(data_list)


@app.route('/team/candidates/download',methods=['GET'])
@team_area(False)
def download_all():
    session_db = Session()
    data = session_db.query(Registration).all()
    session_db.close()
    def generate():
        yield 'id,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements'
        for appl in data:
            yield f"\n{appl.id},{appl.name},{appl.email},{appl.phone_number},{appl.cnic},{appl.year},{appl.domain},{appl.discipline},{appl.about},{appl.association},{appl.why},{appl.achievements}"
    return Response(generate(), mimetype='text/csv')


@app.route('/team/candidates/image/download',methods=['GET'])
@team_area(False)
def download_images_all():
    session_db = Session()
    data = session_db.query(Imagestore).all()
    session_db.close()
    for img_d in data:
        if not path.isfile(f"images_all/{img_d.reg_id}.{img_d.extension}"):
            with open(f'images_all/{img_d.reg_id}.{img_d.extension}','wb') as file:
                file.write(img_d.data)
    shutil.make_archive('images', 'zip', 'images_all')
    return send_file('images.zip',as_attachment=True,cache_timeout=0)


@app.route('/team/candidates/count',methods=['POST'])
@team_area(True)
def count_candidates():
    if not request.is_json:
        return jsonify(err='Invalid request json')
    req_data = request.get_json()
    if 'domain' not in req_data:
        return jsonify(err='Incomplete data')
    session_db = Session()
    query = session_db.query(func.count(Registration.id))
    if not req_data.get('domain') == 'All':
        query = query.filter(Registration.domain == req_data.get('domain'))
    if 'year' in req_data:
        data_count = query.filter(Registration.year == req_data.get('year'),Registration.status == False,Registration.reviewed == False).scalar()
    else:
        data_count = query.filter(Registration.reviewed == True).scalar()
    session_db.close()
    return jsonify(count=data_count)


@app.route('/team/candidates', methods=['GET'])
@team_area(False)
def candidates():
    return render_template('Team/candidates.html',title='Candidates')


@app.route('/team/candidates/candidate', methods=['GET', 'POST'])
@team_area2
def turnin():
    if request.method == 'GET':
        if 'appId' in session:
            session_db = Session()
            data = session_db.query(Registration).options(joinedload('imagestore').load_only('data'),
                                                          defer('status'),defer('reviewed'),defer('selection_status')).filter(
                Registration.id == session.get('appId'), Registration.reviewed == False,
                Registration.status == False).scalar()
            session_db.close()
            if data is None:
                session.pop('appId',None)
                return redirect(url_for('home'))
            image = b64encode(data.imagestore.data).decode("utf-8")
            return render_template('Team/interviewArea.html', data=data, page='interview_area', title='Interview Area',
                                   image=image)
        else:
            return redirect(url_for('home'))
    else:
        if 'appId' in session:
            return jsonify(err=
                           "You have not turned out the previous application.Click <a "
                           "href='/team/candidates/candidate'>here</a> to go to that form and either turn "
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
            data = session_db.query(Interview).filter(Interview.reg_id == session.get('appId')).delete()
            if data == 1:
                session_db.commit()
                json_data = jsonify()
            else:
                session_db.rollback()
                json_data = jsonify(err='No such candidate found')
            session_db.close()
            session.pop('appId', None)
        else:
            json_data = jsonify(err='First turn in to turn out')
        return json_data
    else:
        if 'appId' in session:
            experience = request.form.get('experience')
            interview = request.form.get('interview')
            potential = request.form.get('potential')
            remarks = request.form.get('remarks')
            show_feedback = request.form.get('showFeedback')
            if experience and interview and potential and remarks:
                session_db = Session()
                data = session_db.query(Interview).filter(Interview.reg_id == session.get('appId')).update(
                    {'scores': [experience, interview, potential],
                     'remarks': remarks,
                     'show_feedback':show_feedback == '1'})
                if data == 1:
                    session_db.query(Registration).filter(Registration.id == session.get('appId'),
                                                          Registration.status == False,
                                                          Registration.reviewed == False).update({'reviewed': True})
                    session_db.commit()
                    json = jsonify()
                else:
                    session_db.rollback()
                    json = jsonify(err='This applicant was stuck in interview process')
                session_db.close()
                session.pop('appId', None)
                return json
            else:
                return jsonify(err='Incomplete form submitted')
        else:
            return jsonify(err='Oops something went wrong.Try interviewing the candidate again.')


@app.route('/team/completed', methods=['GET'])
@team_area(False)
def completed():
    return render_template('Team/interview_completed.html',title='Completed Interviews', year=True,is_head=session.get('head'))


@app.route('/team/completed/selection',methods=['POST'])
@team_area(True)
def selection():
    if not request.is_json:
        return jsonify(err='Invalid request json')
    req_data = request.get_json()
    if not ('email' in req_data and req_data.get('selectionStatus') in ['1','2']):
        return jsonify(err='Incomplete data')
    session_db = Session()
    data = session_db.query(Registration).filter(Registration.email == req_data.get('email'),Registration.selection_status == '3',Registration.reviewed == True).update({'selection_status':req_data.get('selectionStatus')})
    if data == 1:
        session_db.commit()
        json = jsonify()
    else:
        session_db.rollback()
        json = jsonify(err='This record has already been dealt with by other user')
    session_db.close()
    return json

@app.route('/team/completed/download')
@team_area(False)
def download_reviewed():
    session_db = Session()
    data = session_db.query(Registration).options(joinedload(Registration.interview)).filter(Registration.reviewed == True,Registration.selection_status != '3').all()
    session_db.close()
    def generate():
        selection={'1':'selected','2':'not selected','3':'not yet reviewed'}
        yield 'id,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements,selection_status,experience,interview,potential,remarks'
        for appl in data:
            yield f"\n{appl.id},{appl.name},{appl.email},{appl.phone_number},{appl.cnic},{appl.year},{appl.domain},{appl.discipline},{appl.about},{appl.association},{appl.why},{appl.achievements},{selection.get(appl.selection_status)},{appl.interview.scores[0]},{appl.interview.scores[1]},{appl.interview.scores[2]},{appl.interview.remarks}"
    return Response(generate(), mimetype='text/csv')


@app.route("/team/candidate/stuck", methods=['POST'])
@team_area(True)
def stuck():
    email = request.form.get('email')
    if email:
        session_db = Session()
        data = session_db.query(Interview).join(Registration).filter(Registration.email == email,
                                                                                  Registration.reviewed == False,
                                                                                  Registration.status == False).delete()
        if data == 1:
            session_db.commit()
            json = jsonify()
        else:
            session_db.rollback()
            json = jsonify(err='No such applicant exists')
        session_db.close()
        return json
    return jsonify(err='no email submitted')


@app.route("/team/completed/<string:e>", methods=['GET', 'POST'])
@team_area2
def candidate_details(e):
    if request.method == 'GET':
        session_db = Session()
        data = session_db.query(Registration).options(joinedload(Registration.interview),
                                                      joinedload(Registration.imagestore)).filter(
            Registration.email == e, Registration.reviewed == True).scalar()
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
        selection_status = request.form.get('selectionStatus')
        show_feedback = request.form.get('showFeedback')
        if experience and interview and potential and remarks and selection_status in ['1', '2', '3']:
            session_db = Session()
            data1 = session_db.query(Interview).filter(Interview.reg_id == e).update(
                {Interview.scores: [experience, interview, potential], Interview.remarks: remarks,
                 Interview.show_feedback: show_feedback == '1'})
            data2 = session_db.query(Registration).filter(Registration.id == e).update(
                {Registration.selection_status: selection_status,Registration.status:False if selection_status=='3' else Registration.status})
            if data1 == 1 and data2 == 1:
                session_db.commit()
                json = jsonify()
            else:
                session_db.rollback()
                json = jsonify(err='Update Failed.No such applicant exists')
            session_db.close()
            return json
        else:
            return jsonify(err='Incomplete form submitted')


@app.route("/team/completed/release", methods=['GET'])
@team_area(True)
def release_all():
    if session.get('head'):
        session_db = Session()
        session_db.query(Registration).filter(Registration.reviewed == True, Registration.status == False,Registration.selection_status != '3').update(
            {'status': True})
        session_db.commit()
        session_db.close()
    return jsonify()


@app.route('/team/candidates/search', methods=['GET'])
@team_area(False)
def search_get():
    return render_template('Team/search.html', title='Search Page')


@app.route('/team/candidates/search/<string:e>', methods=['POST'])
@team_area(True)
def search(e):
    search_query = request.form.get('search')
    domain = request.form.get('domain')
    type_search = request.form.get('type')
    if search_query and domain and type_search and type_search in ['name', 'email', 'phone_number']:
        session_db = Session()
        data_list = []
        query = session_db.query(Registration).filter(
            getattr(Registration,
                    type_search).ilike(
                "%" + search_query + "%"))
        if e == 'records':
            query = query.options(load_only('name', 'email', 'discipline', 'phone_number', 'year', 'reviewed'))
            if not domain == 'All':
                query = query.filter(Registration.domain == domain)
            for appl in query.all():
                data_list.append(
                    [appl.name, appl.email, appl.phone_number,
                     appl.year, appl.discipline,appl.reviewed])
        elif e == 'suggestions':
            query = query.options(load_only(type_search))
            if not domain == 'All':
                query = query.filter(Registration.domain == domain)
            for appl in query.all():
                data_list.append(getattr(appl, type_search))
        session_db.close()
        return jsonify(data_list)
    else:
        return jsonify(err='Incomplete form submitted')

@app.route('/delete',methods=['GET'])
@team_area(True)
def delete_and_backup():
    if session.get('head'):
        session_db = Session()
        session_db.query(Prev_Registration).delete()
        query = 'insert into prev_registration (select id,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements,selection_status,scores,remarks from registration left join interview on registration.id=interview.reg_id)'
        session_db.execute(query)
        session_db.query(Imagestore).delete()
        session_db.query(Interview).delete()
        session_db.query(Registration).delete()
        session_db.commit()
        json_data = jsonify()
    else:
        json_data = jsonify(err = 'you donot have rights to perform deletion')
    return json_data

@app.route('/previous/download',methods=['GET'])
@team_area(False)
def download_previous():
    session_db = Session()
    data = session_db.query(Prev_Registration).all()
    session_db.close()
    def generate():
        selection = {'1': 'selected', '2': 'not selected', '3': 'not yet reviewed'}
        yield 'id,name,email,phone_number,cnic,year,domain,discipline,about,association,why,achievements,selection_status,experience,interview,potential,remarks'
        for appl in data:
            yield f"\n{appl.id},{appl.name},{appl.email},{appl.phone_number},{appl.cnic},{appl.year},{appl.domain},{appl.discipline},{appl.about},{appl.association},{appl.why},{appl.achievements},{selection.get(appl.selection_status)}"+(f",{appl.scores[0]},{appl.scores[1]},{appl.scores[2]},{appl.remarks}" if appl.scores else '')
    return Response(generate(), mimetype='text/csv')


if __name__ == '__main__':
    app.run()
