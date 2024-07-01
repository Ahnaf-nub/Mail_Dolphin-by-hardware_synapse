from flask import Flask, render_template, url_for, redirect, flash, abort, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from datetime import datetime
import torch
from transformers import pipeline
import re
import threading
import time


import os.path
import time
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
]

def get_message_body(msg):
    if 'parts' in msg['payload']:
        for part in msg['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text()
    else:
        return base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

def create_reply_message(original_message, reply_text):
    message_id = original_message['id']
    thread_id = original_message['threadId']
    headers = original_message['payload']['headers']
    sender = subject = ''
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
        if header['name'] == 'Subject':
            subject = header['value']

    reply_subject = "Re: " + subject if not subject.startswith("Re: ") else subject
    reply_message = MIMEText(reply_text)
    reply_message['to'] = sender
    reply_message['from'] = "me"
    reply_message['subject'] = reply_subject
    reply_message['threadId'] = thread_id

    raw_message = base64.urlsafe_b64encode(reply_message.as_bytes()).decode('utf-8')
    return {'raw': raw_message, 'threadId': thread_id}

def get_email_time(msg):
    headers = msg['payload']['headers']
    for header in headers:
        if header['name'] == 'Date':
            return header['value']
    return None

pipe = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")

import userManager
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///uD.db'
app.config['SQLALCHEMY_BINDS'] = {
    'trainData': 'sqlite:///tD.db'
}
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    dateJoined = db.Column(db.Date, default = datetime.utcnow)
    creds = db.Column(db.JSON, nullable=False, default={"gmailAuth": "none"})

class trainData(db.Model):
    __bind_key__ = 'trainData'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    generalInfo = db.Column(db.String, nullable=False)
    specReply = db.Column(db.JSON, nullable=False)
    mailTemplates = db.Column(db.JSON, nullable=False)
    mailContacts = db.Column(db.JSON, nullable=False)
    mailIntents = db.Column(db.JSON, nullable=False)
    mailHistory = db.Column(db.JSON, nullable=False)

class RegisterForm(FlaskForm):
    name = StringField(validators=[
                           InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Name"})
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email Address"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Sign-up')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            flash("Username has already been used.")
            raise ValidationError(
                'That username already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email Address"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Log-in')


def process_response(model_response):
    # Debugging output to check the input
    print("Model Response:", model_response)
    
    # Split the model_response by "assistant" and take the last segment
    segments = model_response.split("assistant|>")
    
    if len(segments) > 1:
        # Take the last segment and search for the text up to "!end"
        last_segment = segments[-1]
        match = re.search(r'(.*?)!end', last_segment, re.DOTALL)
        
        if match:
            to_post = match.group(1).strip()
        else:
            to_post = "no reply found"
    else:
        to_post = "no reply found"
    
    # Debugging output to check the result
    print("Last Segment:", last_segment if len(segments) > 1 else "None")
    print("Match Found:", match)
    print("Text to Post:", to_post)
    
    return f"{to_post}"



@app.route('/')
def landing():
    return render_template('home.html')

@app.route('/dashboard/<dashpage>', methods=['GET', 'POST'])
@login_required
def dashboard(dashpage):
    if(dashpage=="main"):
        return render_template('dashboard.html')
    elif(dashpage=="history"):
        return render_template('history.html')
    elif(dashpage=="integrate"):
        return render_template('integrate.html')
    elif(dashpage=="tune"):
        return render_template('tune.html')
    elif(dashpage=="test"):
        return render_template('test.html')
    elif(dashpage=="settings"):
        return render_template('settings.html')
    
    abort(404)

@app.route('/getnow/<datType>', methods=['GET', 'POST'])
@app.route('/getnow/<datType>/<option>', methods=['GET', 'POST'])
def getUserDat(datType, option=0):
    if(current_user.is_anonymous):
        return {}
    
    user = current_user
    userDat = trainData.query.filter_by(username=user.username).first()
    if(datType == "user"):
        return {"name": user.name, "email":user.username}
    
    if(datType == 'emails'):
        mailDat = {"dates" : ["June 26", "June 27", "June 28", "June 29", "June 30", "July 1"], "num": [1, 2, 4, 0, 6, 2]}
        print(mailDat)
        return mailDat
    if(datType == 'training'):
        dat = {"general": userDat.generalInfo, "spec": userDat.specReply["specReply"], "mailContacts": userDat.mailContacts, "mailIntents": userDat.mailIntents}
        return dat
    
    return {}

# @login_required
def getPrompt(user, usrMail):
    # user = current_user
    userDat = trainData.query.filter_by(username=user.username).first()
    genInf = userDat.generalInfo
    mails = userDat.specReply["specReply"]
    
    messages = [
            {
                "role": "system",
                "content": "You're a customer service representative for a company. You're responsible for replying to emails that come in from customers. Here's some general information about the company you're working for:\n"+genInf+"\nDo not generate any subject. Please reply to the emails you receive next.",
            }
        ]
    
    mailPrompt = ""
    for mail in mails:
        messages.append({
            "role": "user",
            "content" : "Subject:" + mail['input']['subject'] + "\n"+mail['input']['body']
        })
        messages.append({
            "role": "assistant",
            "content" : mail['output']['body']
        })
        # mailPrompt = mailPrompt + f"\n\n\nExample Email: \nSubject: {mail['input']['subject']}\n\n{mail['input']['body']}"
        # mailPrompt = mailPrompt + f"\n\nExample Reply: \n\n{mail['output']['body']}"
    messages.append(
            {
                "role": "user", 
                "content": "Subject:" + usrMail['subject'] + "\n"+usrMail['body']
            })
    # prompt = 
    print(messages)
    return messages

def generateReply(usr, subject, body):
    prompt = getPrompt(usr, {"subject": subject, "body": body})
    promptHere = pipe.tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    _reply = pipe(promptHere, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    _reply = _reply[0]["generated_text"]
    repooly = process_response(_reply+ "!end")
    return repooly
    
@login_required
@app.route('/userData', methods=['GET', 'POST'])
@app.route('/userData/<datatype>', methods=['GET', 'POST'])
def fromClient(datatype="none"):
    user = current_user
    userDat = trainData.query.filter_by(username=user.username).first()

    data = request.get_json()
    if(datatype == "trainData"):
        userDat.generalInfo = data['general']
        userDat.specReply = data['specReply']
        userDat.mailContacts = data['mailContacts']
        userDat.mailIntents = data['mailIntents']
        db.session.commit()
        return {'message': 'Data received!'}
    
    if(datatype == "testEmail"):
        repooly = generateReply(user, data['subject'], data['body'])
        # print(repooly)
        return {"reply": repooly}

    return {'message': 'Failed'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if(not current_user.is_anonymous):
        return redirect(url_for('dashboard', dashpage='main'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard', dashpage='main'))
            else:
                flash("Wrong password!")
        else:
            flash("Username unavailable!")
    return render_template('login.html', form = form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('landing'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if(not current_user.is_anonymous):
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(name = form.name.data, username=form.username.data, password=hashed_password)
        _username, _generalInfo, _specReply, _mailTemplates, _mailContacts, _mailIntents, _mailHistory =  userManager.createUserDat(new_user)

        user_data = trainData(username=_username, generalInfo=_generalInfo, specReply=_specReply, mailTemplates=_mailTemplates, mailContacts=_mailContacts, mailIntents=_mailIntents, mailHistory=_mailHistory)
        db.session.add_all([new_user, user_data])
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template('register.html', form = form)


@app.errorhandler(404)
def not_found(e): 
  return "Page not found!"

def main():
    while True:
        time.sleep(30)
        print("running")
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('gmail', 'v1', credentials=creds)
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
            messages = results.get('messages', [])
            if not messages:
                print("No unread messages found.")
            else:
                first_message_id = messages[0]['id']
                first_message = service.users().messages().get(userId='me', id=first_message_id).execute()
                
                email_time = get_email_time(first_message)
                print(f"Time of the unread email: {email_time}")
                
                try:
                    subject_here = next(header['value'] for header in first_message['payload']['headers'] if header['name'] == 'Subject')
                    print("subject was: " + subject_here)
                except StopIteration:
                    subject_here = "No Subject"
                    print("No subject header found in the first unread message.")
                email = os.getenv("USERNAME")
                user = User.query.filter_by(username=email).first()
                to_reply = generateReply(user, subject_here, get_message_body(first_message))
                reply_message = create_reply_message(first_message, to_reply)
                send_message = service.users().messages().send(userId='me', body=reply_message).execute()
                print("Replied to the first unread message with 'Ok'.")
                
                service.users().messages().modify(userId='me', id=first_message_id, body={'removeLabelIds': ['UNREAD']}).execute()
                print("Marked the first unread message as read.")
            
        except HttpError as error:
            print(f"An error occurred: {error}")



if __name__ == "__main__":
    threading.Thread(target=main, daemon=True).start()
    app.run(debug=True)