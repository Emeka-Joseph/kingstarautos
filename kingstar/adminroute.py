import os,random
from datetime import datetime

from flask import render_template, redirect, flash, session, request, url_for,flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .forms import SignupForm, SigninForm, ListingForm, BlogForm
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
     if 'admin_logged_in' not in session:
        return redirect(url_for('admin_login'))
     else:
        form = BlogForm()
        blog_posts = Blog.query.all()
        cid = session.get('loggedin')
        deets = db.session.query(Users).filter(Users.user_id==cid).first()
        return render_template('admin/add_blog.html', blog_posts=blog_posts, form=form, deets=deets)
    

@app.route('/blog/add', methods=['GET', 'POST'])
def add_blog():
    form = BlogForm()
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
    return render_template('admin/index.html', form=form)
