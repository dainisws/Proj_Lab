from flask import Flask, redirect, url_for, jsonify, session, request
from models import Input, FoodRimi, FoodBarbora, User
from models import init_db
from foodscraper import FoodScraper
import os
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash # pip install Werkzeug

app = Flask(__name__)
app.secret_key = "JAmNqo4kiM3Xv3cEzHv5fUWZ0INE33GD"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"))
db = SQLAlchemy(app)

foodscraper = FoodScraper(db, app)

@app.route('/')
def home():
    return render_template('index.html', username=session.get('user_id', None))

@app.route('/generator')
def generator():
    return render_template('MenuGen.html', username=session.get('user_id', None))

@app.route('/results', methods=['POST'])
def results():
    min_carbs = float(request.args.get('min_carbs')) # example
    input = Input() # should put arguments here
    return 'Generator Results'

@app.route('/documentation')
def documentation():
    return render_template('doc.html', username=session.get('user_id', None))

@app.route('/legal')
def legal():
    return render_template('legal.html', username=session.get('user_id', None))

@app.route('/cart')
def cart():
    return 'Shopping Cart'

@app.route('/profile')
def profile():
    return render_template('profile.html', username=session.get('user_id', None))

@app.route('/signup')
def signup():
    return render_template('register.html')

# Route: Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        

        if not username or not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        usernameExists = db.session.query(db.exists().where(User.username == username)).scalar()
        emailExists = db.session.query(db.exists().where(User.email == email)).scalar()
        if usernameExists or emailExists:
            return jsonify({'success': False, 'message': 'E-mail/username already exists'}), 400

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        user = User(username, email, hashed_password, None)
        db.session.add(user)
        db.session.commit()
        return jsonify({'success': True}), 200

    return render_template('register.html', username=session.get('user_id', None))

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        # Verify user
        allowLogin = False
        if (db.session.query(db.exists().where(User.email == email)).scalar()):
            if check_password_hash(db.session.query(User.password).filter_by(email = email).first().password, password):
                allowLogin = True
        if not allowLogin:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401

        session['user_id'] = db.session.query(User.username).filter_by(email = email).first().username
        return jsonify({'success': True}), 200

    return render_template('register.html', username=session.get('user_id', None))

# Route: Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user from session
    return redirect(url_for('home'))

@app.route('/debug') # Remove this later
def debug():
    return render_template("debug.html", foods=db.session.query(FoodBarbora).all())

if __name__ == '__main__':
    init_db()
    app.run()
    foodscraper.run()