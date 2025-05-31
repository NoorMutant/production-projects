from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from flask_ckeditor import CKEditorField
from wtforms import StringField, BooleanField, SubmitField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from app.models import User

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators = [DataRequired(), Length(min = 2,max = 20)])
    email = StringField('Email',
                           validators = [DataRequired(),Email()])
    password = PasswordField('Password',
                           validators = [DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                           validators = [DataRequired(),EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user :
            raise ValidationError('Username already taken, choose another')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user :
            raise ValidationError('Email already taken')

class LoginForm(FlaskForm):
    email = StringField('Email',
                           validators = [DataRequired(),Email()])
    password = PasswordField('Password',
                           validators = [DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user and user.id != current_user.id:
            raise ValidationError('Username already taken, choose another')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user and user.id != current_user.id:
            raise ValidationError('Email already taken')

    def validate_is_admin(self, field):
        # Prevent users from modifying their own is_admin attribute
        if field.data and current_user.id == self.user.id:
            raise ValidationError('Cannot modify your own admin privileges')



class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    #content = TextAreaField('Content', validators=[DataRequired(), Length(min=1)])
    content = CKEditorField('Content',validators=[DataRequired(), Length(min=1)]) 
    def validate_content(self, content):
        # Custom validation for minimum word count (1000 words)
        min_word_count = 500
        words = len(content.data.split())
        if words < min_word_count:
            raise ValidationError(f'Content must be at least {min_word_count} words.')

        # Custom validation to check for 18+ related words
        forbidden_words = ['word1', 'word2', 'word3']  # Add your list of forbidden words
        for forbidden_word in forbidden_words:
            if forbidden_word.lower() in content.data.lower():
                raise ValidationError(f'Content contains inappropriate language: {forbidden_word}')

    submit = SubmitField('Post')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')