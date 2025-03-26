from flask import Blueprint,request,jsonify,session,url_for
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, login_manager
from app.models import User
user_routes = Blueprint('users',__name__,url_prefix='/users')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@user_routes.route('/signup', methods=['POST']) # POST http://127.0.0.1:5000/users/signup <username,password>
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error' : 'Username and password are required'}),400
    
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error' : 'User already exists'}),409
    
    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message' : 'User created successfully'}),201

    
@user_routes.route('/login', methods=['POST']) # POST http://127.0.0.1:5000/users/login <username,password>
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({'error' : 'Invalid username or password'}),401
    
    login_user(user)

    return jsonify({'message' : f'Welcome {user.username}'}),200

@user_routes.route('/logout') #GET http://127.0.0.1:5000/users/logout <no data>
def logout():
    logout_user()
    return jsonify({'message' : 'Logged out successfully'}),200
    
@user_routes.route('/') #GET http://127.0.0.1:5000/users <no data>
@login_required
def list_users():
    page = request.args.get('page',1,type=int)
    per_page = 5

    users = User.query.paginate(page=page,per_page=per_page,error_out=False)

    return jsonify({
        "users" : [{"id" : u.id, "username" : u.username} 
                   for u in users.items]
    })
