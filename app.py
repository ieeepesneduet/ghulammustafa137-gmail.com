from flask import Flask,render_template,request,jsonify
from sqlalchemy import create_engine,exc
from models import *
from sqlalchemy.orm import sessionmaker
from os import path,environ


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app = Flask(__name__)
db = create_engine(environ['DATABASE_URL'])
# f"postgresql://{environ['USERNAME']}:{environ['PASSWORD']}@localhost:5432/ieee"
Session = sessionmaker(bind=db)
session = Session()

def file_type(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower()

@app.route('/registration',methods=['GET','POST'])
def registration():
    if request.method == 'GET':
        return render_template('index.html')
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
        if firstName and email and phoneNumber and cnic and year and domain and discipline and about and association and why and achievements and image:
            fileType = file_type(image.filename)
            if fileType and fileType in ALLOWED_EXTENSIONS:
                application = Registration(firstName,email,phoneNumber,cnic,year,domain,discipline,about,association,why,achievements)
                session.add(application)
                try:
                    session.commit()
                except exc.IntegrityError:
                    return jsonify(err='email or/and cnic already registered')
                image.save(path.join('./static/images/applicants',str(application.id)+'.'+fileType))
                return jsonify(id=application.id)
            else:
                return jsonify(err='Please upload a .jpg/.png image')
        else:
            return jsonify(err='Your form is incomplete')


@app.route('/status',methods=['GET','POST'])
def status():
    if request.method == 'GET':
        return render_template('status.html')
    else:
        if request.is_json:
            data = session.query(Registration).get(request.get_json()['id'])
            if data is None:
                return jsonify(err='Invalid ID')
            return jsonify(a=data.name,b=data.year,c=data.email,d=data.phone_number,e=data.cnic,f=data.domain,g=data.discipline,h=data.about,i=data.association,j=data.why,k=data.achievements,l=data.status)
        else:
            return jsonify(err='Error parsing data')


if __name__ == '__main__':
    app.run()
