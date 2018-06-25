from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, db
from sqlalchemy.sql import func


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password_hash = Column(String)
    money = Column(Integer)
    players = db.relationship('Player', backref='user', lazy='dynamic')
    bids = db.relationship('Bid', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return "<User(name='%s', password='%s')>" % (
            self.name, self.password_hash)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Player(db.Model):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    surname = Column(String)
    team = Column(String)
    roles = Column(String)
    assigned = Column(Integer)
    assigned_value = Column(Integer)
    assigned_user_id = Column(Integer, db.ForeignKey('users.id'))
    bids = db.relationship('Bid', backref='player', lazy='dynamic')

    def is_assigned(self):
        if self.assigned == 0:
            return False
        else:
            return True

    def __repr__(self):
        return "<Player(name='%s', surname='%s', team='%s')>" % (
            self.name, self.surname, self.team)

class Bid(db.Model):
    __tablename__= 'bids'
    id = Column(Integer, primary_key=True)
    bid = Column(Integer)
    time = Column(DateTime, default=db.func.current_timestamp())
    active = Column(Integer)
    current_time = db.func.current_timestamp()
    user_id = Column(Integer, db.ForeignKey('users.id'))
    player_id = Column(Integer, db.ForeignKey('players.id'))
