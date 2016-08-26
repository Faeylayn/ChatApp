from flask import Flask, g
from flask_restful import Resource, Api, reqparse
import sqlite3
import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, send, emit

Base = declarative_base()

class User(Base):
    __tablename__ = 'ChatUser'
    id = Column(Integer, primary_key=True)
    UserName = Column(String(250), nullable=False)


class Message(Base):
    __tablename__ = 'Message'
    id = Column(Integer, primary_key=True)
    Text = Column(Text, nullable=False)
    PostTime = Column(Integer, nullable=False)
    UserName = Column(String(250), nullable=False)

engine = create_engine('sqlite:///chatapp.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

app = Flask(__name__)
CORS(app)
api = Api(app)
socketio = SocketIO(app)

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0

class LoginUser(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('UserName', type=str, help='user_name address to lookup/create user')
            args = parser.parse_args()

            user_name = args['UserName']
            user = session.query(User).filter(User.UserName == user_name).first()
            if user is not None:
                return {"Message": "Existing User"}
            else:
                new_person = User(UserName=user_name)
                session.add(new_person)
                session.commit()

            return {'user_name': user_name}

        except Exception as e:
            return {'error': str(e)}

api.add_resource(LoginUser, '/LoginUser')

class PostMessage(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('UserName', type=str, help='User id of the posting user')
            parser.add_argument('Text', type=str, help='text of the message')
            args = parser.parse_args()
            print args

            user_name = args['UserName']
            text = args['Text']

            new_message = Message(Text=text, UserName=user_name, PostTime=unix_time_millis(datetime.datetime.utcnow()))
            session.add(new_message)
            session.commit()

            return {
            'text': new_message.Text,
            'Time': new_message.PostTime,
            'UserName': user_name
            }

        except Exception as e:
            return {'error': str(e)}

api.add_resource(PostMessage, '/PostMessage')

@socketio.on('Message Sent')
def handle_my_custom_event(data):
    emit('Message Posted', data, broadcast=True)

class RetreiveMessages(Resource):
    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('earliest', type=str, help='Flag if the request should just pull new messages')
            args = parser.parse_args()
            earliest_time = args['earliest']

            if earliest_time is None:
                messages = session.query(Message).order_by(Message.id.desc()).limit(20).all()
            else:
                messages = session.query(Message).filter(Message.PostTime < earliest_time).order_by(Message.id.desc()).limit(20).all()
            return_messages = []
            messages.reverse()

            for message in messages:
                mess_dict = {
                'text': message.Text,
                'UserName': message.UserName,
                'Time': message.PostTime
                }
                return_messages.append(mess_dict)

            return {
            'Message': return_messages
            }

        except Exception as e:
            return {'error': str(e)}

api.add_resource(RetreiveMessages, '/RetreiveMessages')

if __name__ == '__main__':
    socketio.run(app)
