from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash

db = TinyDB('db.json')
User = Query()

users_table = db.table('users')
workouts_table = db.table('workouts')


def add_user(username, password):
    if db.search(User.username == username):
        return False  
    hashed_password = generate_password_hash(password)
    users_table.insert({'username': username, 'password': hashed_password})

    return True

def check_user(username, password):
    user = users_table.search(User.username == username)
    if user and check_password_hash(user[0]['password'], password):
        return {'username': username, 'type': 'user'}
    return None

def add_workout(username, title, description):
    workouts_table.insert({
        'user': username,
        'title': title,
        'description': description
    })

def get_user_workouts(username):
    return workouts_table.search(Query().user == username)

def get_workout_by_id(workout_id):
    return workouts_table.get(doc_id=workout_id)

def update_workout(workout_id, title, description):
    workouts_table.update({
        'title': title,
        'description': description
    }, doc_ids=[workout_id])

def delete_workout(workout_id):
    workouts_table.remove(doc_ids=[workout_id])
