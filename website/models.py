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
    title = db.Column(db.String(100), nullable=False)
    content_md = db.Column(db.Text, nullable=False)
    content_html = db.Column(db.Text) 
    thumbnail = db.Column(db.String(255))  
    author = db.Column(db.String(50), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.LargeBinary, nullable=False)
    image_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False, unique=True)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content_md = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    images = db.relationship('ProductImage', backref='product', lazy=True)

class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    image_data = db.Column(db.LargeBinary, nullable=False)
    image_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False, unique=True)
    
class Description(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    