from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, PasswordField,DateField,IntegerField, SelectField
from wtforms.validators import Email, DataRequired, EqualTo, Length




class RegForm(FlaskForm):
   fullname = StringField("Fullname",validators=[DataRequired(message="The firstname is a must")])  
   pwd = PasswordField("Enter Password",validators=[DataRequired()]) 
   confirmpwd = PasswordField("Confirm Password",validators=[EqualTo('pwd',message="Let the two password match")])  
   btnsubmit = SubmitField("Register!")


class EditComment(FlaskForm):
   comment = StringField("Comment",validators=[DataRequired(message="input comment")])
   btnsubmit = SubmitField("Edit")
   