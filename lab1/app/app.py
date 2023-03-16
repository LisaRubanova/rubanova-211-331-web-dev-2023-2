from flask import Flask, render_template

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html', msg='qq')

@app.route('/posts')
def posts():
    return render_template('posts.html')

@app.route('/about')
def about():
    return render_template('about.html', msg='qq')