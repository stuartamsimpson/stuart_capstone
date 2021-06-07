from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField
from wtforms.fields.core import DateField
from wtforms.validators import DataRequired

class ActorMovieForm(FlaskForm):
    actor_id = StringField(
        'actor_id'
    )
    movie_id = StringField(
        'movie_id'
    )

class MovieForm(FlaskForm):
    movie_name = StringField(
        'movie_name', validators=[DataRequired()]
    )
    release_date = DateField(
        'release_date',
        validators=[DataRequired()],
        default= date.today()
    )

class ActorForm(FlaskForm):
    actor_name = StringField(
        'actor_name', validators=[DataRequired()]
    )
    age = StringField(
        'age', validators=[DataRequired()]
    )
    gender = SelectField(
        'gender', validators=[DataRequired()],
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        ]
    )
