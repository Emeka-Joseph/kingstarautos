import os,random
from datetime import datetime

from flask import render_template, redirect, flash, session, request, url_for,flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignupForm, SigninForm, ListingForm
from functools import wraps

from kingstar.models import Users, Contact, Vehicle, Premium_Ads, Listings
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
        'price': float(ad.price),  # Convert Decimal to float
        'year_of_prod': ad.year_of_prod,
        'model': ad.model,
        'town': ad.town,
        'state': ad.state
    }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('signin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    form = ListingForm()
    featured_vehicles = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = Listings.query.order_by(Listings.date_of_post.desc()).limit(50).all()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/index.html', 
                           featured_vehicles=featured_vehicles, 
                           slide=slide, 
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = Users(
            user_fname=form.first_name.data,
            user_lname=form.last_name.data,
            user_email=form.email.data,
            user_name=form.username.data,
            user_pwd=hashed_password,
            user_phone=form.user_phone.data
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created successfully!', 'success')
            return redirect(url_for('signin'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')

    return render_template('users/signup.html', form=form, premium_ads=premium_ads_list)

@app.route('/signin', methods = (["GET", "POST"]), strict_slashes = False)
def signin():
    form = SigninForm()
    if request.method=='GET':
        return render_template('users/signin.html', title="Login", form=form)
    else:
        if form.validate_on_submit:
            email = form.email.data
            password = form.password.data
            if email !="" and password !="":
                user = db.session.query(Users).filter(Users.user_email==email).first() 
                if user !=None:
                    pwd =user.user_pwd
                    chk = check_password_hash(pwd, password)
                    if chk:
                        id = user.user_id
                        session['loggedin'] = id
                        return redirect(url_for('index'))
                    else:
                        flash('Invalid email or password', "danger")
                        return redirect(url_for('signin'))
                else:
                    flash("Ensure that your login details are correct, or signup to create an account", "danger")  
                    return redirect(url_for('signin'))     
        else:
            flash("You must complete all fields", "danger")
            return redirect(url_for("signup"))
        

@app.route('/signout')
def signout():
    session.pop('loggedin', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/upload', methods=['GET', 'POST'])
def upload_vehicle():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
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
            
            new_vehicle = Vehicle(name=name, image_url=filename, price=price)
            db.session.add(new_vehicle)
            db.session.commit()
            
            return redirect(url_for('index'))
        else:
            return "Invalid file", 400
    
    return render_template('users/upload_vehicle.html')


@app.route('/post_premium_ad', methods=['POST'])
def post_premium_ad():
    if request.method == 'POST':
        try:
            price = float(request.form['price'])
            year_of_prod = int(request.form['year_of_prod'])
            model = request.form['model']
            town = request.form['town']
            state = request.form['state']
            image = request.files['image']

            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                upload_folder = os.path.join(app.root_path, 'static', 'uploads')
                
                # Ensure the upload folder exists
                if not os.path.exists(upload_folder):
                    os.makedirs(upload_folder)
                
                image_path = os.path.join(upload_folder, filename)
                
                # Save the image
                image.save(image_path)
                
                # Check if the file was actually saved
                if not os.path.exists(image_path):
                    raise Exception(f"Failed to save image at {image_path}")

                print(f"Image saved successfully at: {image_path}")  # Debug print

                new_ad = Premium_Ads(price=price, year_of_prod=year_of_prod, model=model,
                                     town=town, state=state, image_filename=filename)
                db.session.add(new_ad)
                db.session.commit()

                return jsonify({'success': True, 'message': 'Premium Ad posted successfully'})
            else:
                raise Exception("Invalid file type or no file provided")

        except Exception as e:
            print(f"Error posting Premium Ad: {str(e)}")  # Debug print
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Error posting Premium Ad: {str(e)}'}), 400

    return jsonify({'success': False, 'message': 'Invalid request method'}), 405


@app.route('/cars', methods=['GET','POST'])
def cars():
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/cars.html', premium_ads=premium_ads_list)
    


@app.route('/post_listing', methods=['GET', 'POST'])
def post_listing():
    id = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==id).first()
    mdeets = db.session.query(Listings).filter(Listings.listing_userid==id).first()
    if id ==None:
        flash('Please log in to post a listing.', 'warning')
        return redirect(url_for('signin'))

    form = ListingForm()
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

        new_listing = Listings(
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

        flash('Your listing has been posted successfully!', 'success')
        #return redirect(url_for('listings'))  # Redirect to a page showing all listings

    return render_template('users/index.html', form=form,deets=deets, mdeets=mdeets)

@app.template_filter('from_json')
def from_json(value):
    return json.loads(value)

@app.route('/vehicle/<int:listing_id>')
def vehicle_details(listing_id):
    listing = Listings.query.get_or_404(listing_id)
    seller = Users.query.get(listing.listing_userid)
    return render_template('users/vehicle_details.html', listing=listing, seller=seller)


@app.route('/get_premium_ads')
def get_premium_ads():
    ads = Premium_Ads.query.order_by(Premium_Ads.id.desc()).all()
    return jsonify([{
        'price': ad.price,
        'year_of_prod': ad.year_of_prod,
        'model': ad.model,
        'town': ad.town,
        'state': ad.state,
        'image_filename': ad.image_filename
    } for ad in ads])



@app.errorhandler(404)
def pagenotfound(error):
        if session.get('loggedin') ==None:
            flash('Please kindly re-check the route and make sure all spellings are correct','warning')
            return render_template('users/error404.html', error=error),404
        else:
            cid = session['loggedin']
            alluser = db.session.query(Users).filter(Users.user_id==cid).first()
            return render_template('users/error404.html',alluser=alluser, error=error),404


@app.errorhandler(500)
def internalerror(error):
    if session.get('loggedin') ==None:
        flash('Please kindly re-check the route and make sure all spellings are correct','warning')
        return render_template('users/error404.html', error=error),500
    else:
        cid = session['loggedin']
        alluser = db.session.query(Users).filter(Users.user_id==cid).first()
        ''' For you to see this in action, ensure the debug mode is set to False'''
        return render_template('users/error500.html',alluser=alluser, error=error),500


@app.errorhandler(505)
def internalerror(error):
    cid = session['loggedin']
    alluser = db.session.query(Users).filter(Users.user_id==cid).first()
    ''' For you to see this in action, ensure the debug mode is set to False'''
    return render_template('users/error500.html',alluser=alluser, error=error),505