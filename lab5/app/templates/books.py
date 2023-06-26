from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from app import db
import bleach 
from auth import permission_check
from sqlalchemy.sql import func
from models import Book, User, Review, Genre
from flask_login import current_user
from tools import BooksFilter, ImageSaver
from flask_login import login_required
import markdown
from sqlalchemy import exc
# pip install markdown

bp = Blueprint('books', __name__, url_prefix='/books')

# параметры книги
BOOK_PARAMS = [
    'name', 'description', 'year', 'publisher', 'author', 'pages'
]
PER_PAGE = 10

# загрузка параметров книги
def params():
    return { p: request.form.get(p) for p in BOOK_PARAMS }

def check_params(params_to_check):
    m = False
    # print("params_to_check", params_to_check)
    output_name, output_genres, output_desc, output_year, output_publish, output_author, output_pages = ("",) * 7      
    error_name, error_genres, error_desc, error_year, error_publish, error_author, error_pages = (False,) * 7

    # print("name", params_to_check.get('name'))
    if params_to_check.get('name') == "":
        output_name = "Поле не должно быть пустым."
        error_name = True
        print("name")

    print("desc", params_to_check.get('description'))
    if params_to_check.get('description') == "":
        output_desc = "Поле не должно быть пустым."
        error_desc = True
        print("desc")

    print("year", params_to_check.get('year'))
    if params_to_check.get('year') == "":
        output_year = "Поле не должно быть пустым."
        error_year = True
        print("year empty")
    # год находится в пределах разрешенных >1901 и длина 4
    elif len(params_to_check.get('year')) == 4:
        print("year lenght")
        check_year = params_to_check.get('year')
        print("check_year", params_to_check.get('year'))
        available_char = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for i in check_year:
            if i not in available_char:
                error_year = True
                output_year = 'Недопустимый ввод. Встречаются недопустимые символы.'               
                break    
        if error_year == False:
            if int(check_year) < 1901:
                print("int(check_year)", int(check_year))
                output_year = 'Недопустимый ввод. Недопустимый год.'     
                error_year = True
    else:
        print("year letters")
        output_year = 'Недопустимый ввод. Недопустимое количество цифр.'     
        error_year = True

    print("publisher", params_to_check.get('publisher'))
    if params_to_check.get('publisher') == "":
        output_publish = "Поле не должно быть пустым."
        error_publish = True
        print("publisher")
    
    print("author", params_to_check.get('author'))
    if params_to_check.get('author') == "":
        output_author = "Поле не должно быть пустым."
        error_author = True
        print("author")

    print("pages", params_to_check.get('pages'))
    if params_to_check.get('pages') == "":
        output_pages = "Поле не должно быть пустым."
        error_pages = True
        print("pages empty")
    else: 
        print("pages letter")
        check_pages = params_to_check.get('pages')
        # print("check_year", params_to_check.get('year'))
        available_char = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        for i in check_pages:
            # print("i",i)
            if i not in available_char:
                # print("i->", i)
                print("pages letter2")
                error_pages = True
                output_pages = 'Недопустимый ввод. Встречаются недопустимые символы.'               
                break    
    #проверка на пустоту жанров
    genres = Genre.query.all()
    print("genres", genres)
    if error_name == False and error_desc == False and error_year == False and error_publish == False and error_author == False and error_pages == False:
        return [True]
    else:
        return [False, render_template('books/new.html', user = params_to_check, m = True, genres=genres,
                        output_name=output_name, error_name=error_name,
                        output_desc=output_desc, error_desc=error_desc,
                        output_year=output_year, error_year=error_year,
                        output_publish=output_publish, error_publish=error_publish,
                        output_author=output_author, error_author=error_author,
                        output_pages=output_pages, error_pages=error_pages)]

# расчет рейтинга книги
def calc_rating(book_id):
    # запрос на расчет среднего значения оценок книги
    rating = db.session.query(func.avg(Review.rating).label('average')).filter(Review.book_id == book_id).first()
    if rating[0] == None:
        rating = 0
    else:
        rating = round(rating[0], 2)
    return rating

# получение уже выбранных жанров при редактировании книги
def get_genres():
    genres = Genre.query.all()
    choose_genres = []   
    for genre in genres:
        if  request.form.get(str(genre.id)) != None:
            choose_genres.append(genre)
    return choose_genres

# получение выбранных чекбоксов для сортировки книг по году/ам
def get_yaers_for_sort():
    years = db.session.query(Book.year).all()
    choose_years = []   
    for year in years:
        if  request.form.get(str(year)) != None:
            choose_years.append(year)
    return choose_years

# получение списка жанров для их вывода на главной странице с чекбоксами
def get_genres_main_page():
    genres = db.session.query(Genre.name).all()
    return  genres

# получение списка готов для их вывода на главной странице с чекбоксами
def get_years():
    years = db.session.query(Book.year).all()
    new_years = []
    for y in years:
        new_years.append(y[0])
    return  new_years

# перечень параметров для поиска книг
def search_params():
    return {
        'name': request.args.get('name'),
        'genres': get_genres(),
        'year': get_yaers_for_sort(),
        'author': request.args.get('author'),
        'pages': request.args.get('pages')
    }

@bp.route('/')
def index():
    # отображение спика существующих жанров и годов для сортировки
    years = get_years()
    genres = get_genres_main_page()

    page = request.args.get('page', 1, type=int)
    books = BooksFilter(**search_params()).perform()
    pagination = books.paginate(page, PER_PAGE)
    for book in books:
        book.rating = calc_rating(book.id)
        book.reviews = db.session.query(Review).filter(Review.book_id == book.id).count()
    books = pagination.items
    return render_template('index.html',
                           books=books, pagination=pagination,
                           search_params=search_params(), years=years, genres=genres)

@bp.route('/new')
@login_required
@permission_check('create')
def new():
    users = User.query.all()
    genres = Genre.query.all()
    m = False
    book = Book(**params(), cover_id='', genres=genres)
    return render_template('books/new.html', genres=genres, users=users, book=book, m=m)

# функция добавления новой книги
@bp.route('/create', methods=['POST'])
@login_required
@permission_check('create')
def create():
    # print("qwertyuiop[]")
    f = request.files.get('background_img')
    if f and f.filename:
        img = ImageSaver(f).save()
    # отслеживание выбранных жанров
    genres = get_genres()
    
    check_res = check_params(params())
    # print("check_res", check_res[0])
    if not check_res[0]:
        return check_res[1]
    else:
        try:
            book = Book(**params(), cover_id=img.id, genres=genres)
            # запрос на добавление и его комит
            db.session.add(book)
            db.session.commit()
            flash(f'Книга {book.name} была успешно добавлена!', 'success')
        except exc.SQLAlchemyError: 
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введенных данных.', 'danger')
     
        return redirect(url_for('books.index'))

# функция просмотра выбранной книги
@bp.route('/<int:book_id>')
@login_required
@permission_check('show')
def show(book_id):
    #запросы на вывод книги, рецензий и подсчет рейтинга
    book = Book.query.get(book_id)
    book.description = markdown.markdown(book.description)

    reviews_all = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).all()
    reviews_count = db.session.query(Review).filter(Review.book_id == book.id).count()
    book_rating = calc_rating(book.id)
    users = User.query.all()

    # для вывода жанров
    genres_name = []
    for genre in book.genres:
        genres_name.append(genre.name)
    genres_name = ', '.join(genres_name)

    # проверка писал ли пользователь рецензию
    flag_reviews = False
    for review in reviews_all:
        if review.user_id == current_user.id:
            flag_reviews = True
    # вывод пяти рецензий в сокращенном вариаенте просмотра
    reviews_lim5 = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc()).limit(5).all()

    return render_template('books/show.html', book=book, reviews_all=reviews_all, reviews_lim5=reviews_lim5, 
        users=users, flag=flag_reviews, book_id=book_id, book_rating=book_rating, genres_name=genres_name, reviews_count=reviews_count)

# функция редактирования выбранной книги
@bp.route('/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@permission_check('edit')
def edit(book_id):
    print("edit")
    new_data = params()
    update_data = {}
    # запрос жанров и книги
    genres_all = Genre.query.all()
    book = Book.query.get(book_id)
    # print("edit book name", book.name)

    if request.method == 'GET':
        # отображение выбранных жанров
        book_genres = []
        for genre in book.genres:
            book_genres.append(genre.name)       
        return render_template('books/edit.html',
                           genres=genres_all,
                           book=book, book_genres=book_genres)
    else:
        # сохранение изначальныфх данных книги для сранения
        old_data = {"name" : book.name, "description" : book.description, "year" : book.year, 
                  "publisher" : book.publisher, "author" : book.author, "pages" : book.pages,
                  "genres" : book.genres}

        # отслеживание измененных параметров
        for p in BOOK_PARAMS:
            if str(old_data.get(p)) != new_data.get(p):
                update_data[p] = new_data.get(p)
        #были ли вообще изменения
        if update_data != {}:
            try:
                Book.query.filter_by(id = book_id).update(update_data)
                db.session.commit()
            except exc.SQLAlchemyError: 
                db.session.rollback()
                flash('При обервлении данных возникла ошибка. Проверьте корректность введенных данных.', 'danger')
        # отслеживание измененных жанров
        new_genres = get_genres()
        if  old_data.get("genres") != new_genres:
            for genre in genres_all:
                # запрос значений из бд
                my_book = db.session.query(Book).get(book_id)
                my_genre = db.session.query(Genre).get(genre.id)
                # добавление новых жанров
                my_book.genres.append(my_genre)
                try:
                    db.session.commit()
                except exc.SQLAlchemyError: 
                    db.session.rollback()
                    flash('При обервлении данных возникла ошибка. Проверьте корректность введенных данных.', 'danger')
                if genre not in new_genres:
                    try:  
                        my_book.genres.remove(my_genre)
                        db.session.commit()
                    except exc.SQLAlchemyError: 
                        db.session.rollback()
                        flash('При обервлении данных возникла ошибка. Проверьте корректность введенных данных.', 'danger')
        flash('Изменения успешно внесены.', 'success')
        return redirect(url_for('index'))

# удаление книги
@bp.route('/books/<int:book_id>/delete', methods=['GET', 'POST'])
@login_required
@permission_check('delete')
def delete(book_id):
    try:      
        print("ascefewf")
        flash('Книга удалена.', 'success')
        book = Book.query.get(book_id)
        db.session.delete(book)
        db.session.commit()
    except exc.SQLAlchemyError: 
        print("asdffgh")
        db.session.rollback()
        flash('При удалении данных возникла ошибка. Проверьте корректность введенных данных.', 'danger')
    return redirect(url_for('index'))

# отображение рецензий 
@bp.route('/<int:book_id>/reviews', methods=['GET', 'POST'])
@login_required
def reviews(book_id):
    book = Book.query.get(book_id)
   
    page = request.args.get('page', 1, type=int)
    five_per_page = 5 

    sort_by = request.args.get('sort_by', 'new', type=str)
    if sort_by == 'positive':
        order_by = Review.rating.desc() 
    elif sort_by == 'negative':
        order_by = Review.rating.asc() 
    else:
        order_by = Review.created_at.desc() 

    reviews_all = Review.query.filter_by(book_id=book_id)\
        .join(User)\
        .add_columns(User.login)\
        .add_columns(User.last_name)\
        .add_columns(User.first_name)\
        .order_by(order_by)\
        .paginate(page, five_per_page, error_out=False)
    
    if current_user.is_authenticated:
        flag = False
        existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
        if existing_review:
            # есть отзыв от пользователя
            flag = True 
    else:
        flag = None 
    return render_template('books/reviews.html', book=book, reviews_all=reviews_all, flag=flag, sort_by=sort_by, per_page=five_per_page, page=page)

# отображение всего списка рецензий на книгу
@bp.route('/<int:book_id>/reviews', methods=['GET'])
@login_required
@permission_check('look_review')
def view_reviews(book_id):
    book = Book.query.get(book_id)
    book.text = markdown.markdown(book.text)

    reviews = Review.query.filter_by(book_id=book_id).order_by(Review.created_at.desc())
    users = User.query.all()
    return render_template('books/reviews.html', book=book, reviews=reviews, users=users)

# добавление рецензий
@bp.route('/<int:book_id>/add_review', methods=['POST'])
@login_required
def add_review(book_id):
    if not current_user.is_authenticated:
        print("111111111")
        flash('Для оставления отзыва необходимо войти в свой аккаунт.', 'warning')
        return redirect(url_for('auth.login'))
    print("2222222")
    rating = int(request.form['rating'])
    text = request.form['text_review']

    print("333333333333")
    if rating < 0 or rating > 5:
        flash('Недопустимая оценка', 'danger')
        return redirect(url_for('books.show', book_id=book_id))

    print("555555")
    existing_review = Review.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing_review:
        flash('Вы уже оставили отзыв для этого курса.', 'danger')
        return redirect(url_for('books.show', book_id=book_id))

    print("6666666")
    review = Review(rating=rating, text=text, created_at=func.now(), book_id=book_id, user_id=current_user.id)
    db.session.add(review)
    db.session.commit()

    flash('Отзыв успешно добавлен.', 'success')
    return redirect(url_for('books.show', book_id=book_id))
