import os
import sqlalchemy as sa
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from user_policy import UserPolicy
from flask import url_for, current_app
from app import db
from werkzeug.security import check_password_hash, generate_password_hash

# модель пользователя
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role_id = db.Column(db.Integer)

    def is_admin(self):
        return self.role_id == current_app.config['ADMIN_ROLE_ID']

    def is_moder(self):
        return self.role_id == current_app.config['MODER_ROLE_ID']

    def can(self, action, record = None):
        users_policy = UserPolicy(record)
        method = getattr(users_policy, action, None)
        if method:
            return method()
        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return ' '.join([self.last_name, self.first_name, self.middle_name or ''])

    def __repr__(self):
        return '<User %r>' % self.login

genres = db.Table('m2m_g_b',
                db.Column('id_book', db.Integer, db.ForeignKey('books.id'), primary_key=True),
                db.Column('id_genre', db.Integer, db.ForeignKey('genres.id'), primary_key=True))

# модель рецензии
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           server_default=sa.sql.func.now())
    # связи с другими таблицами
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 

    def __repr__(self):
        return '<Review %r>' % self.name

# модель книги
class Book(db.Model):
    __tablename__ = 'books'
    print(db.Model)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year =  db.Column(db.DateTime, nullable=False)
    publisher = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(50), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('book_cover.id'))
    genres = db.relationship('Genre', secondary=genres, lazy='subquery',
                             backref=db.backref('books', lazy=True))
    # связи с другими таблицами
    bg_image = db.relationship('Image')

    reviews = 0
    rating = 0

    def __repr__(self):
        return '<Book %r>' % self.name

# модель жанра
class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Genre %r>' % self.name

# модель обложки для книги
class Image(db.Model):
    __tablename__ = 'book_cover'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    MIME_type = db.Column(db.String(50), nullable=False)
    file_hash = db.Column(db.String(128), nullable=False, unique=True)

    def __repr__(self):
        return '<Image %r>' % self.name

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.name)
        print("path", str(self.name))
        print(str(self.name) + ext)
        return str(self.name)

    @property
    def url(self):
        print("self id")
        return url_for('image', image_id=self.id)


