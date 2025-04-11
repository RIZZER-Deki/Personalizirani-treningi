from tinydb import TinyDB, Query

db = TinyDB('users.json')
User = Query()

def add_user(username, password):
    # Preveri, če uporabnik že obstaja
    if db.search(User.username == username):
        return False  # uporabnik že obstaja
    db.insert({'username': username, 'password': password})
    return True

def check_user(username, password):
    user = db.search((User.username == username) & (User.password == password))
    if user:
        return {'username': username, 'type': 'user'}
    return None
