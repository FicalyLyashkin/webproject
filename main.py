from flask import Flask
from flask import render_template
from flask import request

app = Flask(__name__)
app.config['SECRET_KEY'] = '775664a9b6ace72dedb42f592cb19a2789935126497200fc1aee8eb2a12d23b9'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_room')
def create_room():
    return render_template('create_room.html')


@app.route('/join_room')
def join_room():
    return render_template('join_room.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        print(request.form['auto_entry'])
        print(request.form['cancel'])
        print(request.form['register'])
        return render_template('index.html')

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        print(request.form['email'])
        print(request.form['password'])
        print(request.form['file'])
        print(request.form['auto_entry'])
        print(request.form['cancel'])
        print(request.form['login'])
        return render_template('index.html')

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
