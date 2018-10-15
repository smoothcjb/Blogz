from flask import Flask, request, redirect, render_template, session, flash, url_for
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
    message = db.Column(db.String(255)) 

    def __init__(self, title, message):
        self.title = title
        self.message = message
              

@app.route('/newpost', methods=['POST','GET'])
def new_post():
    title_error='Please enter a title.'
    body_error='Please enter a message'
    title = ''
    message = ''
    id = ''
    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        new_post = Blog(title,message)
        if re.search('\w',message) and not re.search('\w',title):
            return render_template('newpost.html', page_title="Add a Blog Entry", title_error=title_error, title=title, message=message)
        elif not re.search('\w',title):
            return render_template('newpost.html', page_title="Add a Blog Entry", title_error=title_error, body_error=body_error, title=title, message=message)
        elif not re.search('\w',message): 
            return render_template('newpost.html', page_title="Add a Blog Entry", body_error=body_error, title=title, message=message)   
        else:
            db.session.add(new_post)
            db.session.commit()
            blog_posts = Blog.query.all() 
        for blog in blog_posts:
            id = blog.id
        return redirect('/blog?id={0}'.format(id))
    return render_template('newpost.html', page_title="Add a Blog Entry")
           

@app.route('/blog')
def main_blog():
    blog_posts = ''
    id = request.args.get('id')
    if id != None:
        blog_post = Blog.query.get(id)
        title = blog_post.title
        message = blog_post.message
        return render_template('display.html', id=id, title=title, message=message)
    else:
        blog_posts = Blog.query.all()
        return render_template('blog.html', page_title='Build a Blog', blog_posts=blog_posts)    
        
     
   
if __name__ == '__main__':
    app.run()