from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from wtforms import StringField, FloatField, IntegerField, BooleanField, TextAreaField, FileField, SubmitField, MultipleFileField
from flask_wtf.file import FileRequired, FileAllowed


class SignupForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    user_phone = StringField('Phone Number', validators=[DataRequired(), Length(max=11)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class SigninForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class ListingForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    year_of_make = IntegerField('Year of Make', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    gear_type = StringField('Gear Type', validators=[DataRequired()])
    state_used = StringField('State Used', validators=[DataRequired()])
    registered = BooleanField('Registered')
    location = StringField('Location', validators=[DataRequired()])
    car_type = StringField('Car Type', validators=[DataRequired()])
    fuel = StringField('Fuel', validators=[DataRequired()])
    warranty = BooleanField('Warranty')
    remark = TextAreaField('Remark', validators=[Optional()])
    image = FileField('Main Image', validators=[DataRequired()])
    further_images = MultipleFileField('Additional Images (Max 10)', validators=[Optional()])
    submit = SubmitField('Post Listing')



class BusForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    year_of_make = IntegerField('Year of Make', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    gear_type = StringField('Gear Type', validators=[DataRequired()])
    state_used = StringField('State Used', validators=[DataRequired()])
    registered = BooleanField('Registered')
    location = StringField('Location', validators=[DataRequired()])
    car_type = StringField('Car Type', validators=[DataRequired()])
    fuel = StringField('Fuel', validators=[DataRequired()])
    warranty = BooleanField('Warranty')
    remark = TextAreaField('Remark', validators=[Optional()])
    image = FileField('Main Image', validators=[DataRequired()])
    further_images = MultipleFileField('Additional Images (Max 10)', validators=[Optional()])
    submit = SubmitField('Post Listing')


class TruckForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    year_of_make = IntegerField('Year of Make', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    gear_type = StringField('Gear Type', validators=[DataRequired()])
    state_used = StringField('State Used', validators=[DataRequired()])
    registered = BooleanField('Registered')
    location = StringField('Location', validators=[DataRequired()])
    car_type = StringField('Car Type', validators=[DataRequired()])
    fuel = StringField('Fuel', validators=[DataRequired()])
    warranty = BooleanField('Warranty')
    remark = TextAreaField('Remark', validators=[Optional()])
    image = FileField('Main Image', validators=[DataRequired()])
    further_images = MultipleFileField('Additional Images (Max 10)', validators=[Optional()])
    submit = SubmitField('Post Listing')



class PremiumForm(FlaskForm):
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    manufacturer = StringField('Manufacturer', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    year_of_make = IntegerField('Year of Make', validators=[DataRequired()])
    color = StringField('Color', validators=[DataRequired()])
    gear_type = StringField('Gear Type', validators=[DataRequired()])
    state_used = StringField('State Used', validators=[DataRequired()])
    registered = BooleanField('Registered')
    location = StringField('Location', validators=[DataRequired()])
    car_type = StringField('Car Type', validators=[DataRequired()])
    fuel = StringField('Fuel', validators=[DataRequired()])
    warranty = BooleanField('Warranty')
    remark = TextAreaField('Remark', validators=[Optional()])
    image = FileField('Main Image', validators=[DataRequired()])
    further_images = MultipleFileField('Additional Images (Max 10)', validators=[Optional()])
    submit = SubmitField('Post Listing')



class BlogForm(FlaskForm):
    blog_image = FileField('Blog Image', validators=[DataRequired()])
    blog_title = StringField('Blog Title', validators=[DataRequired()])
    blog_body = TextAreaField('Blog Content', validators=[DataRequired()])
    blog_category = StringField('Blog Category', validators=[DataRequired()])
    submit = SubmitField('Post Blog')