# from flask import Flask
# app = Flask(__name__)
#
# @app.route("/")
# def main():
#     return "Welcome!"
#
# if __name__ == "__main__":
#     app.run()

from flask import Flask
from flask_restful import Resource, Api, reqparse
import sqlite3
from flask import g
# from flask.ext.mysql import MySQL
import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

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
    UserId = Column(Integer, ForeignKey('ChatUser.id'))
    User = relationship(User)

engine = create_engine('sqlite:///chatapp.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

# Insert a Person in the person table
# new_person = Person(name='new person')
# session.add(new_person)
# session.commit()


app = Flask(__name__)
api = Api(app)
#
# DATABASE = './chatapp.db'
#
# def get_db():
#     db = getattr(g, '_database', None)
#     if db is None:
#         db = g._database = sqlite3.connect(DATABASE)
#     return db
#
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()

# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'root123'
# app.config['MYSQL_DATABASE_DB'] = 'ChatAppDB'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)
# conn = mysql.connect()


class LoginUser(Resource):
    def post(self):
        try:
            # cur = get_db().cursor()
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
            # cur = get_db().cursor()
            parser = reqparse.RequestParser()
            parser.add_argument('UserId', type=str, help='User id of the posting user')
            parser.add_argument('Text', type=str, help='text of the message')
            args = parser.parse_args()

            user_id = args['UserId']
            text = args['Text']

            new_message = Message(Text=text, UserId=user_id, PostTime=datetime.datetime.utcnow())
            session.add(new_message)
            session.commit()

            return {
            'Message': new_message.Text,
            'Time': new_message.PostTime.isoformat()
            }

        except Exception as e:
            return {'error': str(e)}

api.add_resource(PostMessage, '/PostMessage')

class RetreiveMessages(Resource):
    def get(self):
        try:
            # cur = get_db().cursor()
            parser = reqparse.RequestParser()
            parser.add_argument('NewMessage', type=str, help='Flag if the request should just pull new messages')
            args = parser.parse_args()

            new_flag = args['NewMessage']

            messages = session.query(Message).limit(20).all()
            return_messages = []

            for message in messages:
                mess_dict = {
                'text': message.Text,
                'UserId': message.UserId
                }
                return_messages.append(mess_dict)

            return {
            'Message': return_messages
            }

        except Exception as e:
            return {'error': str(e)}

api.add_resource(RetreiveMessages, '/RetreiveMessages')

if __name__ == '__main__':
    app.run(debug=True)
