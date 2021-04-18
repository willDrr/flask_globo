from flask import Blueprint, session, g, has_request_context, request, current_app, make_response, render_template, flash, redirect, url_for
from app.auth.forms import RegistrationForm, LoginForm, PasswordResetForm, UpdatePasswordForm
from app import db
from app.models import User, Role
from werkzeug.local import LocalProxy
from itsdangerous.url_safe import URLSafeSerializer
from functools import wraps
from app.emails import send_activation_mail, send_password_reset_mail
from flask.ctx import has_request_context

auth = Blueprint("auth", __name__, template_folder="templates")

current_user = LocalProxy(lambda: get_current_user()) 

def login_required(f):
    @wraps(f)
    def _login_required(*args, **kwargs):
        if current_user.is_anonymous():
            flash("You need to be logged in to access this page", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return _login_required

def role_required(role):
    def _role_required(f):
        @wraps(f)
        def __role_required(*args, **kwargs):
            if not current_user.is_role(role):
                flash("You are not authorized to access this page", "danger")
                return redirect(url_for("main.home"))
            return f(*args, **kwargs)
        return __role_required
    return _role_required

def activation_required(f):
    @wraps(f)
    def _activation_required(*args, **kwargs):
        if not current_user.is_active():
            flash("Only activated users have access to this page", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return _activation_required    

@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        if user.check_password(password):
            flash("You are successfully loged in", "success")
            login_user(user) 
            if form.remember_me.data:
                resp = make_response(redirect(url_for("main.home")))
                remember_token = user.get_remember_token()
                db.session.commit()
                resp.set_cookie('remember_token', encrypt_cookie(remember_token), max_age=60*60*24*100)
                resp.set_cookie('user_id', encrypt_cookie(user.id), max_age=60*60*24*100)
                return resp 
            return redirect(url_for("main.home")) # name of the blueprint before the home view
        else:
            form.password.errors.append("The password is not correct")

    return render_template("login.html", form=form)

@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        username    = form.username.data
        email       = form.email.data
        password    = form.password.data
        location    = form.location.data
        description = form.description.data
        role        = form.role.data

        user = User(username, email, password, location, description, role)
        db.session.add(user)
        db.session.commit()
        flash("You are registered", "success")
        login_user(user)
        user.create_token_for("activation")
        db.session.commit()
        send_activation_mail(user)
        return redirect(url_for("main.home"))

    return render_template("register.html", form=form)

@auth.route("/activate/<token>")
@login_required
def activate_account(token):
    if current_user.is_active():
        return redirect(url_for("main.home"))
    if current_user.activate(token):
        db.session.commit()
        flash("Your account is confirmed. Welcome " + current_user.username + " to the page", "success")
    else:
        flash("The confirmation link is not valid or it has expired", "danger")
    return redirect(url_for("main.home")) 
    
@auth.route("/send_activation")
@login_required
def send_activation():
    if current_user.is_active():
        return redirect(url_for("main.home"))
    current_user.create_token_for("activation")
    db.session.commit()
    send_activation_mail(current_user)
    flash("New email has been sent. Please confirm your account", "success")
    return redirect(url_for("main.home"))         

@auth.route("/password_reset", methods=["GET", "POST"])
def password_reset():
    if current_user.is_authenticated():
        return redirect(url_for("main.home"))
    
    form = PasswordResetForm()
    if form.validate_on_submit():
        email = form.email.data
        user  = User.query.filter_by(email=email).first()
        user.create_token_for("reset")
        db.session.commit()
        send_password_reset_mail(user)
        flash("The password reset instructions are sent to your email", "success")
        return redirect(url_for("main.home"))
    
    return render_template("password_reset.html", form=form)

@auth.route("/update_password/<token>/<email>", methods=["GET", "POST"])
def update_password(token, email):
    if current_user.is_authenticated():
        return redirect(url_for("main.home")) 
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_reset_token(token):
        flash("The password reset link is not valid or it has expired", "danger")
        return redirect(url_for("main.home")) 
    
    form = UpdatePasswordForm()
    
    if form.validate_on_submit():
        password        = form.password.data
        user.password   = password
        user.reset_hash = ""
        db.session.add(user)
        db.session.commit()
        
        flash("New password is set! You can now login to your account", "success")
        return redirect(url_for("auth.login")) 
    
    flash("Hi " +  user.username + "! You can now set a new password for the account", "success")
    return render_template("update_password.html", form=form, token=token, email=email)

# find bug related to cookies not being deleted from browser 
@auth.route("/logout")
@login_required
def logout():
    current_user.forget()
    db.session.commit()
    resp = make_response(redirect(url_for("main.home")))
    resp.set_cookie("remember_token", "", max_age=0)
    resp.set_cookie("user_id", "", max_age=0) 
    logout_user()
    flash("You are logged out", "success")
    return resp
 

def login_user(user):
    session["user_id"] = user.id
    
# pop the user session from the hashmap    
def logout_user():
    session.pop("user_id")
    
@auth.app_context_processor
def inject_current_user():
    if has_request_context():
        return dict(current_user=get_current_user())
    return dict(current_user="")     

@auth.app_context_processor
def inject_roles():
    return dict(Role=Role)
    
# if _current_user is None and session.get("user_id"):
def get_current_user():
    _current_user = getattr(g, "_current_user", None)  # using g context to avoid extra calls to the DB; Memoization
    if _current_user is None:
        if session.get("user_id"):
            user = User.query.get(session.get("user_id"))              
            if user:
                _current_user = g._current_user = user
        elif request.cookies.get("user_id"):
            decrypted_cookie = int(decrypt_cookie(request.cookies.get("user_id")))
            user = User.query.get(decrypted_cookie)
            if user and user.check_remember_token(decrypt_cookie(request.cookies.get("remember_token"))):
                login_user(user)
                _current_user = g._current_user = user                
                  
    if _current_user is None:
        _current_user = User()
    return _current_user

def encrypt_cookie(content):    
    s = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cookie")
    encrypt_content = s.dumps(content)
    return encrypt_content

def decrypt_cookie(encrypted_content):
    s = URLSafeSerializer(current_app.config["SECRET_KEY"], salt="cookie")
    try:
        content = s.loads(encrypted_content)
    except BadSignature as bs:
        print("Bad signature error: "+ bs)
        content = "-1"
    return content
    
    
