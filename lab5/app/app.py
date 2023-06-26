import re

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from mysql_db import MySQL
import mysql.connector
PERMITED_PARAMS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
EDIT_PARAMS = ['last_name', 'first_name', 'middle_name', 'role_id']

app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')

db = MySQL(app)

#импортирование переменных BP 
from auth import bp as auth_bp
from auth import init_login_manager, permission_check

from visits import bp as visits_bp

#регистрация BP
app.register_blueprint(auth_bp)
init_login_manager(app)

app.register_blueprint(visits_bp)

@app.before_request
def loger():
    if request.endpoint == 'static':
        return
    path = request.path
    user_id = getattr(current_user, 'id', None)
    query = 'INSERT INTO visit_logs(user_id, path) VALUES (%s, %s);'
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (user_id, path))
            db.connection().commit()
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users')
def users():
    query = 'SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON roles.id = users.role_id'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        users_list = cursor.fetchall()
    
    return render_template('users.html', users_list=users_list)

@app.route('/users/new')
@login_required
@permission_check('create')
def users_new():
    roles_list = load_roles()
    return render_template('users_new.html', roles_list=roles_list, user={})

def load_roles():
    query = 'SELECT * FROM roles;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query)
    roles = cursor.fetchall()
    cursor.close()
    return roles

def extract_params(params_list):
    params_dict = {}
    for param in params_list:
        params_dict[param] = request.form.get(param, None)
    return params_dict

def check_pass_conditons(password):
    pattern_password = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-zа-яА-Я\d@$!#%*?&]{8,128}$')
    return bool(pattern_password.match(password))

def match(text, alphabet=set('абвгдеёжзийклмнопрстуфхцчшщъыьэюяqwertyuiopasdfghjklzxcvbnm')):
    return not alphabet.isdisjoint(text.lower())

def check_params(params):
    output_login, output_pass, output_f_n, output_l_n = ("",) * 4      
    error_login, error_pass, error_f_n, error_l_n = (False,) * 4

    pattern_login = re.compile(r'^[0-9a-zA-Z]{5,50}$')

    if params["login"] == None:
        output_login = "Поле не должно быть пустым."
        error_login = True
    elif not bool(pattern_login.match(params["login"])):
        output_login = "Введенный логин не соответствует требованиям."
        error_login = True

    if params["password"] == None:
        output_pass = "Поле не должно быть пустым."
        error_pass = True
    elif not check_pass_conditons(params['password']):
        # output_pass = "Введенный пароль не соответствует требованиям."
        # error_pass = True
        is_num = re.search('\d+', params['password']) is not None
        print("is_num", is_num)
        if not is_num:
            output_pass = "Введенный пароль не содержит хотя бы одну цифру."
            error_pass = True
            print("num")

        if not error_pass and len(params["password"]) < 8:
            output_pass = "Введенный пароль меньше 8 символов."
            error_pass = True
            print ("len < 8")

        if not error_pass and len(params["password"]) > 128:
            output_pass = "Введенный пароль больше 128 символов."
            error_pass = True
            print("len > 128")

        # is_letter = re.compile(r'^(?=.*[a-z].*)(?=.*[A-Z].*)$')
        flag = False
        for ch in params["password"]:
            if ch.isupper():
                flag = True
                break
        # print("----- is_letter", is_letter) 
        if not error_pass and not flag:
            output_pass = "Введенный пароль не содержит хотя бы одну заглавную."
            error_pass = True
            print("хотя бы 1 заг и стр буква")

        is_space = " " in params['password']
        print("----- пробел", is_space) 
        if not error_pass and is_space:
            output_pass = "Введенный пароль не допустает пробелов."
            error_pass = True
            print("пробел")

    if params["last_name"] == "":
        output_l_n = "Поле не должно быть пустым."
        error_l_n = True
    if params["first_name"] == "":
        output_f_n = "Поле не должно быть пустым."
        error_f_n = True
    
    if error_login == False and error_pass == False and error_f_n == False and error_l_n == False:
        return [True]
    else:
        return [False, render_template('users_new.html', user = params, roles_list = load_roles(), m = True,
                        output_login=output_login, error_login=error_login,
                        output_pass=output_pass, error_pass=error_pass,
                        output_f_n=output_f_n, error_f_n=error_f_n,
                        output_l_n=output_l_n, error_l_n=error_l_n)]

@app.route('/users/create',  methods=['POST', 'GET'])
@login_required
@permission_check('create')
def create_user():
    params = extract_params(PERMITED_PARAMS)


    check_res = check_params(params)
    if not check_res[0]:
        return check_res[1]
    else:

        query = 'INSERT INTO users(login, password_hash, last_name, first_name, middle_name, role_id) VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);'
        try:
            with db.connection().cursor(named_tuple=True) as cursor:
                cursor.execute(query, params)
                db.connection().commit()
                flash('Успешно!', 'success')
        except mysql.connector.errors.DatabaseError:
            db.connection().rollback()
            flash('При сохранении данных возникла ошибка.', 'danger')
            return render_template('users_new.html', user = params, roles_list = load_roles())
    
    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/update', methods=['POST', 'GET'])
@login_required
@permission_check('edit')
def update_user(user_id):
    print("try")
    params = extract_params(EDIT_PARAMS)
    print(params)
    params['id'] = user_id
    print("update")
    if current_user.can('change_role'):
        # print("can")
        query = ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, '
                'middle_name=%(middle_name)s, role_id=%(role_id)s WHERE id=%(id)s;')
    else:
        # print("cannot")
        del params['role_id']
        query = ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, '
                'middle_name=%(middle_name)s WHERE id=%(id)s;')
    # print(query)
    try:
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, params)
            db.connection().commit()
            flash('Успешно!', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При сохранении данных возникла ошибка.', 'danger')
        return render_template('users_edit.html', user = params, roles_list = load_roles())

    return redirect(url_for('users'))

@app.route('/users/<int:user_id>/edit')
@login_required
@permission_check('edit')
def edit_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users_edit.html', user=user, roles_list = load_roles())


@app.route('/users/<int:user_id>/delete',  methods=['POST', 'GET'])
@login_required
@permission_check('delete')
def delete_user(user_id):
    query = 'DELETE FROM users WHERE users.id=%s;'
    try:
        cursor = db.connection().cursor(named_tuple=True)
        cursor.execute(query, (user_id,))
        db.connection().commit()
        cursor.close()
        flash('Пользователь успешно удален', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При удалении пользователя возникла ошибка.', 'danger')
    return redirect(url_for('users'))


@app.route('/user/<int:user_id>')
@permission_check('show')
def show_user(user_id):
    query = 'SELECT * FROM users WHERE users.id = %s;'
    cursor = db.connection().cursor(named_tuple=True)
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    return render_template('users_show.html', user=user)


