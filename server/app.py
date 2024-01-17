#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


class Index(Resource):
    def get(self):
        return "Welcome to Our Blog Site"


api.add_resource(Index, "/")


class ClearSession(Resource):

    def delete(self):

        session['page_views'] = None
        session['user_id'] = None

        return {}, 204


class IndexArticle(Resource):

    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200


class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get(
            'page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401


api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


class Login(Resource):
    def post(self):
        # user credentials
        data = request.get_json()

        # verify user credentials against db
        user = User.query.filter_by(username=data["username"]).first()

        if not user:
            return make_response(jsonify({"message": "401: Not Authorized"}), 401)

        else:
            # store the authenticated user's id in the session:
            session["user_id"] = user.id

            return make_response(jsonify(user.to_dict()), 200)


api.add_resource(Login, "/login")

'''
 -refreshing the page on the frontend
 -Our backend does know who we are though — so we need a way of getting the user data from the backend into state when the page first loads.
'''

# default /check_sesion
class CheckSession(Resource):
    def get(self):
        # verify against session
        user = User.query.filter_by(id=session.get("user_id")).first()

        if not user:
            return {}, 401
        else:
            return make_response(jsonify(user.to_dict()), 200)


api.add_resource(CheckSession, "/check_session")


# We can add a new route for logging out:
# default /logout
class Logout(Resource):
    def delete(self):
        session["user_id"] = None

        return {}, 204


api.add_resource(Logout, "/logout")


if __name__ == '__main__':
    app.run(port=5555, debug=True)
