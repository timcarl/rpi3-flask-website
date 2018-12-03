#!/usr/bin/python3

from flask import Flask, flash, redirect, render_template, request, session, abort
#import data in the Articles function.
from data import Articles


#Create an instance of flask called "app"
app = Flask(__name__)

#We created a data.py file. Defined fnc() named Article with
# an array named articles that has 3 objects.,
#We create a variable named: Articles equal to the function name used in data.py
Articles = Articles()

#Creating URL ROUTES:

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/articles')
def articles():
    # We need to pass in the articles(data), so pass in 2nd param.
    return render_template('articles.html', articles = Articles)


@app.route('/article/<string:id>/')
def article(id):
    # We need to pass in the articles(data), so pass in 2nd param.
    return render_template('article.html', id=id)

    


if __name__ == "__main__":
    app.run(debug=True)

