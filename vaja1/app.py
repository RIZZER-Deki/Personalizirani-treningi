from flask import Flask, request, jsonify, render_template, redirect, session
from database import (
    check_user, add_user,
    add_workout, get_user_workouts,
    get_workout_by_id, update_workout, delete_workout, workouts_table
)
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = 'skrivna_ključavnica_123'
db = TinyDB('db.json')            
workouts_table = db.table('workouts')

@app.route('/')
def homepage():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('homepage.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    
    user_workouts = db.search(Query().user == session['username'])
    stats = {
        'total_workouts': len(user_workouts)
    }

    return render_template('home.html', username=session['username'], jelogiran=True, stats=stats)


@app.route('/')
def home():
    username = session.get('username', '')
    if username == '':
        return redirect('/login')
    return render_template('home.html', username=username, jelogiran=True)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect('/')
    
    return render_template(
        'profile.html',
        username=session['username'],
        userType=session.get('userType', 'navaden')
    )

@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return redirect('/')
    #Najprej zakodira geslo v bajte z .encode(), ker sha256 potrebuje bajtne podatke.

    #Nato uporabi SHA-256 kriptografsko zgoščevalno funkcijo za zaščito gesla.

    #hexdigest() pretvori rezultat v berljivo heksadecimalno obliko.

    #Rezultat: hashed_pw vsebuje zakodirano (zgoščeno) različico gesla.

    new_password = request.form['new_password']
    hashed_pw = sha256(new_password.encode()).hexdigest()
    
    User = Query()
    db.update({'password': hashed_pw}, User.username == session['username'])

    return redirect('/profile')

@app.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect('/')
    
    User = Query()
    db.remove(User.username == session['username'])
    session.clear()

    return redirect('/')


@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = check_user(username, password)
    if user:
        session['username'] = username
        session['userType'] = user['type']
        return jsonify({'prijavaUspela': True})
    else:
        return jsonify({'prijavaUspela': False, 'error': 'Napačno uporabniško ime ali geslo'})
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if len(username) < 3 or len(password) < 4:
            return 'Uporabniško ime in geslo morata imeti dovolj znakov.', 400

        success = add_user(username, password)
        if success:
            return redirect('/login')
        else:
            return 'Uporabniško ime že obstaja!', 400

    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'odjavaUspela': True})

@app.route("/workouts")
def workouts():
    if 'username' not in session:
        return redirect("/login")
    workouts = db.all()
    return render_template("workouts.html", workouts=workouts, jelogiran=True)

@app.route("/workouts/new", methods=["GET", "POST"])
def add_workout():
    if 'username' not in session:
        return redirect("/login")
    
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        if title.strip() == "":
            return "Napaka: Naslov ne sme biti prazen.", 400

        db.insert({"title": title, "description": description, "user": session["username"]})
        return redirect("/workouts")

    return render_template("add_workout.html", jelogiran=True)


@app.route('/workouts/new', methods=['GET', 'POST'])
def new_workout():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        add_workout(session['username'], title, description)
        return redirect('/workouts')

    return render_template('new_workout.html')

@app.route('/workouts/edit/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    if 'username' not in session:
        return redirect('/login')

    workout = get_workout_by_id(workout_id)
    if not workout or workout['username'] != session['username']:
        return 'Ni dostopa', 403

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        update_workout(workout_id, title, description)
        return redirect('/workouts')

    return render_template('edit_workout.html', workout=workout, workout_id=workout_id)

@app.route('/workouts/delete/<int:workout_id>', methods=['POST'])
def delete_workout_route(workout_id):
    if 'username' not in session:
        return redirect('/login')

    workout = get_workout_by_id(workout_id)
    if workout and workout['username'] == session['username']:
        delete_workout(workout_id)
        return redirect('/workouts')

    return 'Ni dostopa', 403

@app.route('/api/workouts/delete/<int:workout_id>', methods=['POST'])
def api_delete_workout(workout_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 403

    workout = get_workout_by_id(workout_id)
    if workout and workout['username'] == session['username']:
        delete_workout(workout_id)
        return jsonify({'success': True})

    return jsonify({'success': False, 'message': 'Unauthorized'}), 403


if __name__ == '__main__':
    app.run(debug=True)