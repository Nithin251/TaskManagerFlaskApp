from flask import Blueprint,jsonify

global_routes = Blueprint('routes',__name__)

@global_routes.route('/') #GET http://127.0.0.1:5000/
def home():
    return jsonify({"message" : "Welcome to the Task Manager API"}),250
