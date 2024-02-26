from flask import Flask, render_template, redirect, url_for, session, request, send_file
from flask_login import login_user
from flask_login import login_required
from time import gmtime, strftime
from flask_pymongo import PyMongo
from flask_login import LoginManager, logout_user, current_user
from utils.userlogin import UserLogin
from werkzeug.utils import secure_filename
import hashlib
import os


app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'Ilia_Zanin_HW2'
app.config['MONGO_URI'] = 'mongodb://127.0.0.1:27017/Ilia_Zanin_HW2'

login_manager=LoginManager(app)
login_manager.login_view = 'login'

UPLOAD_FOLDER = 'avatars'
ALLOWED_EXTENSIONS = {'png'}
DEFAULT_AVATAR = "static/profile_image.jpg" 

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, mongo)

mongo = PyMongo(app)

@app.route('/avatars/<string:avatar>')
@login_required
def avatar(avatar):
    print(avatar)
    return send_file(UPLOAD_FOLDER+'/'+ avatar)

@app.route('/profile')
@login_required
def profile():
    timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    username = current_user.get_user()
    has_avatar = current_user.has_avatar()
    has_summary = current_user.has_summary()
    if has_avatar:
        avatar = UPLOAD_FOLDER + '/' + current_user.get_user() + has_avatar
    else: 
        avatar = DEFAULT_AVATAR
    summary = has_summary if has_summary else None
    return render_template('advanced_profile.html', timestamp=timestamp, username=username, avatar=avatar, summary=summary)

@app.route('/')
@login_required
def index():
        return redirect(url_for('profile'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get("username")
        passwd = request.form.get("password")
        users = mongo.db.users
        user_object = users.find_one({"username": user })
        if user_object:
            if hashlib.sha256(passwd.encode()).hexdigest() == user_object['password']:
                rm = True if request.form.get("remainme") else False
                userlogin=UserLogin().create(user_object)
                login_user(userlogin, remember=rm)
                return redirect(url_for('profile'))
        return "Invalid username or password"
    if request.method == 'GET':
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get("username")
        passwd = request.form.get("password")
        passwd = hashlib.sha256(passwd.encode()).hexdigest()
        users = mongo.db.users
        is_created = users.find_one({"username": user})
        if not is_created:
            is_registered = users.insert_one({"id": users.estimated_document_count()+1, "username": user, "password": passwd})
            if is_registered:
                return render_template('login.html')
            else:
                return "Error!"
        else:
            return "Account with such username already exists"
    if request.method == 'GET':
        return render_template('register.html')

@app.route('/chpass', methods = ['GET', 'POST'])
@login_required
def chpass():
    if request.method == 'GET':
        return render_template('change_pass.html')
    if request.method == 'POST':
        old_pass = request.form.get("old_password")
        new_pass = request.form.get("new_password")
        current_pass = current_user.get_pass()
        if hashlib.sha256(old_pass.encode()).hexdigest() == current_pass:
            new_pass = hashlib.sha256(new_pass.encode()).hexdigest()
            users = mongo.db.users
            users.update_one({"id": current_user.get_id()}, {'$set': {"password": new_pass}}, upsert=False)
            return render_template('pass_changed.html')
        else:
            return "Old password is wrong!"

@app.route('/chpic', methods = ['GET', 'POST'])
@login_required
def chpic():
    if request.method == 'GET':
        return render_template('change_avatar.html')
    if request.method == 'POST':
        if 'file' not in request.files:
            print("FAIL1")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print("FAIL2")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1]
            system_name = current_user.get_user()
            file.save(os.path.join(UPLOAD_FOLDER, system_name + ext))
            users = mongo.db.users
            users.update_one({"id": current_user.get_id()}, {'$set': {"has_avatar": ext}}, upsert=False)
            print("UPLOADED!")
            return redirect('/profile')
        else:
            return "Extension is not allowed!"
        
@app.route('/chprofile', methods = ['GET','POST'])
@login_required
def chprofile():
    if request.method == 'GET':
        return render_template('update_profile.html')
    if request.method == 'POST':
        new_summary = request.form.get("summary")
        users = mongo.db.users
        users.update_one({"id": current_user.get_id()}, {'$set': {"summary": new_summary}}, upsert=False)
        return redirect('/profile')

if __name__ == '__main__':
    app.secret_key = "secretkey"
    app.run(host='localhost', port=5000)
