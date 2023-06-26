from flask import Flask, render_template, abort, send_from_directory, redirect, url_for
from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import bleach

#pip install bleach


app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from auth import bp as auth_bp, init_login_manager
from books import bp as books_bp

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
init_login_manager(app)
from models import Image

@app.route('/')
def index():
    return redirect(url_for('books.index'))


@app.route('/images/<image_id>')
def image(image_id):
    img = Image.query.get(image_id)
    if img is None:
        abort(404)
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               img.storage_filename)