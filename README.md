Stuart’s Udacity Capstone Project

This project is the final piece of work in the Udacity Full Stack Web Developer Nanodegree.

The App and API is a Casting Agency which allows users to view/add/modify/delete Actors amd Movies as well as assigning Actors to Movies.
The application has a front end based on the Fyyer project.
The application is deployed on Heroku and can be accessed via https://stuart-capstone.herokuapp.com

All backend code follows PEP8 style guide.

Getting Started
Pre-requisites and Local Development
Developers using this project should already have Python and PIP installed on their local machines.

To set up the configuration variables and to run 'requirements.txt', from the root folder run:
source setup.sh

To run the application run the following command:
flask run

The application is run on http://127.0.0.1:5000/ by default.

Tests
In order to run tests run the following commands from the root folder:
dropdb capstone_test
createdb capstone_test
python test_app.py

The first time you run the tests, omit the dropdb command.
All tests are kept in test_app.py and should be maintained as updates are made to app functionality

Errors

Error Handling
Errors are returned as JSON objects in the following format:

{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
The API will return the following error types when requests fail:

400: Bad Request
404: Resource Not Found
405: Method Not Allowed
422: Not Processable
500: Internal Service Error

Roles/Users

Two roles have been setup in Auth0.
Casting assistant - which can only view movies and actors
User: stuartudacitycast@mail2uk.com
Password: stuartCASTcapstone1!

Executive Producer - which can do anything
User: stuartudacityexec@mail.com
Password: stuartEXECcapstone1!

API Endpoints

GET /login
The user is redirected to the Auth0 login page where they can login to the app
Roles authorized: all users
Sample: curl http://127.0.0.1:5000/login

GET /callback
Verifies the access token and redirects to home page
Roles authorized: Executive Producer and Casting Assistant
Sample: curl http://127.0.0.1:5000/callback

GET /logout
Clears the session and the user is logged out
Roles authorized: Executive Producer and Casting Assistant
Sample: curl http://127.0.0.1:5000/logout

GET /movies
General:
Returns a list of movie objects which include movie_id, movie_name and release date
Authorized roles: Executive Producer and Casting Assistant
Sample: curl -X GET http://127.0.0.1:5000/movies

GET /movies/create
Returns a form the user can fill out to create a new movie
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/movies/create

POST /movies/create
Creates a new movie on the database, including the submitted movie's name and release date
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/movies/create -H "Content-Type: application/json" -d '{ "movie_name": "New Movie", "release_date": "2021-06-01"}'

GET /movies/{movie_id}
Returns a form the user can fill out to edit a movie
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/movies/1

POST /movies/{movie_id}/edit
Updates a existing movie on the database, The movie's name and/or release date can be edited
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/1/edit -H "Content-Type: application/json" -d '{ "movie_name": "Edited Movie", "release_date": "2020-06-01"}'

GET /movies/{movie_id}/delete
Deletes the movie of the given ID if it exists in the database
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/movies/1/delete

POST /movies/postrequest
Creates a new movie on the database, including the submitted movie's name and release date
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/movies/postrequest -H "Content-Type: application/json" -d '{ "movie_name": "New Movie", "release_date": "2021-06-01"}'
{
  "movie": "New Movie",
  "movie_id": 16,
  "success": true
}

DELETE /movies/deleterequest
Deletes the movie of the given ID if it exists in the database
Authorized roles: Executive Producer
Sample: curl -X DELETE http://127.0.0.1:5000/movies/16/deleterequest
{
  "deleted": 16,
  "movies": [
    {
      "movie_id": 4,
      "movie_name": "Stuarts second movie edited",
      "release_date": "Thu, 27 May 2021 00:00:00 GMT"
    },
    {
      "movie_id": 1,
      "movie_name": "Stuarts first movie",
      "release_date": "Thu, 13 May 2021 00:00:00 GMT"
    }
  ],
  "success": true,
  "total_movies": 2
}

PATCH /movies/{movie_id}/patch
Updates a existing movie on the database, The movie's name and/or release date can be edited
Authorized roles: Executive Producer
Sample: curl -X PATCH http://127.0.0.1:5000/1/patch -H "Content-Type: application/json" -d '{ "movie_name": "Stuarts first movie patched", "release_date": "2020-06-01"}'
{
  "id": 1,
  "success": true
}

GET /actors
General:
Returns a list of actor objects which include actor_id, actor_name, age and gender
Authorized roles: Executive Producer and Casting Assistant
Sample: curl -X GET http://127.0.0.1:5000/actors

GET /actors/create
Returns a form the user can fill out to create a new actor
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/actors/create

POST /actors/create
Creates a new actor on the database, including the submitted actor's name, age and gender
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/actors/create -H "Content-Type: application/json" -d '{"actor_name": "New Actor", "age": 50, "gender": "Other"}'

GET /actors/{actor_id}
Returns a form the user can fill out to edit a actor
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/actors/1

POST /actors/{actor_id}/edit
Updates a existing actor on the database, The actor's name and/or age and/or gender can be edited
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/1/edit -H "Content-Type: application/json" -d '{"actor_name": "Edited Actor", "age": 51, "gender": "Male"}'

GET /actors/{actor_id}/delete
Deletes the actor of the given ID if it exists in the database
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/actors/1/delete

POST /actors/postrequest
Creates a new actor on the database, including the submitted actor's name and release date
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/actors/postrequest -H "Content-Type: application/json" -d '{"actor_name": "New Actor", "age": 50, "gender": "Other"}'
{
  "actor": "New Actor",
  "actor_id": 8,
  "success": true
}

DELETE /actors/deleterequest
Deletes the actor of the given ID if it exists in the database
Authorized roles: Executive Producer
Sample: curl -X DELETE http://127.0.0.1:5000/actors/8/deleterequest
{
  "actors": [
    {
      "actor_id": 7,
      "actor_name": "Stuart actor three edited again",
      "age": 333,
      "gender": "Other"
    },
    {
      "actor_id": 1,
      "actor_name": "Stuart One edited again",
      "age": 55,
      "gender": "Female"
    }
  ],
  "deleted": 8,
  "success": true,
  "total_actors": 2
}

PATCH /actors/{actor_id}/patch
Updates a existing actor on the database, The actor's name and/or release date can be edited
Authorized roles: Executive Producer
Sample: curl -X PATCH http://127.0.0.1:5000/actors/1/patch -H "Content-Type: application/json" -d '{"actor_name": "Stuarts first actor patched", "age": 60, "gender": "Male"}'
{
  "id": 1,
  "success": true
}

GET /actor_movie/create
Returns a form the user can fill out to assign an actor to a movie
Authorized roles: Executive Producer
Sample: curl -X GET http://127.0.0.1:5000/actor_movie/create

POST /actor_movie/create
Creates a new assignment of an actor with a movie on the database
Authorized roles: Executive Producer
Sample: curl -X POST http://127.0.0.1:5000/actor_movie/create -H "Content-Type: application/json" -d '{"actor_id": 1, "movie_id": 1}'