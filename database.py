
users = {
    'admin': {'password': 'admin123', 'type': 'admin'},
    'test': {'password': 'test123', 'type': 'user1'},
    'janez': {'password': 'geslo123', 'type': 'user'}
}

def check_user(username, password):
    user = users.get(username)
    if user and user['password'] == password:
        return user  # Vrne dict z uporabniškimi podatki
    return None