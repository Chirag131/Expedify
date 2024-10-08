from flask import Blueprint ,render_template
from flask_login import login_required, current_user


views = Blueprint('views',__name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)


@views.route('/about')
def about():
    return render_template("about.html", user=current_user)


@views.route('/dashboard')
@login_required
def dash():
    return render_template("dashboard.html",user=current_user)


@views.route('coming_soon')
def coming_soon():
    return render_template("coming_soon.html",user=current_user)