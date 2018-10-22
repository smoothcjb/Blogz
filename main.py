from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from hashutils import create_hash, verify_hash 

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'BL123xyzOGZ'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    message = db.Column(db.String(255)) 
    pub_date = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, message, owner, pub_date=None):
        self.title = title
        self.message = message
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model) :
    id = db.Column(db.Integer, primary_key=True)  
    username = db.Column(db.String(120), unique= True)     
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password,):
        self.username = username
        self.pw_hash = create_hash(password)


@app.before_request
def require_login():
    allowed_routes= ['login', 'signup', 'blog', 'index', 'static']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash("Login required.",'error')
        return redirect('/login')        

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    title_error='Please enter a title.'
    body_error='Please enter a message'
    title = ''
    message = ''
    id = ''

    owner = User.query.filter_by(username=session['username']).first()
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        pub_date = datetime.now()
        new_post = Blog(title,message, owner, pub_date)
        if re.search('\w',message) and not re.search('\w',title):
            return render_template('newpost.html', title_error=title_error, title=title, message=message)
        elif not re.search('\w',title):
            return render_template('newpost.html', title_error=title_error, body_error=body_error, title=title, message=message)
        elif not re.search('\w',message): 
            return render_template('newpost.html', body_error=body_error, title=title, message=message)   
        else:
            db.session.add(new_post)
            db.session.commit()
            blog_posts = Blog.query.all() 
        for blog in blog_posts:
            id = blog.id
        return redirect('/blog?id={0}'.format(id))
    return render_template('newpost.html')  

@app.route('/blog')
def blog():
    id = request.args.get('id')
    user_id = request.args.get('user')
    blog_posts = Blog.query.order_by(Blog.pub_date.desc()).all()
    if id != None:
        blog_post = Blog.query.get(id)
        title = blog_post.title
        message = blog_post.message
        owner_id = blog_post.owner_id 
        date = blog_post.pub_date
        owner = blog_post.owner.username
        return render_template('display.html', id=id, title=title, message=message, owner_id=owner_id, owner=owner, date=date)
    elif user_id != None:
        id = user_id
        blogger = User.query.filter_by(id=id).first()
        username = blogger.username
        return render_template('blogger.html', blogger=blogger, id=id, username=username)
    else:
        return render_template('blog.html', page_title = 'Blogz', blog_posts=blog_posts) 

@app.route('/login', methods=['POST','GET'])   
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and verify_hash(password, user.pw_hash):
            session['username'] = username
            greeting = 'Hello, ' + username + '!'
            flash(greeting,'status')
            return redirect('/newpost')
        elif user and not verify_hash(password, user.pw_hash):
            flash('Invalid Password','error')
        else:
            flash('Invalid Username','error')    
    return render_template('login.html')
     
@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if len(username) < 3 or len(username) > 20 or not re.search('\w',username):    
            username_error = 'Username must contain between 3 and 20 characters.'
            return render_template('signup.html', username_error=username_error,password_error='',verify_error='', username=username)
        if len(password) > 20 or len(password) < 3 or not re.search('\w',password):
           password_error = 'Password must contain between 3 and 20 characters.'
           return render_template('signup.html', username_error='',password_error=password_error,verify_error='', username=username)
        if password != verify:    
            verify_error= 'Passwords do not match.'
            return render_template('signup.html', username_error='',password_error='',verify_error=verify_error)
        if not existing_user:
            new_user = User(username,password)
            db.session.add(new_user)
            db.session.commit() 
            session['username'] = username
            return redirect('/newpost')
        else:
            flash('Username already taken.','error')  
    return render_template('signup.html')

@app.route('/')
def index():
    bloggers = User.query.all()
    return render_template('index.html', page_title = "Blogz", bloggers=bloggers)


@app.route('/logout')
def logout():
    del session['username']
    flash('You have signed out successfully.','status')
    return redirect('/blog')
    
if __name__ == '__main__':
    app.run()