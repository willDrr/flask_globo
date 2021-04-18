from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Length


class UpdateAccountForm(FlaskForm):
    location = StringField("Your location (e.g. city, country)", validators=[ InputRequired("Input is required!"), DataRequired("Data is required!"),
                                                                             Length(min=3, max=40, message="Location must be between 3 and 40 characters long")])
    description = TextAreaField("Description *", validators=[ InputRequired("Input is required!"), DataRequired("Data is required!"),
                                                             Length(min=10, max=200, message="Description must be between 10 and 200 characters long")])
    submit = SubmitField("Update")
