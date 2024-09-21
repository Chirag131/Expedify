import requests
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint('auth', __name__)

# Your GitHub username that users need to follow
YOUR_GITHUB_USERNAME = 'bytemait'

# Function to scrape followers from a user's GitHub profile
def getFollowers():
    url = "https://github.com/orgs/bytemait/followers"
    text = requests.get(url).text
    soup = BeautifulSoup(text, "html.parser")
    items = soup.find_all(class_="Link--secondary pl-1")
    item2 = soup.find_all(class_="Link--secondary")
    
    followers = []
    for item in items:
        followers.append(item.get_text().strip().lower())
    for item in item2:
        followers.append(item.get_text().strip().lower())
    return followers


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        GitHub_username = request.form.get('GitHub_username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(GitHub_username) < 2:
            flash('GitHub Username must be greater than 2 characters.', category='error')
        elif password1 != password2:
            flash("Passwords don't match.", category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            # Scrape your GitHub followers page
            followers = getFollowers()  # Pass the GitHub username here
            
            if GitHub_username.lower() not in followers:
                flash('You must follow the GitHub account to create an account.', 'error')
                return render_template('signup.html', user=current_user, follow_required=True)

            # Account creation logic if user follows you
            new_user = User(email=email, GitHub_username=GitHub_username, password=generate_password_hash(password1, method='scrypt'))
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully!', category='success')
            login_user(new_user, remember=True)
            return redirect(url_for('views.dash'))

    return render_template('signup.html', user=current_user)




@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        GitHub_username = request.form.get('GitHub_username')
        password = request.form.get('password')

        # Check if user exists in the database
        user = User.query.filter_by(GitHub_username=GitHub_username).first()

        if user:
            # Check if the password matches
            if check_password_hash(user.password, password):
                
                # Scrape the user's GitHub followers list to verify they still follow you
                followers = getFollowers()
                
                if GitHub_username.lower() not in followers:
                    # If they don't follow you, flash a message and redirect them to GitHub
                    flash('You must follow the GitHub account to log in.', category='error')
                    return redirect(f'https://github.com/{YOUR_GITHUB_USERNAME}')
                
                # If they follow you, allow them to log in
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.dash'))
            else:
                flash("Incorrect password.", category='error')
        else:
            flash("User does not exist.", category='error')

    return render_template("login.html", user=current_user)
