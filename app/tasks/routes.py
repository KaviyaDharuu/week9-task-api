from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.extensions import db, limiter
from app.models import Task, User, Comment
from app.utils.responses import success_response, error_response, paginated_response
from app.utils.validators import validate_task_data

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks with filtering, sorting, and pagination"""
    current_user_id = get_jwt_identity()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', type=str)
    priority = request.args.get('priority', type=str)
    category = request.args.get('category', type=str)
    sort_by = request.args.get('sort_by', 'created_at', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)
    search = request.args.get('search', type=str)
    
    # Validate pagination
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 10
    
    # Build query
    query = Task.query.filter_by(owner_id=current_user_id)
    
    # Apply filters
    if status and status in ['pending', 'in_progress', 'completed', 'cancelled']:
        query = query.filter_by(status=status)
    
    if priority and priority in ['low', 'medium', 'high']:
        query = query.filter_by(priority=priority)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Task.title.ilike(search_term)) |
            (Task.description.ilike(search_term))
        )
    
    # Get total count before pagination
    total_items = query.count()
    
    # Apply sorting
    if sort_by == 'due_date':
        sort_column = Task.due_date
    elif sort_by == 'priority':
        sort_column = Task.priority
    elif sort_by == 'status':
        sort_column = Task.status
    else:
        sort_column = Task.created_at
    
    if sort_order == 'asc':
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Apply pagination
    tasks = query.offset((page - 1) * per_page).limit(per_page).all()
    
    tasks_data = [task.to_dict() for task in tasks]
    
    return paginated_response(
        tasks_data,
        page=page,
        per_page=per_page,
        total_items=total_items
    )

@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a single task by ID"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    if task.owner_id != current_user_id and current_user_id not in [u.id for u in task.assignees]:
        return error_response('Not authorized to view this task', status_code=403)
    
    return success_response({'task': task.to_dict(include_comments=True)}, status_code=200)

@tasks_bp.route('', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def create_task():
    """Create a new task"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return error_response('Request body is empty', status_code=400)
    
    # Validate data
    errors = validate_task_data(data)
    
    if errors:
        return error_response('Validation failed', errors=errors, status_code=400)
    
    try:
        task = Task(
            title=data.get('title'),
            description=data.get('description'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            category=data.get('category'),
            due_date=data.get('due_date'),
            owner_id=current_user_id
        )
        
        db.session.add(task)
        db.session.commit()
        
        response_data = {
            'message': 'Task created successfully',
            'task': task.to_dict()
        }
        return success_response(response_data, status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to create task', status_code=500)

@tasks_bp.route('/<int:task_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return error_response('Request body is empty', status_code=400)
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    if task.owner_id != current_user_id:
        return error_response('Not authorized to update this task', status_code=403)
    
    # Validate data
    errors = validate_task_data(data)
    
    if errors:
        return error_response('Validation failed', errors=errors, status_code=400)
    
    try:
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'priority' in data:
            task.priority = data['priority']
        if 'category' in data:
            task.category = data['category']
        if 'due_date' in data:
            task.due_date = data['due_date']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        response_data = {
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }
        return success_response(response_data, status_code=200)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to update task', status_code=500)

@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    if task.owner_id != current_user_id:
        return error_response('Not authorized to delete this task', status_code=403)
    
    try:
        db.session.delete(task)
        db.session.commit()
        
        response_data = {'message': 'Task deleted successfully'}
        return success_response(response_data, status_code=200)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to delete task', status_code=500)

@tasks_bp.route('/<int:task_id>/assign', methods=['POST'])
@jwt_required()
def assign_task(task_id):
    """Assign task to users"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'user_ids' not in data:
        return error_response('user_ids is required', status_code=400)
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    if task.owner_id != current_user_id:
        return error_response('Not authorized to assign this task', status_code=403)
    
    try:
        user_ids = data.get('user_ids', [])
        
        for user_id in user_ids:
            user = User.query.get(user_id)
            if user and user not in task.assignees:
                task.assignees.append(user)
        
        db.session.commit()
        
        response_data = {
            'message': 'Task assigned successfully',
            'task': task.to_dict()
        }
        return success_response(response_data, status_code=200)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to assign task', status_code=500)

@tasks_bp.route('/<int:task_id>/comments', methods=['POST'])
@jwt_required()
def add_comment(task_id):
    """Add a comment to a task"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'content' not in data:
        return error_response('content is required', status_code=400)
    
    content = data.get('content', '').strip()
    
    if not content or len(content) > 1000:
        return error_response('Comment must be between 1-1000 characters', status_code=400)
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    if task.owner_id != current_user_id and current_user_id not in [u.id for u in task.assignees]:
        return error_response('Not authorized to comment on this task', status_code=403)
    
    try:
        comment = Comment(
            content=content,
            task_id=task_id,
            author_id=current_user_id
        )
        
        db.session.add(comment)
        db.session.commit()
        
        response_data = {
            'message': 'Comment added successfully',
            'comment': comment.to_dict()
        }
        return success_response(response_data, status_code=201)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to add comment', status_code=500)

@tasks_bp.route('/<int:task_id>/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(task_id, comment_id):
    """Delete a comment"""
    current_user_id = get_jwt_identity()
    
    task = Task.query.get(task_id)
    
    if not task:
        return error_response('Task not found', status_code=404)
    
    comment = Comment.query.get(comment_id)
    
    if not comment or comment.task_id != task_id:
        return error_response('Comment not found', status_code=404)
    
    if comment.author_id != current_user_id:
        return error_response('Not authorized to delete this comment', status_code=403)
    
    try:
        db.session.delete(comment)
        db.session.commit()
        
        response_data = {'message': 'Comment deleted successfully'}
        return success_response(response_data, status_code=200)
    
    except Exception as e:
        db.session.rollback()
        return error_response('Failed to delete comment', status_code=500)
