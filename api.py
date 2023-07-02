from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse
import json
import requests
import secrets
from app import User, Post, crsr, conn
API_KEY = 'api_key'
app = Flask(__name__)
api = Api(app)
class GetUserPosts(Resource):
    def get(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            return jsonify(data=Post.getpostsfromusername(username))
        elif args['api_key'] != API_KEY:
            return jsonify(data="Invalid API Key")
        else:
            return jsonify(data="Invalid API Key")
class GetPost(Resource):
    def get(self, uuid):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            return jsonify(data=Post.getpost(uuid))
        elif args['api_key'] != API_KEY:
            return jsonify(data="Invalid API Key")
        else:
            return jsonify(data="Invalid API Key")
class GetPosts(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            return jsonify(data=Post.getposts())
        else:
            return jsonify(data="Invalid API Key")
class GetUser(Resource):
    def get(self, username):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            return jsonify(data=User.get_user(username).to_dict())
        else:
            return jsonify(data="Invalid API Key")
class GetUsers(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            return jsonify(data=User.get_users())
        else:
            return jsonify(data="Invalid API Key")
class CreateUser(Resource):
    def post(self, fname, lname, username, pwd):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            if User.get_user(username) == None:
                new_user = User(username,fname,lname,pwd).to_dict()
                query = """INSERT INTO users (username,fname,lname,pwd,uuid)
                VALUES
                (:username, :fname, :lname, :pwd, :uuid)"""
                r = crsr.execute(query, new_user)
                conn.commit()
                return jsonify(data=new_user),200,jsonify(message="User created")
            else:
                return jsonify(data="User already exists")
        else:
            return jsonify(data="Invalid API Key")
class CreatePost(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        parser.add_argument('post_content', type=str, required=True, help='Post Content is required', location='form')
        parser.add_argument('username', type=str, required=True, help='Username is required', location='form')
        args = parser.parse_args()
        post_content = args['post_content']
        username = args['username']
        if args['api_key'] == API_KEY:
            if User.get_user(username) != None:
                new_post = Post(post_content,User.get_uuid_from_username(username))
                new_post.send_post()
                return jsonify(message="Post created")
            else:
                return jsonify(data="User does not exist")
        else:
            return jsonify(data="Invalid API Key")
class CreateReply(Resource):
    def post(self, post_content, username, uuid):
        parser = reqparse.RequestParser()
        parser.add_argument('api_key', type=str, required=True, help='API Key is required', location='form')
        args = parser.parse_args()
        if args['api_key'] == API_KEY:
            if User.get_user(username) != None:
                new_post = Post(post_content,User.get_uuid_from_username(username),reply_to=uuid)
                new_post.send_reply()
            else:
                return jsonify(data="User does not exist")
        else:
            return jsonify(data="Invalid API Key")
@app.route('/')
def index():
    return "Welcome to the API"
api.add_resource(GetUserPosts, '/api/getuserposts/<string:username>')
api.add_resource(GetPost, '/api/getpost/<string:uuid>')
api.add_resource(GetUser, '/api/getuser/<string:username>')
api.add_resource(GetUsers, '/api/getusers')
api.add_resource(GetPosts, '/api/getposts')
api.add_resource(CreateUser, '/api/createuser')
api.add_resource(CreatePost, '/api/createpost')
api.add_resource(CreateReply, '/api/createreply')
# Path: api.py
if __name__ == '__main__':
    app.run(debug=True)