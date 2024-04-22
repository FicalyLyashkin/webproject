from flask import Flask, redirect
from flask import render_template
from flask import request
from data import db_session
from data.login_form import LoginForm
from data.users import User
from flask_login import LoginManager, login_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '775664a9b6ace72dedb42f592cb19a2789935126497200fc1aee8eb2a12d23b9'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


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
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user:  # and user.check_password(form.password.data): нужно хэшировать пароль
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    print('error')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        user = User()
        user.nikname = request.form['nikname']
        user.email = request.form['email']
        user.hashed_password = request.form['password']
        user.icon = request.form['file']
        db_sess = db_session.create_session()
        db_sess.add(user)
        db_sess.commit()
        # print(request.form['auto_entry'])
        # print(request.form['cancel'])
        # print(request.form['login'])
        return render_template('index.html')


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')
