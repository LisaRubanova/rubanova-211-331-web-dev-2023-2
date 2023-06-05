from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required

#login_user регистрация/авторизация пользователя
#flash для вывода сообещений
#logout_user  выход пользователя , удаление сессионной перемнной
#login_required -   требуют входа пользователя
#flask_login  вход выход сеансы
#session глобальный объект, сохранение состояния, словарь для данных между запросами
#login_user используется в current_user

#инициализация приложения
app = Flask(__name__)
application = app

app.config.from_pyfile('config.py')
#LoginManager - управление аутент
login_manager = LoginManager()
login_manager.init_app(app) #настройка для входа в систему
login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно авторизироваться.'
login_manager.login_message_category = 'warning'

#UserMixin класс, содержит методы , id, аутент., активная ли запись
class User(UserMixin): #класс для обпередения модели пользователя, методы для авторизации
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/visits')
def visits():
    if 'visits_count' in session:
        session['visits_count'] += 1
    else:
        session['visits_count'] = 1
    return render_template('visits.html')

#функция login вызывается когда пользователь пытается авторизоваться 
@app.route('/login', methods=['GET', 'POST']) #метод авторизации
def login():
    # request создает объект запроса
    if request.method == 'POST': # доступ к HTTP-методу
        login = request.form['login'] #доступ к полям, передаваемым в HTML-форме.
        password = request.form['password'] #доступ к полям, передаваемым в HTML-форме.
        remember = request.form.get('remember_me') == 'on'
        
        for user in get_users():
            if user['login'] == login and user['password'] == password:
                login_user(User(user['id'], user['login']), remember = remember)
                flash('Вы успешно прошли аутентификацию!', 'success') #для отображения сообщений
                param_url = request.args.get('next')#чтобы сохранялась стр на которую хотел юзер до авториз
                return redirect(param_url or url_for('index')) #попадет на нее после авторизации
        flash('Введён неправильный логин или пароль.', 'danger')
    return render_template('login.html')

@app.route('/logout', methods=['GET']) #метод разавторизации
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/secret_page')
@login_required
def secret_page():
    return render_template('secret_page.html')
#обратный вызов используется для перезагрузки объекта 
#пользователя из идентификатора пользователя, хранящегося в сеансе.

#load user для получения пользователя по id, позвращает объект
@login_manager.user_loader 
def load_user(user_id):
    for user in get_users():
        if user['id'] == int(user_id):
            return User(user['id'], user['login'])
    return None

def get_users():
    users = [{
        "id": 1,
        "login": "user",
        "password": "qwerty",
    }]
    return users