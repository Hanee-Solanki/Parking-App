from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html",title="Home Page",username="Nee")

#configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='wsxedcr'
app.config['SECURITY_PASSWORD_SALT']='eenah%%kicn'

db=SQLAlchemy(app)

#Run the app and create database
if __name__ == "__main__":
    app.debug=True
    app.run()
