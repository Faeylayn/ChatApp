from flask import Flask, g
from flask_restful import Resource, Api, reqparse
import sqlite3
import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, create_engine
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
    PostTime = Column(DateTime, nullable=False)
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

            user_name = args['UserName']
            text = args['Text']

            new_message = Message(Text=text, UserName=user_name, PostTime=datetime.datetime.utcnow())
            session.add(new_message)
            session.commit()

            return {
            'text': new_message.Text,
            'Time': new_message.PostTime.isoformat(),
            'UserName': user_name
            }

        except Exception as e:
            return {'error': str(e)}

api.add_resource(PostMessage, '/PostMessage')

@socketio.on('Message Sent')
def handle_my_custom_event(data):
    emit('Message Posted', data, broadcast=True)

class RetreiveMessages(Resource):
    def get(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('NewMessage', type=str, help='Flag if the request should just pull new messages')
            args = parser.parse_args()

            new_flag = args['NewMessage']

            messages = session.query(Message).limit(20).all()
            return_messages = []

            for message in messages:
                mess_dict = {
                'text': message.Text,
                'UserName': message.UserName
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
    # app.run()
