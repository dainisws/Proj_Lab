from flask import Flask, redirect, url_for, jsonify, session, Response, request, send_file
from models import Input, FoodRimi, FoodBarbora, FoodRatingBarbora, FoodRatingRimi, User
from models import init_db
from foodscraper import FoodScraper
import os
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash # pip install Werkzeug
from solver import SolverModel
from sqlalchemy import case
import time

app = Flask(__name__)


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
with open("key.txt", "r") as file:
    app.secret_key = file.read() # Šo būtu jānomaina, ja publicē

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.db"))
db = SQLAlchemy(app)
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

result_data = {}
optimal_result_data = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

foodscraper = FoodScraper(db, app)

@app.route('/')
def home():
    return render_template('index.html', username=session.get('user_id', None))

@app.route('/generator')
def generator():
    if session.get('user_id', None) is None:
        return redirect(url_for('signup'))
    else:
        return render_template('MenuGen.html', username=session.get('user_id', None))
    
@app.route('/getbarborafoods', methods=['GET'])
def getbarborafoods():
    items = db.session.query(FoodBarbora.id, FoodBarbora.name).all()
    items_list = [{"id": item.id, "name": item.name} for item in items]
    return jsonify(items_list)
@app.route('/getrimifoods', methods=['GET'])
def getrimifoods():
    items = db.session.query(FoodRimi.id, FoodRimi.name).all()
    items_list = [{"id": item.id, "name": item.name} for item in items]
    return jsonify(items_list)
@app.route('/getbarboragroups', methods=['GET'])
def getbarboragroups():
    items = db.session.query(FoodBarbora.last_category).distinct().all()
    items_list = [{"name": item.last_category} for item in items]
    return jsonify(items_list)
@app.route('/getrimigroups', methods=['GET'])
def getrimigroups():
    items = db.session.query(FoodRimi.last_category).distinct().all()
    items_list = [{"name": item.last_category} for item in items]
    return jsonify(items_list)
@app.route('/getbarboraratings', methods=['GET'])
def getbarboraratings():
    if session.get('user_id', None) is None:
        return "No session found", 400
    items = db.session.query(FoodRatingBarbora.food_id, FoodRatingBarbora.rating).join(User, User.id == FoodRatingBarbora.user_id).filter(User.username == session.get('user_id', None)).all()
    items_list = [{"id": item.food_id, "rating": item.rating} for item in items]
    return jsonify(items_list)
@app.route('/getrimiratings', methods=['GET'])
def getrimiratings():
    if session.get('user_id', None) is None:
        return "No session found", 400
    items = db.session.query(FoodRatingRimi.food_id, FoodRatingRimi.rating).join(User, User.id == FoodRatingRimi.user_id).filter(User.username == session.get('user_id', None)).all()
    items_list = [{"id": item.food_id, "rating": item.rating} for item in items]
    return jsonify(items_list)

@app.route('/documentation')
def documentation():
    return render_template('doc.html', username=session.get('user_id', None))

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    if session.get('user_id', None) is None:
        return render_template('register.html', username=session.get('user_id', None))
    if request.method == 'POST':
        if session.get('cartItems', None) != None:
            removed_items = [item for item in session.get('cartItems', []) if item['id'] == request.json]
            for item in removed_items:
                session['totalPrice'] = session.get('totalPrice', 0) - float(item['0'])
                session['totalCalories'] = session.get('totalCalories', 0) - float(item['2'])
                session['totalFat'] = session.get('totalFat', 0) - float(item['3'])
                session['totalProtein'] = session.get('totalProtein', 0) - float(item['4'])
                session['totalCarbs'] = session.get('totalCarbs', 0) - float(item['5'])
            session['cartItems'] = [item for item in session.get('cartItems', []) if item['id'] != request.json]
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 400
    cartItems = session.get('cartItems', [])
    rounded_items = [
    {
        key: round(value, 1) if isinstance(value, (int, float)) else value
        for key, value in item.items()
    }
    for item in cartItems
]
    return render_template('cart.html', username=session.get('user_id', None), 
                            items=rounded_items, 
                            calories = max(0, round(session.get('totalCalories', 0.0), 2)), 
                            fat = max(0, round(session.get('totalFat', 0.0), 2)), 
                            protein = max(0, round(session.get('totalProtein', 0.0), 2)), 
                            carbs = max(0, round(session.get('totalCarbs', 0.0), 2)), 
                            price = max(0, round(session.get('totalPrice', 0.0), 2)))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if session.get('user_id', None) is None:
        return redirect(url_for('home'))
    if request.method == 'POST':
        if 'image' not in request.files:
            return "Something went wrong...", 400
        
        file = request.files['image']
        
        if file.filename == '':
            return "Something went wrong...", 400
        
        if file and allowed_file(file.filename):
            user = db.session.query(User).filter_by(username=session.get('user_id', None)).first()
            user.profile_picture = file.read()
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            return "Picture must be JPG/JPEG", 400
    return render_template('profile.html', username=session.get('user_id', None))

@app.route('/profilepicture')
def get_image():
    default_image_path = os.path.join('static/images', 'pfp.jpg')
    try:
        image = db.session.query(User.profile_picture).filter_by(username=session.get('user_id', None)).first()
        if not image:
            return send_file(default_image_path, mimetype='image/jpeg')
        else:    
            return Response(image, mimetype='image/jpeg')
    except:
        return send_file(default_image_path, mimetype='image/jpeg')
    
@app.route('/signup')
def signup():
    if session.get('user_id', None) is None:
        return render_template('register.html', username=session.get('user_id', None))
    else:
        return redirect(url_for('profile'))

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
    if session.get('user_id', None) is not None:
        session.pop('user_id', None)
    if session.get('cartItems', None) is not None:
        session.pop('cartItems', None)
    if session.get('inputdata', None) is not None:
        session.pop('inputdata', None)
    if session.get('totalCalories', None) is not None:
        session.pop('totalCalories', None)
    if session.get('totalFat', None) is not None:
        session.pop('totalFat', None)
    if session.get('totalProtein', None) is not None:
        session.pop('totalProtein', None)
    if session.get('totalPrice', None) is not None:
        session.pop('totalPrice', None)
    return redirect(url_for('home'))

@app.route('/deleteprofile')
def deleteProfile():
    if session.get('user_id', None) is not None:
        try:
            db.session.delete(db.session.query(User).filter_by(username=session.get('user_id', None)).first())
            db.session.commit() 
            session.pop('user_id', None)
        except Exception as e: print(e)
 
    return redirect(url_for('home'))

@app.route('/compute', methods=['GET', 'POST'])
def compute():
    if session.get('user_id', None) is None:
        return render_template('register.html', username=session.get('user_id', None))
    data = session.get('inputdata', None)
    if request.method == 'POST':
        #try:
        data = request.get_json()
        if data.get('computeType') == "init":
            session['inputdata'] = data
            session['totalPrice'] = 0.0
            session['totalCalories'] = 0.0
            session['totalFat'] = 0.0
            session['totalProtein'] = 0.0
            session['totalCarbs'] = 0.0
            session['cartItems'] = []
        else: #add to cart link calories protein fat carbs amount
            session['totalPrice'] = session.get('totalPrice', 0) + float(data.get('item')['0']) * float(data.get('item')['8'])
            session['totalCalories'] = session.get('totalCalories', 0) + float(data.get('item')['2']) * float(data.get('item')['8'])
            session['totalFat'] = session.get('totalFat', 0) + float(data.get('item')['3']) * float(data.get('item')['8'])
            session['totalProtein'] = session.get('totalProtein', 0) + float(data.get('item')['4']) * float(data.get('item')['8'])
            session['totalCarbs'] = session.get('totalCarbs', 0) + float(data.get('item')['5']) * float(data.get('item')['8'])
            if 'cartItems' not in session:
                session['cartItems'] = []
            dat = data.get('item')
            dat['0'] = float(data.get('item')['0']) * float(data.get('item')['8'])
            dat['2'] = float(data.get('item')['2']) * float(data.get('item')['8'])
            dat['3'] = float(data.get('item')['3']) * float(data.get('item')['8'])
            dat['4'] = float(data.get('item')['4']) * float(data.get('item')['8'])
            dat['5'] = float(data.get('item')['5']) * float(data.get('item')['8'])
            dat['id'] = len(session['cartItems'])
            session['cartItems'].append(dat)
            data = session['inputdata']
        return jsonify({'success': True}), 200

    if data != None:
        a1 = float(data.get('minCalories'))
        a2 = float(data.get('maxCalories'))
        a3 = float(data.get('minFat'))
        a4 = float(data.get('maxFat'))
        a5 = float(data.get('minProtein'))
        a6 = float(data.get('maxProtein'))
        a7 = float(data.get('minCarbs'))
        a8 = float(data.get('maxCarbs'))
        a9 = float(data.get('weightTaste'))
        a10 = float(data.get('weightPrice'))
        store = data.get('store')
        
        uid = db.session.query(User.id).filter_by(username=session.get('user_id',None)).first()[0]

        # updating food ratings
        if store == "Rimi":
            food_groups_with_ratings = data.get('foodGroupsWithRatings', [])
            for item in food_groups_with_ratings:
                group_name = item.get('name')
                rating = item.get('rating')
                if rating != None:
                    foods = db.session.query(FoodRimi.id).filter_by(last_category=group_name).all()
                    for food in foods:
                        foodRating = db.session.query(FoodRatingRimi).filter(FoodRatingRimi.food_id==food[0], FoodRatingRimi.user_id==uid).first()
                        if foodRating != None:
                            foodRating.rating = rating
                        else:
                            food2 = FoodRatingRimi(uid, food[0], rating)
                            db.session.add(food2)
            db.session.commit()
            foods_with_ratings = data.get('foodsWithRatings', [])
            for item in foods_with_ratings:
                id = item.get('id')
                rating = item.get('rating')
                if rating != None:
                    foodRating = db.session.query(FoodRatingRimi).filter(FoodRatingRimi.food_id==id, FoodRatingRimi.user_id==uid).first()
                    if foodRating != None:
                        foodRating.rating = rating
                    else:
                        food = FoodRatingRimi(uid, id, rating)
                        db.session.add(food)
            db.session.commit()
        else:
            food_groups_with_ratings = data.get('foodGroupsWithRatings', [])
            for item in food_groups_with_ratings:
                group_name = item.get('name')
                rating = item.get('rating')
                foods = db.session.query(FoodBarbora.id).filter_by(last_category=group_name).all()
                if rating != None:
                    for food in foods:
                        foodRating = db.session.query(FoodRatingBarbora).filter(FoodRatingBarbora.food_id==food[0], FoodRatingBarbora.user_id==uid).first()
                        if foodRating != None:
                            foodRating.rating = rating
                        else:
                            food2 = FoodRatingBarbora(uid, food[0], rating)
                            db.session.add(food2)
            db.session.commit()
            foods_with_ratings = data.get('foodsWithRatings', [])
            for item in foods_with_ratings:
                id = item.get('id')
                rating = item.get('rating')
                if rating != None:
                    foodRating = db.session.query(FoodRatingBarbora).filter(FoodRatingBarbora.food_id==id, FoodRatingBarbora.user_id==uid).first()
                    if foodRating != None:
                        foodRating.rating = rating
                    else:
                        food = FoodRatingBarbora(uid, id, rating)
                        db.session.add(food)
            db.session.commit()
        
        # solver
        results = "N/A"
        if store == "Rimi":
            arr = db.session.query(
                FoodRimi.id,
                FoodRimi.pricePerKg,
                case(
                    (FoodRatingRimi.food_id == FoodRimi.id, FoodRatingRimi.rating),  # condition and result as a positional argument
                    else_=5
                ).label("rating"),
                FoodRimi.calories,
                FoodRimi.fat,
                FoodRimi.protein,
                FoodRimi.carbs,
                FoodRimi.name,
                FoodRimi.link
            ).outerjoin(
                FoodRatingRimi, 
                (FoodRimi.id == FoodRatingRimi.food_id) & (FoodRatingRimi.user_id == uid)
            ).all()
        else:
            arr = db.session.query(
                FoodBarbora.id,
                FoodBarbora.pricePerKg,
                case(
                    (FoodRatingBarbora.food_id == FoodBarbora.id, FoodRatingBarbora.rating),  # condition and result as a positional argument
                    else_=5
                ).label("rating"),
                FoodBarbora.calories,
                FoodBarbora.fat,
                FoodBarbora.protein,
                FoodBarbora.carbs,
                FoodBarbora.name,
                FoodBarbora.link
            ).outerjoin(
                FoodRatingBarbora, 
                (FoodBarbora.id == FoodRatingBarbora.food_id) & (FoodRatingBarbora.user_id == uid)
            ).all()
        arr = [
            item for item in arr 
            if all(value is not None for value in item)
        ]

        cart_links = [item['7'] for item in session.get('cartItems', [])]
        filtered_arr = [record for record in arr if record[8] not in cart_links]
        results = SolverModel(a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, filtered_arr, session['totalCalories'], session['totalFat'], session['totalProtein'], session['totalCarbs']).solve()
        resultsOptimal = results[results[:, -1].astype(float) > 0.05]

        global result_data, optimal_result_data
        result_data[session['user_id']] = results.tolist()
        optimal_result_data[session['user_id']] = resultsOptimal.tolist()
        #except:
        #    return jsonify({'success': False}), 400
    return render_template('results.html', username=session.get('user_id', None), 
                            results=result_data.get(session['user_id'], None), 
                            resultsOptimal=optimal_result_data.get(session['user_id'], None), 
                            calories = max(0, round(session.get('totalCalories', 0.0), 2)), 
                            fat = max(0, round(session.get('totalFat', 0.0), 2)), 
                            protein = max(0, round(session.get('totalProtein', 0.0), 2)), 
                            carbs = max(0, round(session.get('totalCarbs', 0.0), 2)), 
                            price = max(0, round(session.get('totalPrice', 0.0), 2)))

@app.route('/debug') # Remove this later
def debug():
    return render_template("debug.html", foods=db.session.query(FoodBarbora).all())

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
    foodscraper.run()