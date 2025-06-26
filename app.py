from flask import Flask, render_template,request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html",title="Home Page",username="Nee")

if __name__ == "__main__":
    app.debug=True
    app.run()
