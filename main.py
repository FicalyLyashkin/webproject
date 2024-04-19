from flask import Flask
from flask import render_template

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


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/registration')
def registration():
    return render_template('registration.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
