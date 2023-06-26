import os

SECRET_KEY = '9695cce7d2daa4d9c7f952d1cca92b6c9183e5907262017d987e60de07801749'

SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://std_1880_exam:qwertyuiop@std-mysql.ist.mospolytech.ru/std_1880_exam'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

ADMIN_ROLE_ID = 1
MODER_ROLE_ID = 2


UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media', 'images')