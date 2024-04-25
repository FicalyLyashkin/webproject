import os
from flask import Flask, redirect
from flask import render_template
from flask import request
from werkzeug.utils import secure_filename
import re
from data import db_session
from data.login_form import LoginForm
from data.users import User
from data.rooms import Room
from data.create_room_form import CreateRoomForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data.register_form import RegisterForm
from googleapiclient.discovery import build
from flask import jsonify
from data.join_room_form import JoinRoomForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '775664a9b6ace72dedb42f592cb19a2789935126497200fc1aee8eb2a12d23b9'
login_manager = LoginManager()
login_manager.init_app(app)
youtube = build('youtube', 'v3', developerKey='AIzaSyDBwGcZnOylzdtsu0VkHdY7m2d_QiM2hHQ')
UPLOAD_FOLDER = '/static/img/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def extract_video_id(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.match(youtube_regex, url)
    if youtube_regex_match:
        return youtube_regex_match.group(6)
    return None

@app.route('/update_video', methods=['POST'])
@login_required
def update_video():
    room_id = request.json.get('room_id')
    url = request.json.get('url')
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == room_id).first()
    if room.leader_id != current_user.id:
        return jsonify({'error': 'Only the leader can update the video'}), 403

    video_id = extract_video_id(url)
    if video_id:
        room.video_link = f"https://www.youtube.com/embed/{video_id}?autoplay=1&controls=0"
        db_sess.commit()
        return jsonify({'video_id': video_id})
    else:
        return jsonify({'error': 'Invalid YouTube URL'}), 400

@app.route('/update_time', methods=['POST'])
@login_required
def update_time():
    db_sess = db_session.create_session()
    room_id = request.json.get('room_id')
    current_time = request.json.get('current_time')
    room = db_sess.query(Room).filter(Room.code == room_id).first()
    if room and room.leader_id == current_user.id:
        room.current_time = current_time
        db_sess.commit()
        return jsonify({'message': 'Time updated'}), 200
    return jsonify({'error': 'Not authorized or room not found'}), 400

@app.route('/get_time', methods=['GET'])
def get_time():
    db_sess = db_session.create_session()
    room_id = request.args.get('room_id')
    room = db_sess.query(Room).filter(Room.code == room_id).first()
    if room:
        return jsonify({'current_time': room.current_time}), 200
    return jsonify({'error': 'Room not found'}), 404

@app.route('/current_video')
def current_video():
    room_id = request.args.get('room_id')
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == room_id).first()
    if room and room.video_link:
        return jsonify({'video_link': room.video_link})
    return jsonify({'error': 'No video currently available'}), 404

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

        image = form.icon.data
        filename = secure_filename(image.filename)
        image.save(os.path.join('static/img', filename))

        user = User()
        user.nikname = form.name.data
        user.email = form.email.data
        user.icon = filename
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/create_room', methods=['POST', 'GET'])
@login_required
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
        room.leader_id = current_user.id
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
    db_sess = db_session.create_session()
    room = db_sess.query(Room).filter(Room.code == code).first()
    if not room:
        return "Комната не найдена", 404

    if request.method == 'POST' and request.is_json:
        url = request.json['url']
        video_id = extract_video_id(url)
        if video_id:
            room.video_link = f"https://www.youtube.com/embed/{video_id}?autoplay=1&controls=0"
            db_sess.commit()
            return jsonify({'video_id': video_id})
        return jsonify({'error': 'Invalid YouTube URL'}), 400

    if request.method == 'POST':
        url = request.form['link']
        video_id = extract_video_id(url)
        if video_id:
            room.video_link = f"https://www.youtube.com/embed/{video_id}?autoplay=1&controls=0"
            db_sess.commit()
            return render_template('room.html', room=room, room_code=code, video_id=video_id, play=True)
        else:
            return render_template('room.html', room=room, room_code=code, play=False)

    return render_template('room.html', room=room, room_code=code, video_link=room.video_link)


if __name__ == '__main__':
    db_session.global_init("db/users.db")
    app.run(port=8080, host='127.0.0.1')
