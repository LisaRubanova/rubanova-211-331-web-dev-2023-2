import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from models import Book, Image, Genre
from app import db, app

# модель сортировки книг
class BooksFilter:
    def __init__(self, name, genres, year, author, pages):
        self.name = name
        self.genres = genres
        self.year = year
        self.author = author
        self.pages = pages
        self.query = Book.query

    def perform(self):
        self.__filter_by_name()
        self.__filter_by_genres_ids()
        self.__filter_by_author_name()
        self.__filter_by_year()
        self.__filter_by_pages()
        return self.query.order_by(Book.year.desc())
    
    # сортировка по названию 
    def __filter_by_name(self):
        if self.name:
            self.query = self.query.filter(
                Book.name.ilike('%' + self.name + '%'))
    # сортировка по жанру
    def __filter_by_genres_ids(self):
        print("self.genres", self.genres)
        if self.genres:
            session.query(Genre).filter(Genre.id.in_((self.genres))).all()
            # self.query = self.query.filter(
            #     Genre.genres.in_(self.genres))
    
    # сортировка по автору
    def __filter_by_author_name(self):
        if self.author:
            self.query = self.query.filter(
                Book.author.ilike('%' + self.author + '%'))
    # сортировка по году
    def __filter_by_year(self):
        if self.year:
            self.query = self.query.filter(
                Book.year.ilike('%' + self.year + '%'))
    # сортировка по количеству страниц
    def __filter_by_pages(self):
        if self.pages:
            self.query = self.query.filter(
                Book.pages.ilike('%' + self.pages + '%'))


class ImageSaver:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.img = self.__find_by_md5_hash()
        if self.img is not None:
            return self.img
        name = secure_filename(self.file.filename)
        self.img = Image(
            name=name,
            MIME_type=self.file.mimetype,
            file_hash=self.file_hash)
        db.session.add(self.img)
        db.session.commit()
        self.file.save(
            os.path.join(app.config['UPLOAD_FOLDER'],
                         self.img.storage_filename))
        
        return self.img

    def __find_by_md5_hash(self):
        self.file_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Image).filter(Image.file_hash == self.file_hash)).scalar()
