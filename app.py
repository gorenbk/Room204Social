# Import everything
from flask import Flask, request, render_template, redirect, session, jsonify
import uuid as uuid_module
import hashlib
import sqlite3
import os
import datetime
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'data', 'db.db')
conn = sqlite3.connect(DATABASE, check_same_thread=False)
import logging
from datetime import datetime, timezone, timedelta
crsr = conn.cursor()
crsr.execute("""CREATE TABLE IF NOT EXISTS users
(username TEXT,
fname TEXT,
lname TEXT,
pwd TEXT,
uuid TEXT);""")
crsr.execute("""CREATE TABLE IF NOT EXISTS posts
(uuid TEXT,
post_content TEXT,
user_uuid TEXT,
url TEXT,
reply_to TEXT,
timestamp TEXT);""")
conn.commit()
conn.commit()
app = Flask(__name__)
app.secret_key = '604d60c010ae89882132604ab91eef5a02a1bccb703b74eb918431e45364312a'
def react(self):
    query = """INSERT INTO reactions (type, post_uuid, user_uuid, reaction_uuid)
            VALUES (?, ?, ?, ?)"""
    values = (self.type, self.post_uuid, self.user_uuid, self.reaction_uuid)
    try:
        crsr.execute(query, values)
        conn.commit()
        logging.info(f"Reaction {self.reaction_uuid} sent successfully.")
    except Exception as e:
        logging.error(f"Error sending reaction {self.reaction_uuid}: {e}")
class User():
    def __init__(self,username,fname,lname,pwd, uuid_str=None, hashed=False):
        # Set the attributes of the user
        self.username = username
        self.fname = fname
        self.lname = lname
        self.pwd = hashlib.sha256(pwd.encode("utf-8")).hexdigest() if not hashed else pwd
        self.uuid = str(uuid_module.uuid4()) if not uuid_str else uuid_str
        self.logged_in = False
    def verify_pwd(self,pwd_input):
        print(f"Verifying password for {self.username}, inputs is {pwd_input}, hashed password is {self.pwd}")
        # Hash the password
        pwd_hashed = hashlib.sha256(pwd_input.encode('utf-8')).hexdigest()
        # Compare the hashed password with the stored password
        print(f"Hashed password is {pwd_hashed}")
        if pwd_hashed == self.pwd:
            return True
        else:
            return False
    def to_dict(self):
        # Return a dictionary of the user
        return {"username": self.username, "fname": self.fname, "lname": self.lname, "pwd": self.pwd, "uuid": self.uuid}
    @staticmethod
    def from_dict(dict):
        # Return a user object from a dictionary
        return User(dict["username"],dict["fname"],dict["lname"],dict["pwd"],dict["uuid"], hashed=True)
    def login(self):
        # Set the logged_in attribute to True
        self.logged_in = True
    @staticmethod
    def get_user(username):
        # Get the user from the database
        crsr.execute("SELECT * FROM users WHERE username = ?", (username,))
        result = crsr.fetchone()  # Fetch one record
        print("User dictionary (get_user):",)
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            # Create dictionary
            user_dict = dict(zip(column_names, result))
            return User.from_dict(user_dict)
        else:
            return None
    def get_uuid_from_username(username):
        # Get the uuid from the database
        crsr.execute("SELECT uuid FROM users WHERE username = ?", (username,))
        result = crsr.fetchone()
        if result:
            return result[0]
        else:
            return None
    @staticmethod
    def get_username_from_uuid(uuid):
        # Get the user from the database
        crsr.execute("SELECT username FROM users WHERE uuid = ?", (uuid,))
        result = crsr.fetchone()  # Fetch one record'
        print(f"Query result: {result}")
        if result:
            print(f"Username: {result[0]}")
            return result[0]
        else:
            return None
    def get_users():
        # Get the posts from the database
        crsr.execute("SELECT * FROM users")
        result = crsr.fetchall()
        print("result:", result)
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            print("column_names:", column_names)
            user_list = []
            # For each record, create a dictionary and append it to the list
            for record in result:
                user_dict = dict(zip(column_names, record))
                user_list.insert(0, user_dict)
                print("user_list:", user_list)
            return user_list
        else:
            return None
class Post():
    def __init__(self,post_content,user_uuid, time=None, uuid_str=None, reply_to=None):
        # Set the attributes of the post
        print("Creating post")
        self.reply_to = reply_to
        self.post_content = post_content
        self.user_uuid = user_uuid
        tz = timezone(timedelta(hours=-5), 'EST')
        _time = datetime.now(tz)
        self.time = str(_time.strftime("%m/%d/%Y %I:%M %p")) if not time else time
        print('time:',self.time)
        self.uuid = str(uuid_module.uuid4()) if not uuid_str else uuid_str
        self.url = f"/view?post_id={self.uuid}"
    def to_dict(self):
        # Return a dictionary of the post
        return {"uuid": self.uuid, "post_content": self.post_content, "user_uuid": self.user_uuid, "url": self.url, "time":self.time}
    def send_post(self):
        # Send the post to the database
        query = """INSERT INTO posts (uuid, post_content, user_uuid, url, timestamp)
               VALUES (?, ?, ?, ?, ?)"""
        values = (self.uuid, self.post_content, self.user_uuid, self.url, self.time)
        try:
            crsr.execute(query, values)
            conn.commit()
            logging.info(f"Post {self.uuid} sent successfully.")
        except Exception as e:
            logging.error(f"Error sending post {self.uuid}: {e}")

    def getposts():
        # Get the posts from the database
        crsr.execute("SELECT * FROM posts")
        result = crsr.fetchall()
        print("result:", result)
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            print("column_names:", column_names)
            posts_list = []
            # For each record, create a dictionary and append it to the list
            for record in result:
                post_dict = dict(zip(column_names, record))
                post_dict["username"] = (User.get_username_from_uuid(post_dict["user_uuid"]))
                posts_list.insert(0, post_dict)
                print("posts_list:", posts_list)
            return posts_list
        else:
            return None
    def getpost(uuid):
        # Get the post from the database
        crsr.execute("SELECT * FROM posts WHERE uuid = ?", (uuid,))
        result = crsr.fetchone()
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            # Create dictionary
            post_dict = dict(zip(column_names, result))
            return post_dict
        else:
            return None
    @staticmethod
    def getpostsfromusername(username):
        # Get the posts from the database
        crsr.execute("SELECT * FROM posts WHERE user_uuid = ?", (User.get_uuid_from_username(username),))
        result = crsr.fetchall()
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            posts_list = []
            # For each record, create a dictionary and append it to the list
            for record in result:
                post_dict = dict(zip(column_names, record))
                posts_list.insert(0, post_dict)
            return posts_list
        else:
            return None
    def send_reply(self):
        query = """INSERT INTO posts (uuid, post_content, user_uuid, url, reply_to, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)"""
        values = (self.uuid, self.post_content, self.user_uuid, self.url, self.reply_to, self.time)
        try:
            crsr.execute(query, values)
            conn.commit()
            logging.info(f"Post {self.uuid} sent successfully.")
        except Exception as e:
            logging.error(f"Error sending post {self.uuid}: {e}")
    def get_replies_from_uuid(uuid):
        # Get the replies from the database
        crsr.execute("SELECT * FROM posts WHERE reply_to IS ?", (uuid,))
        result = crsr.fetchall()
        print("result:", result)
        if result:
            # Get column names
            column_names = [description[0] for description in crsr.description]
            print("column_names:", column_names)
            posts_list = []
            # For each record, create a dictionary and append it to the list
            for record in result:
                post_dict = dict(zip(column_names, record))
                post_dict["username"] = (User.get_username_from_uuid(post_dict["user_uuid"]))
                posts_list.insert(0, post_dict)
                print("posts_list:", posts_list)
            return posts_list
        else:
            return None
# Decorator
def logged_into(uuid):
    def real_decorator(func):
        def wrapper(*args, **kwargs):
            # Set the current user
            global current_user 
            # Get the user from the database
            crsr.execute("SELECT * FROM users WHERE uuid = ?", (uuid,))
            current_user = User.from_dict(crsr.fetchone())
            func(*args, **kwargs, user_uuid = uuid)
        return wrapper
    return real_decorator
"""
NOTICE: If you want to add a class, add it before this comment.
Anything below this comment is @app.route() and defining urls for the site. Remember this.
"""
@app.route('/')
def index():
    # Return the welcome page
    return render_template("welcome.html")
@app.route('/signup', methods = ['GET','POST'])
def signup():
    # Return the signup page
    if request.method == 'POST':
        if User.get_user(request.form['username']):
            return redirect('/login')
        else:
            # Create a new user
            new_user = User(request.form["username"],request.form["fname"],request.form["lname"],request.form["pwd"]).to_dict()
            query = """INSERT INTO users (username,fname,lname,pwd,uuid)
            VALUES
            (:username, :fname, :lname, :pwd, :uuid)"""
            r = crsr.execute(query, new_user)
            conn.commit()
            print("Executing query", query, new_user, request.form)
            # Redirect to the login page
            return redirect("/login")
    return render_template("signup.html")
@app.route('/login', methods = ['GET','POST'])
def login():
    # Return the login page
    if request.method == 'POST':
        user = User.get_user(request.form["username"])
        if user:
            if user.verify_pwd(request.form["pwd"]):
                user.login()
                session['current_user_uuid'] = user.uuid
                return redirect("/feed")
            else:
                return render_template("login.html", error = "Wrong password")
        else:
            return render_template("login.html", error = "User not found")
    return render_template("login.html")
@app.route('/feed', methods = ['GET','POST'])
def feed():
    # Automatic login
    user = User.get_user(User.get_username_from_uuid(session['current_user_uuid']))  # Replace "the_username" with the desired username
    if user:
        user.login()
        session['current_user_uuid'] = user.uuid
        # Return the feed page
        print("Number of posts:", len(Post.getposts())) if Post.getposts() else print("No posts")
        print("Posts:", Post.getposts())
        return render_template("feed.html", posts = Post.getposts(),username=User.get_username_from_uuid(session['current_user_uuid']),fname = user.fname if user is not None else "Unknown", len=len(Post.getposts()) if Post.getposts() else 0)
    else:
        return redirect("/login")
@app.route('/post', methods = ['GET','POST'])
def post():
    if request.method == 'POST':
        new_post = Post(request.form["post_content"],session['current_user_uuid'])
        new_post.post_content = '<br>'.join(new_post.post_content.splitlines())
        new_post.send_post()
        return redirect("/feed")
    return render_template("post.html")
@app.route('/@<username>', methods = ['GET','POST'])
def profile(username):
    return render_template("profile.html", posts = Post.getpostsfromusername(username), fname = User.get_user(username).fname, len=len(Post.getpostsfromusername(username)) if Post.getpostsfromusername(username) else 0)
@app.route('/view?post_id=<post_id>', methods = ['GET','POST'])
@app.route('/view', methods = ['GET','POST'])
def view():
    post_id = request.args.get('post_id')
    post = Post.getpost(post_id)
    if post:
        if request.method == 'POST':
            new_post = Post(request.form['post_content'],session['current_user_uuid'], reply_to=post['uuid'])
            new_post.post_content = '<br>'.join(new_post.post_content.splitlines())
            new_post.send_reply()
            return redirect("/view?post_id="+post_id)
        if Post.getpost(Post.getpost(post_id)['reply_to']):
            original_post = Post.getpost(Post.getpost(post_id)['reply_to'])
            print('original_post:',original_post)
        else:
            original_post = None
        return render_template("view.html", post=post["post_content"], username=User.get_username_from_uuid(post["user_uuid"]), replies=Post.get_replies_from_uuid(post_id) if Post.get_replies_from_uuid(post_id) else None, len=len(Post.get_replies_from_uuid(post_id)) if Post.get_replies_from_uuid(post_id) else None, original_post = original_post, original_username = User.get_username_from_uuid(original_post['user_uuid']) if original_post else None)
    else:
        return "Post not found."
@app.route('/directory')
def directory():
    return render_template('directory.html', users = User.get_users(), len = len(User.get_users()) if User.get_users() else 0)
if __name__ == "__main__":
    conn.commit()
    app.run(debug=True)