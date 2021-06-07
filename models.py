#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate(app, db)

database_path = os.environ.get('DATABASE_URL')

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

actor_movie = db.Table('actor_movie',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.movie_id')),
    db.Column('actor_id', db.Integer, db.ForeignKey('actor.actor_id'))
)

class Movie(db.Model):
    __tablename__ = 'movie'

    movie_id = db.Column(db.Integer, primary_key=True)
    movie_name = db.Column(db.String)
    release_date = db.Column(db.Date)
    actors = db.relationship("Actor", secondary=actor_movie, back_populates="movies")

    def __repr__(self):
        return f'<Movie {self.movie_id} {self.movie_name} {self.release_date}>'

    def __init__(self, movie_name, release_date):
        self.movie_name = movie_name
        self.release_date= release_date

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'movie_id': self.movie_id,
            'movie_name': self.movie_name,
            'release_date': self.release_date
        }

class Actor(db.Model):
    __tablename__ = 'actor'

    actor_id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column(db.String)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(120))
    movies = db.relationship("Movie", secondary=actor_movie, back_populates="actors")

    def __repr__(self):
        return f'<Actor {self.actor_id} {self.actor_name} {self.age} {self.gender}>'

    def __init__(self, actor_name, age, gender):
        self.actor_name = actor_name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'actor_id': self.actor_id,
            'actor_name': self.actor_name,
            'age': self.age,
            'gender': self.gender
        }