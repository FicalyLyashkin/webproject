from flask import Flask, redirect
from flask import render_template
from flask import request
from data import db_session
from data.login_form import LoginForm
from data.users import User
from data.rooms import Room
from data.create_room_form import CreateRoomForm
from flask_login import LoginManager, login_user, login_required, logout_user
from data.register_form import RegisterForm
from googleapiclient.discovery import build
from parse import parse
from data.join_room_form import JoinRoomForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '775664a9b6ace72dedb42f592cb19a2789935126497200fc1aee8eb2a12d23b9'
login_manager = LoginManager()
login_manager.init_app(app)
youtube = build('youtube', 'v3', developerKey='AIzaSyDBwGcZnOylzdtsu0VkHdY7m2d_QiM2hHQ')


def extract_video_id(url):
    pattern = "https://www.youtube.com/watch?v={video_id}"
    result = parse(pattern, url)
    if result:
        return result['video_id']
    else:
        return None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/join_room', methods=['POST', 'GET'])
def join_room():
    form = JoinRoomForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if not db_sess.query(Room).filter(Room.code == form.code.data).first():
            return render_template('join_room.html', form=form,
                                   messsage="Комнаты с таким номером не существует")
        room = db_sess.query(Room).filter(Room.code == form.code.data).first()
        if room and room.check_password(form.password.data):
            return redirect(f"/room{form.code.data}")

    return render_template('join_room.html', form=form)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    print('error')
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nikname=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/create_room', methods=['POST', 'GET'])
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if db_sess.query(Room).filter(Room.code == form.code.data).first():
            return render_template("create_room.html",
                                   title='Создать комнату',
                                   form=form,
                                   message="Такая комната уже есть")
        room = Room()
        room.code = form.code.data
        room.set_password(form.password.data)
        db_sess.add(room)
        db_sess.commit()
        return redirect(f"/room{form.code.data}")
    return render_template("create_room.html", title='Создать комнату', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/room<code>', methods=['GET', 'POST'])
def room(code):
    video_id = None
    if request.method == 'POST':
        url = request.form['link']
        video_id = extract_video_id(url)

    if video_id:
        return render_template('room.html', video_id=video_id, play=True)
    else:
        return render_template('room.html', play=False)


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')
