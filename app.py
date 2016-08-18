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
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'ChatUser'
    id = Column(Integer, primary_key=True)
    UserName = Column(String(250), nullable=False)

# class Message(Base):
#     __tablename__ = 'address'
#     id = Column(Integer, primary_key=True)
#     street_name = Column(String(250))
#     street_number = Column(String(250))
#     post_code = Column(String(250), nullable=False)
#     person_id = Column(Integer, ForeignKey('person.id'))
#     person = relationship(Person)

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
            parser.add_argument('email', type=str, help='Email address to lookup/create user')
            args = parser.parse_args()

            _userEmail = args['email']
            try:
                user = session.query(User).filter(User.UserName == _userEmail).first()
                if user is not None:
                    return {"Message": "Existing User"}
            except Exception as e:
                new_person = User(UserName=_userEmail)
                session.add(new_person)
                session.commit()

            return {'Email': _userEmail}

        except Exception as e:
            return {'error': str(e)}

api.add_resource(LoginUser, '/LoginUser')

if __name__ == '__main__':
    app.run(debug=True)
