#!/usr/bin/python3
# -*- coding: utf-8 -*-
# https://flask-mysqldb.readthedocs.io/en/latest/


from flask import Flask, flash, redirect, url_for, logging, render_template, request, session, abort
# from flaskext.mysql import  MySQL
from flask_mysqldb import MySQL
# import data in the Articles function.
# from data import Articles
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps





# Create an instance of flask called "app"
app = Flask(__name__)

# init MYSQL
mysql = MySQL(app)


# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'theMED@120*'
app.config['MYSQL_DB'] = 'myflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'







#We created a data.py file. Defined fnc() named Article with
# an array named articles that has 3 objects.,
#We create a variable named: Articles equal to the function name used in data.py


#Articles = Articles()

#Creating URL ROUTES:
#We use a route() decorator to bind a function to a URL.
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')


# Articles
@app.route('/articles')
def articles():
    # Create cursor
    cur = mysql.connection.cursor()

    # Get Articles
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close the connection
    cur.close()
    return render_template('articles.html', articles= Articles)



# Single Article

@app.route('/article/<string:id>/')
def article(id):
    # Create a cursor
    cur = mysql.connection.cursor()

    # Get article
    result = cur.execute("SELECT * FROM articles WHERE id = %s ", [id])

    article = cur.fetchone()

    
    # We need to pass in the articles(data), so pass in 2nd param.
    return render_template('article.html', id=id)


# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = PasswordField('Password', [
            validators.DataRequired(),
            validators.EqualTo('confirm', message='Passwords do not match')
        ])
    confirm = PasswordField('Confirm Password')





# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    #set it equal to the above FORM.
    form = RegisterForm(request.form)
    #check if POST request and form is validated.
    if request.method == 'POST' and form.validate():
        #IF only need access to data for KNOWN fields,use: form.<field>.data
        name = form.username.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data)) 

        # Create cursor STUPID! forgot the mysql. here!!!!!!!!
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute("INSERT INTO user(name, email, username, password) VALUES (%s, %s, %s, %s )", (name, email, username, password))

        #Commit to DB
        mysql.connection.commit()

        #close connection
        cur.close()
        
        #Once registered: message, category
        flash('You are now registered and can now log in', 'success')

        redirect(url_for('login'))
    return render_template('register.html', form=form)



# User Login
@app.route('/login', methods=['GET', 'POST']) 
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create a cursor
        cur = mysql.connection.cursor()

        #Get user username
        result = cur.execute("SELECT * FROM user WHERE username = %s", [username])


        if result > 0:
            # get stored hash
            data =cur.fetchone()
            password = data['password']


            #Compare passwords
            if sha256_crypt.verify(password_candidate, password):
                #Passed
                session['loggin_in']=True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)
    
    return render_template('login.html')
            

                
                
       
    

#check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))



#Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    #create cursor
    cur = mysql.connection.cursor()

    #Get articles
    result = cur.execute("SELECT * FROM articles")
    # Show articles from only the user logged in
    result = cur.execute("SELECT * FROM articles WHERE author = %s", [session['username']])

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles =articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg)
        #Close the connection
        cur.close()
    return render_template('dashboard.html')
    

#Article Form Class
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body  = TextAreaField('Body', [validators.Length(min=30)])

#Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body  = form.body.data

        #create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

        # Commit to the db
        mysql.connection.commit()

        #Close the connection
        cur.close()

        flash('Article Created', 'success')


        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form)



#Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = fetchone()
    cur.close()

    #get form
    form = ArticleForm(request.form)

    #populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']

    if request.method ==  'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        #create cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)


        cur.execute("UPDATE articles SET title=%s, body=%s WHERE id=%s", (title, body, id))


        mysql.connection.commit()

        cur.close()

        flash('Article Updated', 'success')


        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)


#Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM articles WHERE id=%s", [id])

    mysql.connection.commit()

    cur.close()

    flash('Article deleted!', 'success')

    return redirect(url_for('dashboard'))

                          


                          

                          

                          
                

    










if __name__ == "__main__":
    app.secret_key='secret123'
    app.run(debug=True)

