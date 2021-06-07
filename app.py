from json import dump
import os
from flask import Flask, request, abort, jsonify, json, render_template, flash, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

from models import setup_db, db, Movie, Actor, actor_movie
from forms import *
from auth.auth import AuthError, requires_auth
from werkzeug.exceptions import NotFound, MethodNotAllowed, UnprocessableEntity, HTTPException

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

FULLPATH_AUTH0_DOMAIN = 'https://' + os.environ.get('AUTH0_DOMAIN')

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  # Set up CORS. Allow '*' for origins and set Access-Control-Allow
    CORS(app, resources={r"/api/*":{"origins":"*"}})
    
    
    oauth = OAuth(app)

    auth0 = oauth.register(
        'auth0',
        client_id=os.environ.get('AUTH0_CLIENT_ID'),
        client_secret=os.environ.get('AUTH0_CLIENT_SECRET'),
        api_base_url=FULLPATH_AUTH0_DOMAIN,
        access_token_url=FULLPATH_AUTH0_DOMAIN + '/oauth/token',
        authorize_url=FULLPATH_AUTH0_DOMAIN + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    app.config.from_object('config')

    @app.route('/')
    @cross_origin()
    def index():
        return render_template('pages/home.html')

    @app.route('/login')
    @cross_origin()
    def login():
        return auth0.authorize_redirect(redirect_uri=os.environ.get('AUTH0_CALLBACK_URL'), audience=os.environ.get('AUTH0_AUDIENCE'))

    # Here we're using the /callback route.
    @app.route('/callback')
    @cross_origin()
    def callback_handling():
        # Handles response from token endpoint
        token = auth0.authorize_access_token()
        session['token'] = token['access_token']
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        # Store the user information in flask session.
        session['jwt_payload'] = userinfo
        session['profile'] = {
            'user_id': userinfo['sub'],
            'name': userinfo['name'],
            'picture': userinfo['picture']
        }
        return redirect('/')

    @app.route('/logout')
    @cross_origin()
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {'returnTo': url_for('index', _external=True), 'client_id': os.environ.get('AUTH0_CLIENT_ID')}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

    @app.route("/authorization/url", methods=["GET"])
    @cross_origin()
    def generate_auth_url():
        print(os.environ)
        url = f'https://' + os.environ.get("AUTH0_DOMAIN") + '/authorize' \
            f'?audience=' + os.environ.get('AUTH0_AUDIENCE') + '' \
            f'&response_type=token&client_id=' \
            f'' + os.environ.get('AUTH0_CLIENT_ID') + '&redirect_uri=' \
            f'' + os.environ.get('AUTH0_CALLBACK_URL')
            
        return jsonify({
            'url': url
        })

    #  ----------------------------------------------------------------
    #  Movies
    #  ----------------------------------------------------------------

    @app.route('/movies', methods=['GET'])
    @cross_origin()
    @requires_auth('get:movies')
    def movies(payload):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            movie_query = Movie.query.all()
            data = []
            for movie in movie_query:
                data.append({
                "id": movie.movie_id,
                "movie_name": movie.movie_name,
                "release_date": movie.release_date
                })
            return render_template('pages/movies.html', movies=data), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/movies/create', methods=['GET'])
    @cross_origin()
    @requires_auth('post:movies')
    def create_movie_form(payload):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            form = MovieForm()
            return render_template('forms/new_movie.html', form=form), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/movies/create', methods=['POST'])
    @cross_origin()
    @requires_auth('post:movies')
    def create_movie_submission(payload):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed
            form = MovieForm(request.form, meta={'csrf': False})
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)
        if form.validate():
            error = False
            try:
                new_movie = Movie(
                    movie_name = form.movie_name.data,
                    release_date = form.release_date.data
                )
                new_movie.insert()
            except:
                error = True
                db.session.rollback()
            finally:
                db.session.close()
                # on successful db insert, flash success
                if error:
                    flash('An error occurred. Movie ' + form.movie_name.data + ' could not be listed.')
                else:
                    flash('Movie ' + form.movie_name.data + ' was successfully listed!')
                return render_template('pages/home.html'), 200
        else:
            message = []
            error_fields = ''
            for field, errors in form.errors.items():
                message.append(field + ': (' + '|'.join(errors) + ')')
                error_fields += field + ', '
            error_fields = error_fields[:-2]
            flash('The Movie data is not valid. Please try again! Errors are in '+error_fields)
            return render_template('pages/home.html')

    @app.route('/movies/<int:movie_id>', methods=['GET'])
    @cross_origin()
    @requires_auth('post:movies')
    def show_movie(payload, movie_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            data = db.session.query(Movie).filter(Movie.movie_id==movie_id).first()
            return render_template('pages/show_movie.html', movie=data), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/movies/<int:movie_id>/edit', methods=['GET'])
    @cross_origin()
    @requires_auth('patch:movies')
    def edit_movie(payload, movie_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            movie = Movie.query.get(movie_id)
            form = MovieForm(obj=movie)

            return render_template('forms/edit_movie.html', form=form, movie=movie), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)


    @app.route('/movies/<int:movie_id>/edit', methods=['POST'])
    @cross_origin()
    @requires_auth('patch:movies')
    def edit_movie_submission(payload, movie_id):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed
            movie = Movie.query.get(movie_id)
            form = MovieForm(request.form, meta={'csrf': False})
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)
        if form.validate():
            error = False
            try:
                # update the movie data from form
                form.populate_obj(movie)
                movie.update()
            except:
                error = True
                db.session.rollback()
                flash('Error! Movie ' + movie.movie_name + ' could not be listed.')
            finally:
                db.session.close()
                # on successful db insert, flash success
                if error:
                    flash('An error occurred. Movie ' + form.movie_name.data + ' could not be updated.')
                else:
                    flash('Movie ' + form.movie_name.data + ' was successfully updated')
                #return redirect(url_for('show_movie', movie_id=movie_id))
                return render_template('pages/home.html')
        else:
            message = []
            error_fields = ''
            for field, errors in form.errors.items():
                message.append(field + ': (' + '|'.join(errors) + ')')
                error_fields += field + ', '
                error_fields = error_fields[:-2]
                flash('The Movie data is not valid. Please try again! Errors are in '+error_fields)
            #return redirect(url_for('show_movie', movie_id=movie_id))
            return render_template('pages/home.html')

    @app.route('/movies/<int:movie_id>/delete', methods=['GET'])
    @cross_origin()
    @requires_auth('delete:movies')
    def delete_movie(payload, movie_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            movie = Movie.query.get(movie_id)
            if movie is None:
                raise NotFound
            movie.delete()
            return render_template('pages/home.html')
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route("/movies/postrequest", methods=['POST'])
    @cross_origin()
    @requires_auth("post:movies")
    def create_movie_from_request(payload):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed

            movie_data = request.get_json()
            # if all data not submitted then raise error
            if 'movie_name' and 'release_date' not in movie_data:
                raise UnprocessableEntity
            new_movie_name = movie_data.get('movie_name')
            new_release_date = movie_data.get('release_date')
            new_movie = Movie(movie_name=new_movie_name, release_date=new_release_date)
            new_movie.insert()
            return jsonify({
                'success': True,
                'movie_id': new_movie.movie_id,
                'movie': new_movie.movie_name
            })
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/movies/<int:movie_id>/deleterequest', methods=['DELETE'])
    @cross_origin()
    @requires_auth('delete:movies')
    def delete_movie_deleterequest(payload, movie_id):
        try:
            if not request.method == 'DELETE':
                raise MethodNotAllowed

            movie = Movie.query.get(movie_id)
            if movie is None:
                raise NotFound

            movie.delete()
            # get page of movies for display after delete
            all_movies = Movie.query.all()
            current_movies = [movie.format() for movie in all_movies]
            if len(current_movies) == 0:
                raise NotFound

            return jsonify({
                'success': True,
                'deleted': movie_id,
                'movies': current_movies,
                'total_movies': len(all_movies)
            })
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/movies/<int:movie_id>/patch', methods=['PATCH'])
    @cross_origin()
    @requires_auth('patch:movies')
    def patch_movie_submission(payload, movie_id):
        try:
            if not request.method == 'PATCH':
                raise MethodNotAllowed
            movie_data = request.get_json()

            if 'movie_name' or 'release_date' in movie_data:
                new_name = movie_data.get('movie_name', None)
                new_release_date = movie_data.get('release_date', None)
            
                movie = Movie.query.filter(Movie.movie_id == movie_id).one_or_none()
                if movie == None:
                    raise NotFound
                if new_name != None:
                    movie.movie_name = new_name
                if new_release_date != None:
                    movie.release_date = new_release_date
                movie.update()
                return jsonify({
                    "success": True, 
                    "id": movie_id
                })
            else:
                # if no changes submitted then raise error
                raise UnprocessableEntity
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    #  ----------------------------------------------------------------
    #  Actors
    #  ----------------------------------------------------------------

    @app.route('/actors', methods=['GET'])
    @cross_origin()
    @requires_auth('get:actors')
    def actors(payload):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            actor_query = Actor.query.all()
            data = []
            for actor in actor_query:
                data.append({
                "id": actor.actor_id,
                "actor_name": actor.actor_name,
                "age": actor.age,
                "gender": actor.gender
                })

            return render_template('pages/actors.html', actors=data), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/create', methods=['GET'])
    @cross_origin()
    @requires_auth('post:actors')
    def create_actor_form(payload):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            form = ActorForm()
            return render_template('forms/new_actor.html', form=form), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/create', methods=['POST'])
    @cross_origin()
    @requires_auth('post:actors')
    def create_actor_submission(payload):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed
            form = ActorForm(request.form, meta={'csrf': False})
        
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)
        if form.validate():
            error = False
            try:
                new_actor = Actor(
                    actor_name = form.actor_name.data,
                    age = form.age.data,
                    gender = form.gender.data
                )

                new_actor.insert()
            except:
                error = True
                db.session.rollback()
            finally:
                db.session.close()
                # on successful db insert, flash success
                if error:
                    flash('An error occurred. Actor ' + form.actor_name.data + ' could not be listed.')
                else:
                    flash('Actor ' + form.actor_name.data + ' was successfully listed!')
                return render_template('pages/home.html'), 200
        else:
            message = []
            error_fields = ''
            for field, errors in form.errors.items():
                message.append(field + ': (' + '|'.join(errors) + ')')
                error_fields += field + ', '
            error_fields = error_fields[:-2]
            flash('The Actor data is not valid. Please try again! Errors are in '+error_fields)
            return render_template('pages/home.html')


    @app.route('/actors/<int:actor_id>', methods=['GET'])
    @cross_origin()
    @requires_auth('post:actors')
    def show_actor(payload, actor_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            data = db.session.query(Actor).filter(Actor.actor_id==actor_id).first()

            return render_template('pages/show_actor.html', actor=data), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/<int:actor_id>/edit', methods=['GET'])
    @cross_origin()
    @requires_auth('patch:actors')
    def edit_actor(payload, actor_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            actor = Actor.query.get(actor_id)
            form = ActorForm(obj=actor)

            return render_template('forms/edit_actor.html', form=form, actor=actor), 200
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/<int:actor_id>/edit', methods=['POST'])
    @cross_origin()
    @requires_auth('patch:actors')
    def edit_actor_submission(payload, actor_id):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed
            actor = Actor.query.get(actor_id)
            form = ActorForm(request.form, meta={'csrf': False})
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)
        if form.validate():
            error = False
            try:
                # update the actor data from form
                form.populate_obj(actor)
                actor.update()
            except:
                error = True
                db.session.rollback()
                flash('Error! Actor ' + actor.actor_name + ' could not be listed.')
            finally:
                db.session.close()
                # on successful db insert, flash success
                if error:
                    flash('An error occurred. Actor ' + form.actor_name.data + ' could not be updated.')
                else:
                    flash('Actor ' + form.actor_name.data + ' was successfully updated')
                #return render_template('pages/show_actor.html', actor=actor), 200
                return render_template('pages/home.html')
        else:
            message = []
            error_fields = ''
            for field, errors in form.errors.items():
                message.append(field + ': (' + '|'.join(errors) + ')')
                error_fields += field + ', '
                error_fields = error_fields[:-2]
                flash('The Actor data is not valid. Please try again! Errors are in '+error_fields)
            #return render_template('pages/show_actor.html', actor=actor)
            return render_template('pages/home.html')

    @app.route('/actors/<int:actor_id>/delete', methods=['GET'])
    @cross_origin()
    @requires_auth('delete:actors')
    def delete_actor(payload, actor_id):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            actor = Actor.query.get(actor_id)
            if actor is None:
                raise NotFound
            actor.delete()
            #return redirect(url_for('actors')), 200
            return render_template('pages/home.html')
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/<int:actor_id>/deleterequest', methods=['DELETE'])
    @cross_origin()
    @requires_auth('delete:actors')
    def delete_actor_deleterequest(payload, actor_id):
        try:
            if not request.method == 'DELETE':
                raise MethodNotAllowed

            actor = Actor.query.get(actor_id)
            if actor is None:
                raise NotFound

            actor.delete()
            # get page of actors for display after delete
            all_actors = Actor.query.all()
            current_actors = [actor.format() for actor in all_actors]
            if len(current_actors) == 0:
                raise NotFound

            return jsonify({
                'success': True,
                'deleted': actor_id,
                'actors': current_actors,
                'total_actors': len(all_actors)
            })
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route("/actors/postrequest", methods=['POST'])
    @cross_origin()
    @requires_auth("post:actors")
    def create_actor_from_request(payload):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed

            actor_data = request.get_json()
            # if all data not submitted then raise error
            if 'actor_name' and 'age' and 'gender' not in actor_data:
                raise UnprocessableEntity
            new_actor_name = actor_data.get('actor_name')
            new_age = actor_data.get('age')
            new_gender = actor_data.get('gender')
            new_actor = Actor(actor_name=new_actor_name, age=new_age, gender=new_gender)
            new_actor.insert()
            return jsonify({
                'success': True,
                'actor_id': new_actor.actor_id,
                'actor': new_actor.actor_name
            })
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actors/<int:actor_id>/patch', methods=['PATCH'])
    @cross_origin()
    @requires_auth('patch:actors')
    def patch_actor_submission(payload,  actor_id):
        try:
            if not request.method == 'PATCH':
                raise MethodNotAllowed
            actor_data = request.get_json()

            if 'actor_name' or 'age' or 'gender' in actor_data:
                new_name = actor_data.get('actor_name', None)
                new_age = actor_data.get('age', None)
                new_gender = actor_data.get('gender', None)
            
                actor = Actor.query.filter(Actor.actor_id == actor_id).one_or_none()
                if actor == None:
                    raise NotFound
                if new_name != None:
                    actor.actor_name = new_name
                if new_age != None:
                    actor.age = new_age
                if new_gender != None:
                    actor.gender = new_gender
                actor.update()
                return jsonify({
                    "success": True, 
                    "id": actor_id
                })
            else:
                # if no changes submitted then raise error
                raise UnprocessableEntity
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(422)

    #  ----------------------------------------------------------------
    #  Actor_movies
    #  ----------------------------------------------------------------

    @app.route('/actor_movie/create', methods=['GET'])
    @cross_origin()
    @requires_auth('post:moviesactors')
    def create_actor_movie(payload):
        try:
            if not request.method == 'GET':
                raise MethodNotAllowed
            form = ActorMovieForm()
            return render_template('forms/new_actor_movie.html', form=form)
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)

    @app.route('/actor_movie/create', methods=['POST'])
    @cross_origin()
    @requires_auth('post:moviesactors')
    def create_actor_movie_submission(payload):
        try:
            if not request.method == 'POST':
                raise MethodNotAllowed
            form = ActorMovieForm(request.form, meta={'csrf': False})
        except MethodNotAllowed:
            abort(405)
        except UnprocessableEntity:
            abort(422)
        except NotFound:
            abort(404)
        except AuthError:
            abort(AuthError)
        except:
            abort(500)
        if form.validate():
            error = False
            try:
                movie = Movie.query.get(form.movie_id.data)
                actor = Actor.query.get(form.actor_id.data)
                movie.actors.append(actor)
                movie.update()
            except:
                error = True
                db.session.rollback()
            finally:
                db.session.close()
                # on successful db insert, flash success
                if error:
                    flash('An error occurred. The actor could not be assigned to the movie')
                else:
                    flash('The actor was successfully assigned to the movie')
                return render_template('pages/home.html')
        else:
            message = []
            error_fields = ''
            for field, errors in form.errors.items():
                message.append(field + ': (' + '|'.join(errors) + ')')
                error_fields += field + ', '
            error_fields = error_fields[:-2]
            flash('The Actor_movie data is not valid. Please try again! Errors are in '+error_fields)
            return render_template('pages/home.html')

    # error handlers for all expected errors 
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False, 
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False, 
            "error": 500,
            "message": "internal server error"
        }), 500

    @app.errorhandler(AuthError)
    def authentification_failed(AuthError):
        return json.dumps({
            'success': False,
            'error': AuthError.status_code,
            'message': AuthError.error['message']
            }), AuthError.status_code

    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=8080, debug=True)
    
    return app

app = create_app()

