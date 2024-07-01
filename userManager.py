from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

def createUserDat(user):
    username = user.username
    generalInfo = "Add some general information about yourself / your company so it can be useful to the AI to learn about you and therefore send emails on your behalf."
    specReply = {"specReply": [
        {
            "name":"Give an example name", 
            "input":{
                "subject":" ",
                "body": "#Example input email body",
            },
            "output":{
                "body": "#Example reply email body"
            }
        }
    ]}
    mailTemplates = {"mailTemplates": [
        {
            "subject": " ",
            "body": " "
        }
    ]}
    mailContacts = {
        "reply": True,
        "contacts": []
    }
    mailIntents = {
        "reply": True,
        "intents": []
    }
    mailHistory = {"mailHistory": [
        {
            "date": " ",
            "time": " ",
            "subject": " ",
            "body": " "
        }
    ]}

    return username, generalInfo, specReply, mailTemplates, mailContacts, mailIntents, mailHistory