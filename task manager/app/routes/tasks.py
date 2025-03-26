from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Task

task_routes = Blueprint('tasks', __name__, url_prefix='/tasks')

@task_routes.route('/')
def get_tasks():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    status_filter = request.args.get('status', type=str)

    # Define the base query before any filtering
    query = Task.query  

    # Apply status filter if provided
    if status_filter in ['pending', 'completed']:
        query = query.filter(Task.status == status_filter)

    # Paginate the results
    tasks = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "tasks": [{
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "status": t.status,
            "user_id": t.user_id
        } for t in tasks.items],  # Use `.items` to get the actual list of tasks
        "total": tasks.total,
        "pages": tasks.pages,
        "current_page": tasks.page
    })

@task_routes.route("/<int:task_id>")
def get_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error' : "Task not found"}),404
    
    return jsonify({"id" : task.id,
                    "title" : task.title,
                    "description" : task.description,
                    "status" : task.status,
                    "user_id" : task.user_id})

@task_routes.route("/",methods=['POST'])
@login_required
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    user_id = data.get('user_id')

    if not title or not description or not user_id:
        return jsonify({'error' : "Title,description and user_id are required"}),400
    
    new_task = Task(title=title,description=description,status='pending',user_id=user_id)

    db.session.add(new_task)
    db.session.commit()

    return jsonify({ 'message' : "Task created successfully",
                    'task' : [{
                    "id" : new_task.id,
                    "title" : new_task.title,
                    "description" : new_task.description,
                    "status" : new_task.status,
                    'user_id' : new_task.user_id}]}), 201

@task_routes.route("/<int:task_id>",methods=['PUT'])
@login_required
def update_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error' : "Task not found"}),404

    data = request.get_json()
    task.title = data.get('title',task.title)
    task.description = data.get('description',task.description)
    new_status = data.get('status')

    if new_status:
        try:
            task.set_status(new_status)
        except ValueError:
            return jsonify({'error' : "Invalid status"}),400
  
    db.session.commit()

    return jsonify({ 'message' : "Task updated successfully",
                    'task' : [{
                    "id" : task.id,
                    "title" : task.title,
                    "description" : task.description,
                    "status" : task.status,
                    'user_id' : task.user_id}]}), 200

@task_routes.route("/<int:task_id>",methods=['DELETE'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error' : "Task not found"}),404
    
    db.session.delete(task)
    db.session.commit()

    return jsonify({'message' : "Task deleted successfully"})
