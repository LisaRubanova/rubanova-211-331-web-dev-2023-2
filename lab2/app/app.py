from flask import Flask, render_template, request
from flask import make_response
import re

app = Flask(__name__)
application = app

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html'))
    if "name" in request.cookies:
        resp.delete_cookie("name")
    else:
        resp.set_cookie("name", "value")
    return resp

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.route('/calc', methods=['GET', 'POST'])
def calc():
    answer=''
    error_text=''
    if request.method=='POST':
        try:
            first_num = int(request.form['firstnumber'])
            second_num = int(request.form['secondnumber'])
        except ValueError:
            error_text='Был передан текст. Введите, пожалуйста, число.'
            return render_template('calc.html', answer=answer, error_text=error_text)
        operation = request.form['operation']
        if operation == '+':
            answer = first_num + second_num
        elif operation == '-':
            answer = first_num - second_num
        elif operation == '*':
            answer = first_num * second_num
        elif operation == '/':
            try:
                answer = first_num / second_num
            except ZeroDivisionError:
                error_text = 'На ноль делить нельзя'
    return render_template('calc.html', answer=answer, error_text=error_text)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

@app.route('/phone_number', methods=['GET', 'POST'])
def phone_number():
    error = False
    m = False
    error_text=''
    available_char = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "(", ")", "-", " ", "."]

    if request.method=='POST':
        m = True
        number = request.form['number']   
        for i in number:
            if i not in available_char:
                error = True
                error_text = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы.'               
                break    
        
        only_desimal = filter(str.isdecimal, number)
        number = "".join(only_desimal)
        # print(number)

        if error == False:          
            if len(number) == 10:
                error_text = "8-" + number[0:3] + "-" + number[3:6] + "-" + number[6:8] + "-" + number[8:10]
            elif len(number) == 11:
                error_text = number[0] + "-" + number[1:4] + "-" + number[4:7] + "-" + number[7:9] + "-" + number[9:11]
            else:
                error = True
                error_text = 'Недопустимый ввод. Неверное количество цифр.'
                
    return render_template('phone_number.html', m = m, error_text = error_text, error = error)
# +7 (123) 456-75-90
# 8(123)4567590
# 123.456.75.90
