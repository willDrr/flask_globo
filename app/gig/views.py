from flask import Blueprint, render_template, request, flash, abort, url_for, redirect
from app.auth.views import current_user, activation_required, login_required, role_required
from app import db
from app.models import User, Role, Gig
from werkzeug.utils import escape, unescape
from app.gig.forms import CreateGigForm, UpdateGigForm
from functools import wraps

gig = Blueprint("gig", __name__, template_folder="templates") 

def gig_owner_required(f):
    @wraps(f)
    def _gig_owner_required(*args, **kwargs):
        gig = Gig.query.filter_by(slug=request.view_args["slug"]).first()
        if not gig or not current_user.is_gig_owner(gig):
            flash("You are not the owner of that gig.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return _gig_owner_required

@gig.route("/create", methods=["GET", "POST"])
@login_required
@role_required(Role.EMPLOYER)
@activation_required
def create():
    form = CreateGigForm()

    if form.validate_on_submit():
        title        = escape(form.title.data)
        description = escape(form.description.data)
        payment        = form.payment.data
        location    = escape(form.location.data)

        gig = Gig(title, description, payment, location, current_user.id)
        db.session.add(gig)
        db.session.commit()
        flash("The new gig has been added. \""+ gig.title +"\"", "success")
        return redirect(url_for("gig.show", slug=gig.slug))

    return render_template("create_gig.html", form=form)

@gig.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
@role_required(Role.EMPLOYER)
@gig_owner_required
@activation_required
def edit(slug):
    form = UpdateGigForm()

    gig = Gig.query.filter_by(slug=slug).first()

    if form.validate_on_submit():
        gig.title        = escape(form.title.data)
        gig.description = escape(form.description.data)
        gig.payment        = form.payment.data
        gig.location    = escape(form.location.data)

        db.session.add(gig)
        db.session.commit()
        flash("The gig is updated.", "success")
        return redirect(url_for("gig.show", slug=gig.slug))

    form.title.data            = unescape(gig.title)
    form.description.data     = unescape(gig.description)
    form.payment.data        = gig.payment
    form.location.data        = unescape(gig.location)
    return render_template("edit_gig.html", gig=gig, form=form)

@gig.route("/delete/<slug>", methods=["POST"])
@login_required
@role_required(Role.EMPLOYER)
@gig_owner_required
@activation_required
def delete(slug):
    gig = Gig.query.filter_by(slug=slug).first()
    db.session.delete(gig)
    db.session.commit()
    flash("The gig was deleted", "success")
    return redirect(url_for("main.home")) 

@gig.route("/info/<slug>")
@login_required
def show(slug):
    gig = Gig.query.filter_by(slug=slug).first()
    if not gig:
        abort(404)
    musicians = gig.musicians.all()
    return render_template("show_gig.html", gig=gig, musicians=musicians)

@gig.route("/my_gigs")
@login_required
@activation_required
def my_gigs():
    gigs = None
    if current_user.is_role(Role.MUSICIAN):
        gigs = current_user.applied_gigs.all()
    if current_user.is_role(Role.EMPLOYER):
        gigs = current_user.gigs.all()
        
    return render_template("my_gigs.html", gigs=gigs)

@gig.route("/apply/<slug>", methods=["POST"])
@login_required
@role_required(Role.MUSICIAN)
@activation_required
def apply_to_gig(slug):
    gig = Gig.query.filter_by(slug=slug).first()
    if not gig:
        abort(404)
        
    current_user.apply(gig)
    db.session.commit()
    
    flash("You just applied to the gig: \"" + gig.title + "\".", "success")
    return redirect(request.referrer)
     