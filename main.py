from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'BL123xyzOG'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog_entry = db.Column(db.String(255)) 

    def __init__(self, title, blog_entry):
        self.title = title
        self.blog_entry = blog_entry
              

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    title_message='Please enter a title.'
    body_message='Please enter a message'
    title = ''
    blog_entry = ''
    if request.method == 'POST':
        title = request.form['title']
        blog_entry = request.form['blog_entry']
        new_post = Blog(title,blog_entry)
        db.session.add(new_post)
        db.session.commit()
        if re.search('\w',blog_entry):
            return render_template('newpost.html', page_title="Add a Blog Entry", title_message=title_message, title=title, blog_entry=blog_entry)
        elif not re.search('\w',title):
            return render_template('newpost.html', page_title="Add a Blog Entry", title_message=title_message, body_message=body_message, title=title, blog_entry=blog_entry)
        elif not re.search('\w',blog_entry): 
            return render_template('newpost.html', page_title="Add a Blog Entry", body_message=body_message, title=title, blog_entry=blog_entry)   
        
        else:
            return redirect('/blog')    
    return render_template('newpost.html', page_title="Add a Blog Entry")
 

@app.route('/blog', methods=['POST','GET'])
def index():
    blog_posts = Blog.query.all()
    return render_template('blog.html', page_title='Build a Blog', blog_posts=blog_posts) 
         


if __name__ == '__main__':
    app.run()