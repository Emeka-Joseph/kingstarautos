import os,random
from datetime import datetime

from flask import render_template, redirect, flash, session, request, url_for,flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignupForm, SigninForm, ListingForm, BlogForm, BusForm, TruckForm,MessageForm
from functools import wraps

from kingstar.models import Users, Contact, Vehicle, Premium_Ads, Listings, Blog, BusListings, TruckListings, Contact
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


@app.route('/')
def index():
    form = ListingForm()
    msg_form = MessageForm()
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    featured_vehicles = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = Listings.query.order_by(Listings.date_of_post.desc()).limit(50).all()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/index.html', 
                           featured_vehicles=featured_vehicles, 
                           slide=slide, 
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form, deets = deets, msg_form=msg_form)


@app.route('/buses')
def bus():
    form = BusForm()
    msg_form = MessageForm()
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    featured_vehicles = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = BusListings.query.order_by(BusListings.date_of_post.desc()).limit(50).all()
    
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/buses.html', 
                           featured_vehicles=featured_vehicles, 
                           slide=slide, 
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form, deets = deets,msg_form=msg_form)


@app.route('/trucks')
def truck():
    form = TruckForm()
    msg_form = MessageForm()
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    featured_vehicles = Vehicle.query.limit(7).all()  # Get 5 vehicles for the slider
    slide = db.session.query(Vehicle).all()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    listings = TruckListings.query.order_by(TruckListings.date_of_post.desc()).limit(50).all()
    
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/trucks.html', 
                           featured_vehicles=featured_vehicles, 
                           slide=slide, 
                           premium_ads=premium_ads_list,  # Use the list of dicts
                           listings=listings, form=form, deets = deets, msg_form=msg_form)


@app.route('/get_premium_ads')
def get_premium_ads():
    ads = Premium_Ads.query.order_by(Premium_Ads.id.desc()).all()
    return jsonify([{
        'price': ad.price,
        'year_of_prod': ad.year_of_make,
        'model': ad.model,
        'town': ad.location,
        'manufacturer': ad.manufacturer,
        'image_filename': ad.image_filename
    } for ad in ads])


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    msg_form = MessageForm()
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

    return render_template('users/signup.html', form=form, premium_ads=premium_ads_list, msg_form=msg_form)

@app.route('/signin', methods = (["GET", "POST"]), strict_slashes = False)
def signin():
    form = SigninForm()
    msg_form = MessageForm()
    if request.method=='GET':
        return render_template('users/signin.html', title="Login", form=form, msg_form=msg_form)
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



@app.route('/cars', methods=['GET','POST'])
def cars():
    msg_form = MessageForm()
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/cars.html', premium_ads=premium_ads_list, msg_form=msg_form)
    

@app.route('/about', methods=['GET','POST'])
def about():
    msg_form = MessageForm()
    cid = session.get('loggedin')
    premium_ads = Premium_Ads.query.order_by(Premium_Ads.date.desc()).limit(15).all()
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    premium_ads_list = [premium_ad_to_dict(ad) for ad in premium_ads]
    return render_template('users/about.html', premium_ads=premium_ads_list, deets=deets, msg_form=msg_form)



@app.route('/messages', methods=['GET', 'POST'])
def messages():
    msg_form = MessageForm()
    form = ListingForm()
    if msg_form.validate_on_submit():
        # Validate the form inputs
        mail=msg_form.email.data
        name=msg_form.name.data
        phone=msg_form.phone.data
        content=msg_form.message.data
        # Create a new Contact object
        new_contact = Contact(
            contact_email=mail,
            contact_name=name,
            contact_phone=phone,
            contact_content=content
        )
        
        try:
            # Add the new contact to the database
            db.session.add(new_contact)
            db.session.commit()
            flash('Your message has been sent successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending your message. Please try again.', 'error')
            app.logger.error(f'Database error: {str(e)}')
        return render_template('users/index.html', msg_form=msg_form, form=form)
    
@app.route('/post_listing', methods=['GET', 'POST'])
def post_listing():
    id = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==id).first()
    mdeets = db.session.query(Listings).filter(Listings.listing_userid==id).first()
    if id ==None:
        flash('Please log in to post a listing.', 'warning')
        return redirect(url_for('signin'))

    form = ListingForm()
    msg_form = MessageForm()
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

    return render_template('users/index.html', form=form,deets=deets, mdeets=mdeets, msg_form=msg_form)



@app.route('/post/bus', methods=['GET', 'POST'])
def post_bus():
    id = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==id).first()
    mdeets = db.session.query(BusListings).filter(BusListings.listing_userid==id).first()
    if id ==None:
        flash('Please log in to post a listing.', 'warning')
        return redirect(url_for('signin'))

    form = BusForm()
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

        new_listing = BusListings(
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
        return redirect(url_for('bus'))



@app.route('/post/truck', methods=['GET', 'POST'])
def post_truck():
    id = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==id).first()
    mdeets = db.session.query(TruckListings).filter(TruckListings.listing_userid==id).first()
    if id ==None:
        flash('Please log in to post a listing.', 'warning')
        return redirect(url_for('signin'))

    form = TruckForm()
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

        new_listing = TruckListings(
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
        return redirect(url_for('truck'))



@app.template_filter('from_json')
def from_json(value):
    return json.loads(value)

@app.route('/vehicle/<int:listing_id>')
def vehicle_details(listing_id):
    msg_form = MessageForm()
    listing = Listings.query.get_or_404(listing_id)
    seller = Users.query.get(listing.listing_userid)
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('users/vehicle_details.html', listing=listing, seller=seller, deets=deets, msg_form=msg_form)


@app.route('/bus/<int:listing_id>')
def bus_details(listing_id):
    msg_form = MessageForm()
    busl = BusListings.query.get_or_404(listing_id)
    seller = Users.query.get(busl.listing_userid)
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('users/bus_details.html', busl=busl, seller=seller, deets=deets, msg_form=msg_form)


@app.route('/trucks/<int:listing_id>')
def truck_details(listing_id):
    msg_form = MessageForm()
    truckl = TruckListings.query.get_or_404(listing_id)
    seller = Users.query.get(truckl.listing_userid)
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('users/truck_details.html', truckl=truckl, seller=seller, deets=deets, msg_form=msg_form)


@app.route('/blog')
def blog():
    msg_form = MessageForm()
    all_blogs = db.session.query(Blog).order_by(Blog.created_at.desc()).all()
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('users/blog.html', blogs=blogs, all_blogs=all_blogs, deets=deets, msg_form=msg_form)



@app.route('/blog/<int:blog_id>')
def blog_detail(blog_id):
    msg_form = MessageForm()
    blog = Blog.query.get_or_404(blog_id)
    cid = session.get('loggedin')
    deets = db.session.query(Users).filter(Users.user_id==cid).first()
    return render_template('users/blog_detail.html', blog=blog, msg_form=msg_form, deets=deets)


@app.errorhandler(404)
def pagenotfound(error):
        msg_form = MessageForm()
        if session.get('loggedin') ==None:
            flash('Please kindly re-check the route and make sure all spellings are correct','warning')
            return render_template('users/error404.html', error=error),404
        else:
            cid = session['loggedin']
            deets = db.session.query(Users).filter(Users.user_id==cid).first()
            return render_template('users/error404.html',deets=deets, error=error, msg_form=msg_form),404


@app.errorhandler(500)
def internalerror(error):
    msg_form = MessageForm()
    if session.get('loggedin') ==None:
        flash('Please kindly re-check the route and make sure all spellings are correct','warning')
        return render_template('users/error404.html', error=error),500
    else:
        cid = session['loggedin']
        alluser = db.session.query(Users).filter(Users.user_id==cid).first()
        ''' For you to see this in action, ensure the debug mode is set to False'''
        return render_template('users/error500.html',alluser=alluser, error=error, msg_form=msg_form),500


@app.errorhandler(505)
def internalerror(error):
    msg_form = MessageForm()
    cid = session['loggedin']
    alluser = db.session.query(Users).filter(Users.user_id==cid).first()
    ''' For you to see this in action, ensure the debug mode is set to False'''
    return render_template('users/error500.html',alluser=alluser, error=error, msg_form=msg_form),505