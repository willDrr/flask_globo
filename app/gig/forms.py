from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, DecimalField
from wtforms.validators import InputRequired, DataRequired, Length
from wtforms.widgets import Input
from markupsafe import Markup


class PriceInput(Input):
    input_type = "number"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        kwargs.setdefault("step", "0.01")
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return Markup("""<div class="input-group mb-3">
            <div class="input-group-prepend">
                        <span class="input-group-text">$</span>
                    </div>
                    <input %s>
        </div>""" % self.html_params(name=field.name, **kwargs))

class PriceField(DecimalField):
    widget = PriceInput()

class GigForm(FlaskForm):
    title          = StringField("Title", validators=[ InputRequired("Input is required!"), DataRequired("Data is required!"),
                                                    Length(min=5, max=80, message="Title must be between 5 and 80 characters long")])
    description    = TextAreaField("Description", validators=[ InputRequired("Input is required!"), DataRequired("Data is required!"),
                                                           Length(min=10, max=200, message="Description must be between 10 and 200 characters long")])
    payment        = PriceField("Payment")
    location       = StringField("Location", validators=[ InputRequired("Input is required!"), DataRequired("Data is required!"),
                                                      Length(min=3, max=40, message="Location must be between 3 and 40 characters long")])
    
    
class CreateGigForm(GigForm):
    submit         = SubmitField("Create gig")

class UpdateGigForm(GigForm):
    submit         = SubmitField("Update gig")    