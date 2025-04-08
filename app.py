from flask import Flask, request, jsonify, render_template, redirect, session
from database import check_user

app = Flask(__name__)
app.secret_key = 'skrivna_ključavnica_123'

@app.route('/')
def home():
    username = session.get('username', '')
    if username == '':
        return redirect('/login')
    return render_template('home.html', username=username, jelogiran=True)

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
    
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'odjavaUspela': True})

if __name__ == '__main__':
    app.run(debug=True)
