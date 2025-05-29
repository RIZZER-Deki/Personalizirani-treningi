from hashlib import sha256
from flask import Flask, request, render_template, redirect, session, url_for
from database import (
    check_user, add_user,
    add_workout, get_user_workouts,
    get_workout_by_id, update_workout, delete_workout
)
from tinydb import TinyDB, Query

app = Flask(__name__)
app.secret_key = 'skrivna_ključavnica_123'
db = TinyDB('db.json')
workouts_table = db.table('workouts')


@app.route('/')
def homepage():
    return render_template('homepage.html', username=session.get('username'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('homepage'))

    user_workouts = workouts_table.search(Query().username == session['username'])
    stats = {'total_workouts': len(user_workouts)}
    return render_template('home.html', username=session['username'], jelogiran=True, stats=stats)


@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('homepage'))

    return render_template('profile.html',
                           username=session['username'],
                           userType=session.get('userType', 'navaden'))


@app.route('/profile/change-password', methods=['POST'])
def change_password():
    if 'username' not in session:
        return redirect(url_for('homepage'))

    new_password = request.form['new_password']
    hashed_pw = sha256(new_password.encode()).hexdigest()
    db.update({'password': hashed_pw}, Query().username == session['username'])
    return redirect(url_for('profile'))


@app.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect(url_for('homepage'))

    db.remove(Query().username == session['username'])
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    user = check_user(username, password)

    if user:
        session['username'] = username
        session['userType'] = user.get('type', 'navaden')
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error='Napačno uporabniško ime ali geslo')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if len(username) < 3 or len(password) < 4:
            return 'Uporabniško ime in geslo morata imeti dovolj znakov.', 400

        if add_user(username, password):  
            return redirect(url_for('login'))
        else:
            return 'Uporabniško ime že obstaja!', 400

    return render_template('signup.html')


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('homepage'))


@app.route('/workouts')
def workouts():
    if 'username' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '').lower()
    all_workouts = workouts_table.search(Query().username == session['username'])

    if search:
        all_workouts = [w for w in all_workouts if search in w['title'].lower()]

    return render_template('workouts.html', workouts=all_workouts, jelogiran=True)


@app.route('/workouts/new', methods=['GET', 'POST'])
def add_workout():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form['description'].strip()
        split = request.form['split']

        if not title:
            return "Napaka: Naslov ne sme biti prazen.", 400

        workouts_table.insert({
            "title": title,
            "description": description,
            "split": split,
            "username": session["username"]
        })
        return redirect(url_for('workouts'))

    return render_template('add_workout.html', jelogiran=True)


@app.route('/workouts/edit/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    workout = workouts_table.get(doc_id=workout_id)

    if not workout or workout['username'] != session['username']:
        return 'Ni dostopa', 403

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        workouts_table.update({'title': title, 'description': description}, doc_ids=[workout_id])
        return redirect(url_for('workouts'))

    return render_template('edit_workout.html', workout=workout)


@app.route('/api/workouts/delete/<int:workout_id>', methods=['POST'])
def delete_workout_api(workout_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    workout = workouts_table.get(doc_id=workout_id)

    if workout and workout['username'] == session['username']:
        workouts_table.remove(doc_ids=[workout_id])
        return redirect(url_for('workouts'))

    return 'Ni dovoljenja', 403


if __name__ == '__main__':
    app.run(debug=True)
