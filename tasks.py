from celery import Celery
from os import environ
import smtplib
import ssl
import requests

context = ssl.create_default_context()
port = 465
sender_email = "recruitmentpesneduet@gmail.com"
celeryapp = Celery('tasks',broker='sqla+'+environ['DATABASE_URL'])

@celeryapp.task
def background_registration(name,email,year,domain,discipline,phone_number,cnic,rand_str):
    message = f"""\
     Subject: IEEE PES RECRUITMENT

     Hi {name},

     Your IEEE PES NED Recruitment Code is pes/20/{rand_str}.

     We wish you best of luck for your interview.

     Kind Regards,
     IEEE PES NEDUET"""
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, environ.get('GMAIL_PASSWORD'))
        server.sendmail(sender_email, 'ghulammustafa137@gmail.com', message)
    requests.get(f'https://script.google.com/macros/s/{environ.get("GOOGLE_SHEETS_KEY")}/exec',
                 params={'name': name, 'email': email, 'year': year, 'discipline': discipline, 'domain': domain,
                         'phoneNumber': phone_number, 'code': 'pes/20/' + rand_str, 'cnic': cnic})
