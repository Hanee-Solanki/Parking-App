from datetime import datetime
from flask_sqlalchemy import SQLAlchemy,UserMixin,RoleMixin
db = SQLAlchemy()

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password=db.Column(db.String(128),nullable=False)
    role_id = db.Column(db.String(8),db.ForeignKey('role.role_id'),nullable=False)
    roles=db.relationship('Role',secondary='user_roles')

class Role(db.Model,RoleMixin):
    role_id = db.Column(db.String(8),primary_key=True)
    role_name=db.Column(db.String(30),unique=True)

class ParkingLot(db.Model):
    lot_id = db.Column(db.String(10),primary=True)
    location_name = db.Column(db.String(30),nullable=False)
    address = db.Column(db.String(200),nullable=False)
    postal_code = db.Column(db.String(6),nullable=False)
    price = db.Column(db.Integer,nullable=False)
    max_spots = db.Column(db.Integer,nullable=False)
    spots = db.relationship('ParkingSpot',backref='lot',cascade='all, delete',lazy=True)

class ParkingSpot(db.Model):
    stall_id = db.Column(db.Integer,primary=True)
    lot_id = db.Column(db.String(10),db.ForeignKey('parkinglot.lot_id'),nullable=False)
    status = db.Column(db.String(1),default='A')

class Reservation(db.Model):
    reservation_id = db.Column(db.Integer,primary=True)
    stall_id = db.Column(db.Integer,db.ForeignKey('parkingspot.stall_id'),nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    start_time = db.Column(db.DateTime,nullable=False)
    end_time =  db.Column(db.DateTime)
    charges = db.Column(db.Float)
    user = db.relationship('User',backref='reservations')
    stall = db.relationship('ParkingSpot',backref='reservations')


