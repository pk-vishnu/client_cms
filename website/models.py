from . import db
from datetime import datetime
from flask_login import UserMixin 

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150),unique=True)
    password = db.Column(db.String(100))
    username = db.Column(db.String(100))
    
class Blogger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    
    RESPONSE_DELIMITER = '|||'
    
    @property
    def response_list(self):
        if self.response:
            return self.response.split(self.RESPONSE_DELIMITER)
        return []

    @response_list.setter
    def response_list(self, value):
        if value:
            self.response = self.RESPONSE_DELIMITER.join(value)
        else:
            self.response = ''