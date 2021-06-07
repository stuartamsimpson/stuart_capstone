import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_testing import TestCase

from app import create_app
from models import setup_db, Movie, Actor


class CapstoneTestCase(unittest.TestCase):
    """This class represents the capstone test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "capstone_test"
        self.database_path = "postgresql://{}/{}".format('postgres:Mu1rj4mbo1@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.NO_USER ={
            'Authorization': ''
        }

        self.CAST_ASSIST ={
            'Authorization': os.environ.get('CASTING_ASSISTANT')
        }

        self.EXEC_PROD ={
            'Authorization': os.environ.get('EXECUTIVE_PRODUCER')
        }

        self.new_movie1 = {
            'movie_name': 'unit test movie success 1',
            'release_date': '2021-06-01'
        }

        self.new_movie2 = {
            'movie_name': 'unit test movie success 2',
            'release_date': '2021-06-02'
        }

        self.new_movie3 = {
            'movie_name': 'unit test movie success 3',
            'release_date': '2021-06-03'
        }

        self.updated_movie = {
            'movie_name': 'unit test movie success updated',
            'release_date': '2021-06-02'
        }

        self.new_actor1 = {
            'actor_name': 'unit test actor success 1',
            'age': 50,
            'gender': 'male'
        }

        self.new_actor2 = {
            'actor_name': 'unit test actor success 2',
            'age': 55,
            'gender': 'female'
        }

        self.new_actor3 = {
            'actor_name': 'unit test actor success 3',
            'age': 60,
            'gender': 'other'
        }

        self.updated_actor = {
            'actor_name': 'unit test actor success updated',
            'age': 60,
            'gender': 'other'
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def testa_create_new_movie_by_request(self):
        print('test_create_new_movie_by_request', flush=True)
        res = self.client().post('/movies/postrequest', json=self.new_movie1, headers=self.EXEC_PROD)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'], self.new_movie1['movie_name'])
        res1 = self.client().post('/movies/postrequest', json=self.new_movie2, headers=self.EXEC_PROD)
        res2 = self.client().post('/movies/postrequest', json=self.new_movie3, headers=self.EXEC_PROD)


    def testb_get_all_movies(self):
        res = self.client().get('/movies', headers=self.CAST_ASSIST)
        self.assertEqual(res.status_code, 200)

    def testc_405_put_get_all_movies(self):
        res = self.client().put('/movies', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testd_get_all_movies_no_auth(self):
        res = self.client().get('/movies', headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def teste_get_movies_form(self):
        res = self.client().get('/movies/create', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testf_405_put_movies_form(self):
        res = self.client().put('/movies/create', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testg_create_movies_form_no_auth(self):
        res = self.client().get('/movies/create', headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def testh_post_movie(self):
        res = self.client().post('/movies/create', json=self.new_movie1, headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testi_405_put_movie(self):
        res = self.client().put('/movies/create', json=self.new_movie1,  headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testj_create_movie_no_auth(self):
        res = self.client().post('/movies/create',  json=self.new_movie1, headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def testk_get_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().get(f'/movies/{id}', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testl_405_put_get_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().put(f'/movies/{id}', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testm_get_movie_no_permissions(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().get(f'/movies/{id}', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found in JWT')

    def testn_patch_movie_form(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().get(f'/movies/{id}/edit', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testo_405_put_patch_movie_form(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().put(f'/movies/{id}/edit', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testp_patch_movie_form_no_permissions(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().get(f'/movies/{id}/edit', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found in JWT')

    def testq_patch_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().post(f'/movies/{id}/edit', json=self.updated_movie, headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testr_405_patch_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().put(f'/movies/{id}/edit', json=self.updated_movie,  headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def tests_patch_movie_no_auth(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().post(f'/movies/{id}/edit',  json=self.updated_movie, headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')


    def testt_delete_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().get(f'/movies/{id}/delete', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testu_404_delete_unknown_movie(self):
        res = self.client().get(f'/movies/5555/delete', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testv_delete_movie_request(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().delete(f'/movies/{id}/deleterequest', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.movie_id == id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertTrue(data['total_movies'])
        self.assertTrue(len(data['movies']))
        self.assertEqual(movie, None)

    def testw_404_delete_request_unknown_movie(self):
        res = self.client().delete(f'/movies/5555/deleterequest', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testx_patch_movie(self):
        id = Movie.query.order_by(Movie.movie_id.desc()).first().movie_id
        res = self.client().patch(f'/movies/{id}/patch', json=self.updated_movie, headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], id)

    def testa_create_new_actor_by_request(self):
        print('test_create_new_actor_by_request', flush=True)
        res = self.client().post('/actors/postrequest', json=self.new_actor1, headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'], self.new_actor1['actor_name'])
        res1 = self.client().post('/actors/postrequest', json=self.new_actor2, headers=self.EXEC_PROD)
        res2 = self.client().post('/actors/postrequest', json=self.new_actor3, headers=self.EXEC_PROD)


    def testb_get_all_actors(self):
        res = self.client().get('/actors', headers=self.CAST_ASSIST)
        self.assertEqual(res.status_code, 200)

    def testc_405_put_get_all_actors(self):
        res = self.client().put('/actors', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testd_get_all_actors_no_auth(self):
        res = self.client().get('/actors', headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def teste_get_actors_form(self):
        res = self.client().get('/actors/create', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testf_405_put_actors_form(self):
        res = self.client().put('/actors/create', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testg_create_actors_form_no_auth(self):
        res = self.client().get('/actors/create', headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def testh_post_actor(self):
        res = self.client().post('/actors/create', json=self.new_actor1, headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testi_405_put_actor(self):
        res = self.client().put('/actors/create', json=self.new_actor1,  headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testj_create_actor_no_auth(self):
        res = self.client().post('/actors/create',  json=self.new_actor1, headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def testk_get_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().get(f'/actors/{id}', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testl_405_put_get_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().put(f'/actors/{id}', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testm_get_actor_no_permissions(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().get(f'/actors/{id}', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found in JWT')

    def testn_patch_actor_form(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().get(f'/actors/{id}/edit', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testo_405_put_patch_actor_form(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().put(f'/actors/{id}/edit', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testp_patch_actor_form_no_permissions(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().get(f'/actors/{id}/edit', headers=self.CAST_ASSIST)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found in JWT')

    def testq_patch_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().post(f'/actors/{id}/edit', json=self.updated_actor, headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testr_405_patch_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().put(f'/actors/{id}/edit', json=self.updated_actor,  headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def tests_patch_actor_no_auth(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().post(f'/actors/{id}/edit',  json=self.updated_actor, headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')


    def testt_delete_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().get(f'/actors/{id}/delete', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testu_404_delete_unknown_actor(self):
        res = self.client().get(f'/actors/5555/delete', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testv_delete_actor_request(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().delete(f'/actors/{id}/deleterequest', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        actor = Actor.query.filter(Actor.actor_id == id).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
        self.assertTrue(data['total_actors'])
        self.assertTrue(len(data['actors']))
        self.assertEqual(actor, None)

    def testw_404_delete_request_unknown_actor(self):
        res = self.client().delete(f'/actors/5555/deleterequest', headers=self.EXEC_PROD)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def testx_patch_actor(self):
        id = Actor.query.order_by(Actor.actor_id.desc()).first().actor_id
        res = self.client().patch(f'/actors/{id}/patch', json=self.updated_actor, headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], id)

    def testy_get_actor_movie_form(self):
        res = self.client().get('/actor_movie/create', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testyy_405_put_actor_movie_form(self):
        res = self.client().put('/actor_movie/create', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testyyy_create_actor_movie_form_no_auth(self):
        res = self.client().get('/actor_movie/create', headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

    def testz_post_actor_movie(self):
        res = self.client().post('/actor_movie/create', headers=self.EXEC_PROD)
        self.assertEqual(res.status_code, 200)

    def testzz_405_put_actor_movie(self):
        res = self.client().put('/actor_movie/create', headers=self.EXEC_PROD)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def testzzz_create_actor_movie_no_auth(self):
        res = self.client().post('/actor_movie/create',  headers=self.NO_USER)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'authorization_header_missing')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
