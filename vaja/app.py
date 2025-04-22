from flask import Flask, request, jsonify, render_template, redirect, session
from database import check_user, add_user

app = Flask(__name__)
app.secret_key = 'skrivna_ključavnica_123'

@app.route('/')
def homepage():
    if 'username' in session:
        return redirect('/dashboard')
    return render_template('homepage.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect('/')
    return render_template('home.html', username=session['username'], jelogiran=True)


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
    
@app.route('/profile/delete', methods=['POST'])
def delete_account():
    if 'username' not in session:
        return redirect('/')
    
    User = Query()
    db.remove(User.username == session['username'])
    session.clear()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
