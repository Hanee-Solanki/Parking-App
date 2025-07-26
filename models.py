from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime,timezone
db=SQLAlchemy()

#database models
class User(db.Model,UserMixin):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True,nullable=False)
    email=db.Column(db.String(150),unique=True,nullable=False)
    password=db.Column(db.String(255),nullable=False)
    role = db.Column(db.String(8),nullable=False)
   

class ParkingLot(db.Model):
    __tablename__='parkinglots'
    lot_id = db.Column(db.Integer,primary_key=True)
    location_name = db.Column(db.String(30),nullable=False)
    address = db.Column(db.String(200),nullable=False)
    postal_code = db.Column(db.String(6),nullable=False)
    price = db.Column(db.Integer,nullable=False)
    max_spots = db.Column(db.Integer,nullable=False)

    #one lot has many spots
    spots = db.relationship('ParkingSpot',backref='lot',cascade='all, delete',lazy=True)

class ParkingSpot(db.Model):
    __tablename__='parkingspots'
    stall_id = db.Column(db.Integer,primary_key=True)
    lot_id = db.Column(db.Integer,db.ForeignKey('parkinglots.lot_id'),nullable=False)
    status = db.Column(db.String(1),default='A')
    

class Reservation(db.Model):
    __tablename__='reservations'
    reservation_id = db.Column(db.Integer,primary_key=True)
    stall_id = db.Column(db.Integer,db.ForeignKey('parkingspots.stall_id'))
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    start_time = db.Column(db.DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
    end_time =  db.Column(db.DateTime(timezone=True))
    charges = db.Column(db.Float)
    user = db.relationship('User',backref='reservations')
    stall = db.relationship('ParkingSpot',backref=db.backref('reservations',cascade='all,delete'))
