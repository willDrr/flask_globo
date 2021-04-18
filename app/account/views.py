from flask import Blueprint, render_template, flash, url_for, redirect
from app.auth.views import current_user, activation_required, login_required, logout_user
from app.models import User, Role, Gig
from app import db
from werkzeug.utils import escape, unescape
from app.account.forms import UpdateAccountForm

account = Blueprint("account", __name__, template_folder="templates") 

@account.route("/profile/<username>")
@login_required
@activation_required
def show(username):
    user = User.query.filter_by(username=username).first()
    gigs = None
    if user.is_role(Role.EMPLOYER):
        gigs = user.gigs.all()
    if user.is_role(Role.MUSICIAN):
        gigs = user.applied_gigs.all()
    return render_template("show_account.html", user=user, gigs=gigs)

@account.route("/edit", methods=["GET", "POST"])
@login_required
@activation_required
def edit():
    form = UpdateAccountForm()
    
    if form.validate_on_submit():
        current_user.location = escape(form.location.data)
        current_user.description = escape(form.description.data)
        db.session.add(current_user._get_current_object()) # getting real user object from proxy outside of the application context        
        db.session.commit()
        flash("Your account has been updated", "success")
        return redirect(url_for("account.show", username=current_user.username))
    
    form.location.data = unescape(current_user.location)
    form.description.data = unescape(current_user.description)
    return render_template("edit_account.html", form=form) 


@account.route("/delete", methods=["POST"])
@login_required
@activation_required
def delete():
    db.session.delete(current_user._get_current_object())
    db.session.commit()
    logout_user()
    flash("Your account has been deleted", "success")
    return redirect(url_for("main.home"))  