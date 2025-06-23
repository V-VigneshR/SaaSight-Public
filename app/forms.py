from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    price = IntegerField('Price (USD)', validators=[NumberRange(min=0)])
    quantity = IntegerField('Available Licenses', validators=[NumberRange(min=1)])
    category = SelectField('Category', choices=[
        ('productivity', 'Productivity'),
        ('devtools', 'Developer Tools'),
        ('design', 'Design'),
        ('ai', 'AI/ML'),
        ('marketing', 'Marketing'),
        ('other', 'Other')
    ], validators=[DataRequired()])


class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        coerce=int,
        validators=[DataRequired(message="Please select a rating.")]
    )
    text = TextAreaField(
        'Review',
        validators=[DataRequired(message="Review cannot be empty.")]
    )
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role', choices=[('USER', 'User'), ('MANAGER', 'Manager')])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])