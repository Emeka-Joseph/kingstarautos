from datetime import datetime
from kingstar import db 
from sqlalchemy.dialects.mysql import JSON


class Users(db.Model):
    user_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    user_fname = db.Column(db.String(100),nullable=False)
    user_lname = db.Column(db.String(100),nullable=False)
    user_email = db.Column(db.String(120), unique=True) 
    user_datereg=db.Column(db.DateTime(), default=datetime.utcnow)
    user_name = db.Column(db.String(100),nullable=False)
    user_pwd=db.Column(db.String(120),nullable=False)
    user_phone = db.Column(db.Integer)
    

class Admin(db.Model):
    admin_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_fullname = db.Column(db.String(100),nullable=False)
    admin_email = db.Column(db.String(120)) 
    admin_password=db.Column(db.String(120),nullable=False)




class Contact(db.Model):
    contact_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
    contact_email = db.Column(db.String(100),nullable=False)
    contact_name =db.Column(db.String(255),nullable=True)
    contact_subject = db.Column(db.String(80),nullable=True)
    contact_content = db.Column(db.String(255), nullable=True)


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    

class Premium_Ads(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    year_of_prod = db.Column(db.Integer, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    town = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<Premium_Ad {self.model}>'



class Listings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(200), nullable=False)
    manufacturer = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    year_of_make = db.Column(db.Integer, nullable=False)
    color = db.Column(db.String(50), nullable=False)
    gear_type = db.Column(db.String(50), nullable=False)
    state_used = db.Column(db.String(100), nullable=False)
    registered = db.Column(db.Boolean, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    car_type = db.Column(db.String(100), nullable=False)
    fuel = db.Column(db.String(50), nullable=False)
    warranty = db.Column(db.Boolean, nullable=False)
    remark = db.Column(db.Text, nullable=True)
    date_of_post = db.Column(db.DateTime, default=datetime.utcnow)
    further_images = db.Column(JSON, nullable=True)
    #listing_userid = db.Column(db.Integer)
    #listing_userid = db.Column(db.Integer, db.ForeignKey('user.id'))
    listing_userid = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)

    def __repr__(self):
        return f'<Listing {self.manufacturer} {self.model}>'