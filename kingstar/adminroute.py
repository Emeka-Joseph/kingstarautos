import os,random
from datetime import datetime

from flask import render_template, redirect, flash, session, request, url_for,flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignupForm, SigninForm, ListingForm, BlogForm, PremiumForm, MessageForm
from functools import wraps

from kingstar.models import Users, Contact, Vehicle, Premium_Ads, Listings, Blog
from kingstar import app, db
from werkzeug.utils import secure_filename
from flask import jsonify

from sqlalchemy.sql import text
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import requests
import json

from sqlalchemy.exc import IntegrityError

from sqlalchemy import desc,asc,or_,func

import string

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/kingstarautos'
app.config['UPLOAD_FOLDER'] = 'kingstar/static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


if not os.path.exists(os.path.join(app.static_folder, 'uploads')):
    os.makedirs(os.path.join(app.static_folder, 'uploads'))

def generate_name(): 
    filename = random.sample(string.ascii_lowercase,10) 
    return ''.join(filename)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def premium_ad_to_dict(ad):
    return {
        'id': ad.id,
        'image_filename': ad.image_filename,
        'manufacturer': ad.manufacturer,
        'model': ad.model,
        'price': float(ad.price),  # Convert to float if needed
        'year_of_make': ad.year_of_make,
        'color': ad.color,
        'gear_type': ad.gear_type,
        'state_used': ad.state_used,
        'registered': ad.registered,
        'location': ad.location,
        'car_type': ad.car_type,
        'fuel': ad.fuel,
        'warranty': ad.warranty,
        'remark': ad.remark,
        'date': ad.date.isoformat() if ad.date else None,  # Convert datetime to ISO format string
        'further_images': ad.further_images,
        'listing_userid': ad.listing_userid
    }


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def first_25_words(text):
    words = text.split()
    return ' '.join(words[:25]) + ('...' if len(words) > 25 else '')

app.jinja_env.filters['first_25_words'] = first_25_words

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "Admin_kingstar" and password == "admin_kingstarautos@2024":
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('admin/admin_login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    form = BlogForm()
    allusers = Users.query.all()
    allblogs = Blog.query.all()
    return render_template('admin/index.html', allusers=allusers, form=form, allblogs=allblogs)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))



@app.route('/blogs')
def blogs():
     msg_form = MessageForm()
     if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
     else:
        form = BlogForm()
        blog_posts = Blog.query.all()
        cid = session.get('loggedin')
        deets = db.session.query(Users).filter(Users.user_id==cid).first()
        return render_template('admin/add_blog.html', blog_posts=blog_posts, form=form, deets=deets, msg_form=msg_form)
    

@app.route('/blog/add', methods=['GET', 'POST'])
@admin_required
def add_blog():
    form = BlogForm()
    msg_form = MessageForm()
    if form.validate_on_submit():
        try:
            # Handle file upload
            if form.blog_image.data:
                filename = secure_filename(form.blog_image.data.filename)
                form.blog_image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = url_for('static', filename=f'uploads/{filename}')
            else:
                image_path = None  # Or a default image path

            new_blog = Blog(
                blog_image=image_path,
                blog_title=form.blog_title.data,
                blog_body=form.blog_body.data,
                blog_category=form.blog_category.data
            )
            db.session.add(new_blog)
            db.session.commit()
            flash('Your blog post has been created!', 'success')
            return redirect(url_for('blogs'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'error')
            app.logger.error(f'Error adding blog post: {str(e)}')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {getattr(form, field).label.text}: {error}", 'error')
    return render_template('admin/index.html', form=form, msg_form=msg_form)


@app.route('/premium')
def premium():
    form = PremiumForm()
    msg_form = MessageForm()
    cid = session.get('admin_logged_in')
    #deets = db.session.query(Users).filter(Users.user_id==cid).first()
    deets = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    #slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(50).all()
    
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('admin/premium.html',
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form, msg_form=msg_form, deets=deets)


@app.route('/premium_ads', methods=['GET', 'POST'])
def premium_ads():
    form = PremiumForm()
    msg_form = MessageForm()
    cid = session.get('admin_logged_in')
    deets = db.session.query(Users).all()

    #featured_vehicles = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    #slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(50).all()
    
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('admin/premium_ads.html',
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form,deets=deets, msg_form=msg_form)




@app.route('/post/premium', methods=['GET', 'POST'])
def post_premium():
    id = session.get('admin_logged_in')
    #deets = db.session.query(Users).filter(Users.user_id==id).first()
    #mdeets = db.session.query(TruckListings).filter(TruckListings.listing_userid==id).first()
    if id ==None:
        flash('Please log in to post a listing.', 'warning')
        return redirect(url_for('admin_login'))
    form = PremiumForm()
    if form.validate_on_submit():
        main_image = form.image.data
        main_image_filename = secure_filename(main_image.filename)
        main_image.save(os.path.join(app.config['UPLOAD_FOLDER'], main_image_filename))
        further_images = form.further_images.data
        further_image_filenames = []
        for image in further_images[:10]:  # Limit to 10 images
            if image:
                filename = secure_filename(image.filename)
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                further_image_filenames.append(filename)

        new_listing = Premium_Ads(
            image_filename=main_image_filename,
            further_images=json.dumps(further_image_filenames),  # Store as JSON string
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            price=form.price.data,
            year_of_make=form.year_of_make.data,
            color=form.color.data,
            gear_type=form.gear_type.data,
            state_used=form.state_used.data,
            registered=form.registered.data,
            location=form.location.data,
            car_type=form.car_type.data,
            fuel=form.fuel.data,
            warranty=form.warranty.data,
            remark=form.remark.data,
            listing_userid=id
        )
        db.session.add(new_listing)
        db.session.commit()
        flash('Your premium listing has been posted successfully!', 'success')
    return redirect(url_for('premium'))
        

@app.route('/premium/<int:premium_id>')
def premium_details(premium_id):
    msg_form = MessageForm()
    prem = Premium_Ads.query.get_or_404(premium_id)
    #deets = Users.query.get(busl.listing_userid)
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('admin/premium_details.html', prem=prem, deets=deets, msg_form=msg_form)


@app.route('/upload', methods=['GET', 'POST'])
def upload_vehicle():
    msg_form = MessageForm()
    
    deets = db.session.query(Users).all()

    if request.method == 'POST':
        name = request.form['name']
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            upload_folder = os.path.join(app.root_path, 'static', 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            image_path = os.path.join(upload_folder, filename)
            try:
                image.save(image_path)
                print(f"Image saved to: {image_path}")  # Debug print
            except Exception as e:
                print(f"Error saving image: {e}")  # Debug print
                return "Error saving image", 500
            
            new_vehicle = Vehicle(name=name, image_url=filename)
            db.session.add(new_vehicle)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return "Invalid file", 400
    
    return render_template('admin/upload_vehicle.html', deets=deets, msg_form=msg_form)



