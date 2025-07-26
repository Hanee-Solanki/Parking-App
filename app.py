from flask import Flask, render_template,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_login import UserMixin,LoginManager,login_user,logout_user,current_user
from datetime import datetime,timezone
from flask_bcrypt import Bcrypt
from functools import wraps
from models import db,User,ParkingLot,ParkingSpot,Reservation
from collections import defaultdict
import random

app = Flask(__name__)

#configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='wsxedcr'
#app.config['SECURITY_PASSWORD_SALT']='eenah%%kicn'
#app.config['SECURITY_REGISTERABLE']=True


#connecting database and app with init_app
db.init_app(app)

#initializing Bcrypt
bcrypt = Bcrypt(app)

login_manager=LoginManager()
login_manager.init_app(app)

#default login view if the user tries to access a page without being logged in
login_manager.login_view='user_login'
login_manager.login_message_category='info'
login_manager.login_message="Please log in to access this page"

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)

#custom decorator for admin access
def user_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('user_login'),next=request.url)
        return f(*args,**kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if not current_user.is_authenticated:
            flash('Admin access required. Please log in','warning')
            return redirect(url_for('admin_login',next=request.url))
        if getattr(current_user,'role',None) != 'admin':
            flash('You do not have permission to acccess this page','danger')
            return redirect(url_for('user_dashboard'))
        return f(*args,**kwargs)
    return decorated_function        



def create_admin():
    admin = User.query.filter_by(username='Hanee').first()
    if not admin:
        hashed_password=bcrypt.generate_password_hash('Parkadmin@2025').decode('utf-8')
        admin = User(username='Hanee',email='24f3005318@ds.study.iitm.ac.in',password=hashed_password,role='admin')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user_dashboard'))
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username,role='user').first()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user)
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)                      
            return redirect(url_for('user_dashboard'))
        else:
            flash('Login failed. Invalid credentials','danger')
    return render_template("/user_login.html")

@app.route('/user_registration',methods=['GET','POST'])
def user_registration():
    if request.method=='POST':
        username = request.form['username']
        email=request.form['email']
        password=request.form['password']
        existing_username=User.query.filter_by(username=username).first()
        if not existing_username:
            hashed_password=bcrypt.generate_password_hash(password).decode('utf-8')
            new_user=User(username=username,email=email,password=hashed_password,role='user')
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been successfully created!','success')
            return redirect(url_for('user_login'))
        else:
            flash('Username already exists. Try a different name','error')
    return render_template("/user_registration.html")

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if current_user.is_authenticated and current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    if request.method=="POST":
        username=request.form['username']
        password=request.form['password']
        user=User.query.filter_by(username=username,role='admin').first()
        if user and bcrypt.check_password_hash(user.password,password):
            login_user(user)
            next_page=request.args.get('next')
            if next_page:
                return redirect(next_page)  
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login failed. Invalid credentials','danger')
    return render_template('/admin_login.html')

@app.route('/logout')
@user_required
def logout():
    #return to the correct login page based on role
    logout_user()
    flash('You have been logged out','success')
    return redirect(url_for('home'))          


#Functions for Admin Dashboard
@app.route('/admin_dashboard',methods=['GET','POST'])
@admin_required
def admin_dashboard():
    users=User.query.filter_by(role='user')
    reservations=Reservation.query.all()
    parkinglots=ParkingLot.query.all()
    total_spots = ParkingSpot.query.count()
    occupied_spots=ParkingSpot.query.filter_by(status='O').count()
    total_revenue=0.0
    for r in reservations:
        if r.end_time:
            total_revenue=total_revenue+r.charges
    spot_data = [total_spots,occupied_spots]
    return render_template('admin_dashboard.html',users=users,reservations=reservations,parkinglots=parkinglots,total_revenue=total_revenue,spot_data=spot_data)

@app.route('/create_lot',methods=['GET','POST'])
@admin_required
def create_lot():
    if request.method=='POST':
        lot_id=generate_lot_id()
        location_name=request.form['location_name']
        address=request.form['address']
        postal_code=request.form['postal_code']
        max_spots=int(request.form['max_spots'])
        price=int(request.form['price'])
        new_lot=ParkingLot(lot_id=lot_id,location_name=location_name,address=address,postal_code=postal_code,max_spots=max_spots,price=price)
        db.session.add(new_lot)
        db.session.commit()
        
        #creating spots in the lot
        for i in range(max_spots):
            new_spot=ParkingSpot(lot_id=lot_id,)
            db.session.add(new_spot)
        db.session.commit()

        return redirect(url_for('admin_dashboard'))
    return render_template('create_lot.html')

#generating customized lot id for Calgary city that starts with number 8
#Assuming that owner can own upto 999 parking lots, so range is 8001-8999
def generate_lot_id():
    while True:
        new_lot_id=random.randint(8001,8999)
        if not ParkingLot.query.filter_by(lot_id=new_lot_id).first():
            return new_lot_id

@app.route('/view_lot/<int:lot_id>',methods=['GET','POST'])
@admin_required
def view_lot(lot_id):
    parkingspots=ParkingSpot.query.filter_by(lot_id=lot_id)
    lot_location=getattr(ParkingLot.query.get_or_404(lot_id),'location_name')
    return render_template('view_lot.html',parkingspots=parkingspots,location_name=lot_location)    

@app.route('/edit_lot/<int:lot_id>',methods=['GET','POST'])
@admin_required
def edit_lot(lot_id):
    parkinglot=ParkingLot.query.get_or_404(lot_id)
    if request.method=='POST':
        new_max_spots=int(request.form['max_spots'])
        parkinglot.price=int(request.form['price'])
        current_spots=parkinglot.max_spots
        if new_max_spots<current_spots:
            occupied=ParkingSpot.query.filter_by(lot_id=lot_id).join(Reservation).filter(Reservation.end_time==None).count()
            if new_max_spots<occupied:
                flash('Cannot reduce the lot as some spots are still occupied','danger')
                return redirect(url_for('edit_lot',lot_id=lot_id))
            else:
                spots_to_reduce=ParkingSpot.query.filter_by(lot_id=lot_id).limit(current_spots-new_max_spots).all()
                for spot in spots_to_reduce:
                    if spot.status=='A':
                        db.session.delete(spot)
        elif new_max_spots>current_spots:
            for i in range(current_spots+1,new_max_spots+1):
                new_spot=ParkingSpot(lot_id=lot_id)
                db.session.add(new_spot)
        parkinglot.max_spots=new_max_spots
        db.session.commit()
        flash('Updated successfully','success')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_lot.html',parkinglot=parkinglot)

@app.route('/delete_lot/<int:lot_id>',methods=['POST'])
@admin_required
def delete_lot(lot_id):
    parkinglot=ParkingLot.query.get_or_404(lot_id)
    #checking if any spot is occupied    
    occupied_spot=ParkingSpot.query.filter_by(lot_id=lot_id,status='O').first()
    if occupied_spot:
        flash('Cannot deleted an occupied parking lot','danger')
        return redirect(url_for('view_lot',lot_id=lot_id))
    else:
        db.session.delete(parkinglot)
        db.session.commit()    
        flash('Parking Lot deleted successfully','success')
        return redirect(url_for('admin_dashboard'))


@app.route('/view_user_history/<int:user_id>')
@admin_required
def view_user_history(user_id):
    reservations=Reservation.query.filter_by(user_id=user_id).all()
    return render_template('transaction_history.html',reservations=reservations)

#Functions for User Dashboard
@app.route('/user_dashboard',methods=['GET','POST'])
@user_required
def user_dashboard():
    user=User.query.filter_by(id=current_user.id).first()
    reservations=Reservation.query.filter_by(user_id=current_user.id).all()
    reservation_counts=(
        db.session.query(ParkingLot.location_name,func.count(Reservation.reservation_id))
        .join(ParkingSpot,ParkingLot.lot_id==ParkingSpot.lot_id)
        .join(Reservation,Reservation.stall_id==ParkingSpot.stall_id)
        .filter(Reservation.user_id==current_user.id)
        .group_by(ParkingLot.location_name)
        .all()
    )
    lot_labels=[row[0] for row in reservation_counts]
    lot_counts=[row[1] for row in reservation_counts]
    
    return render_template("user_dashboard.html",user=user,reservations=reservations,lot_labels=lot_labels,lot_counts=lot_counts)


@app.route('/transaction_history')
@user_required
def transaction_history():
    return render_template('transaction_history.html',reservations=current_user.reservations)


@app.route('/reserve',methods=['GET','POST'])
@user_required
def reserve():
    parkinglots=ParkingLot.query.all()
    if request.method=='POST':
        lot_id=request.form['lot_id']
        available_spot=ParkingSpot.query.filter_by(lot_id=lot_id,status='A').first()
        if available_spot:
            available_spot.status='O'
            reservation=Reservation(stall_id=available_spot.stall_id,user_id=current_user.id)
            db.session.add(reservation)
            db.session.commit()
            flash("Reservation Successful!","success")
        else:
            flash("No available spots in this lot","danger")
        return redirect(url_for('user_dashboard'))
    return render_template('reserve.html',parkinglots=parkinglots)

@app.route('/release/<int:reservation_id>',methods=['POST'])
@user_required
def release(reservation_id):
    reservation=Reservation.query.get_or_404(reservation_id)
    if reservation.user_id!=current_user.id:
        flash('Unauthorized access','danger')
        return redirect(url_for('user_dashboard'))
    if reservation.end_time is None:
        reservation.end_time=datetime.now(timezone.utc)
        start=reservation.start_time
        end=reservation.end_time
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        duration=(end-start).total_seconds()/3600 
        reservation.charges=round(duration*reservation.stall.lot.price,2)
        reservation.stall.status='A'
        db.session.commit()
        flash('Spot is released','success')
    else:
        flash('This spot has already been released','warning')          
    return redirect(url_for('user_dashboard'))

#Run the app and create database
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_admin()
    app.debug=True
    app.run()
