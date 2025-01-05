from flask import Flask, request
from models import Input, Food
from models import init_db
from foodscraper import FoodScraper
import os
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"))
db = SQLAlchemy(app)

foodscraper = FoodScraper(db, app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generator')
def generator():
    return render_template('MenuGen.html')

@app.route('/results', methods=['POST'])
def results():
    min_carbs = float(request.args.get('min_carbs')) # example
    input = Input() # should put arguments here
    return 'Generator Results'

@app.route('/documentation')
def documentation():
    return render_template('doc.html')

@app.route('/legal')
def legal():
    return render_template('legal.html')

@app.route('/cart')
def cart():
    return 'Shopping Cart'

@app.route('/profile')
def profile():
    return 'Profile'

@app.route('/signup')
def signup():
    return render_template('register.html')

@app.route('/debug') # Remove this later
def debug():
    return render_template("debug.html", foods=db.session.query(Food).all())

if __name__ == '__main__':
    init_db()
    app.run()
    foodscraper.run()