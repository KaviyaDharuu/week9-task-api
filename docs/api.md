# Task Management API - Comprehensive Documentation

## Overview

The Task Management API is a production-ready Flask REST API solution for managing tasks with advanced features. It provides user authentication, full CRUD operations, filtering, pagination, rate limiting, and comprehensive testing.

## Technical Stack

- **Framework**: Flask 2.3.3 with custom blueprints
- **Database**: SQLAlchemy ORM with SQLite/PostgreSQL support
- **Authentication**: JWT (JSON Web Tokens) with refresh tokens
- **Validation**: Input validation and Marshmallow schemas
- **Testing**: Pytest with fixtures and comprehensive coverage
- **Rate Limiting**: Flask-Limiter for API throttling
- **CORS**: Flask-CORS for cross-origin requests

## Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/KaviyaDharuu/week9-task-api.git
cd week9-task-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
cp .env.example .env
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
export JWT_SECRET_KEY=your-jwt-secret-key

# Run application
python run.py
```

API will be available at `http://localhost:5000`

## Authentication Flow

### 1. Register User
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201):
{
  "status": "success",
  "data": {
    "user": {...},
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi..."
  }
}
```

### 2. Login
```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123"
}

Response (200):
{
  "status": "success",
  "data": {
    "user": {...},
    "access_token": "eyJ0eXAi...",
    "refresh_token": "eyJ0eXAi..."
  }
}
```

### 3. Use Access Token
```bash
GET /api/auth/me
Authorization: Bearer eyJ0eXAi...

Response (200):
{
  "status": "success",
  "data": {
    "user": {...}
  }
}
```

### 4. Refresh Token
```bash
POST /api/auth/refresh
Authorization: Bearer eyJ0eXAi... (refresh token)

Response (200):
{
  "status": "success",
  "data": {
    "access_token": "new_token..."
  }
}
```

## Task Management Endpoints

### Create Task
```bash
POST /api/tasks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Complete API project",
  "description": "Finish task management API",
  "priority": "high",
  "category": "development",
  "due_date": "2024-02-15T00:00:00Z"
}

Response (201):
{
  "status": "success",
  "data": {
    "message": "Task created successfully",
    "task": {...}
  }
}
```

### Get All Tasks (with Filtering & Pagination)
```bash
GET /api/tasks?page=1&per_page=10&priority=high&status=pending&sort_by=created_at&sort_order=desc
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "items": [...],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total_pages": 5,
      "total_items": 48,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

### Get Single Task
```bash
GET /api/tasks/{id}
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "task": {...}
  }
}
```

### Update Task
```bash
PUT /api/tasks/{id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated title",
  "status": "in_progress",
  "priority": "medium"
}

Response (200):
{
  "status": "success",
  "data": {
    "message": "Task updated successfully",
    "task": {...}
  }
}
```

### Delete Task
```bash
DELETE /api/tasks/{id}
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "message": "Task deleted successfully"
  }
}
```

### Task Comments

#### Add Comment
```bash
POST /api/tasks/{task_id}/comments
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "content": "This task looks good"
}

Response (201):
{
  "status": "success",
  "data": {
    "message": "Comment added successfully",
    "comment": {...}
  }
}
```

#### Delete Comment
```bash
DELETE /api/tasks/{task_id}/comments/{comment_id}
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "message": "Comment deleted successfully"
  }
}
```

## User Management Endpoints

### Get User Profile
```bash
GET /api/users/{user_id}
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "created_at": "2024-01-25T10:30:00Z"
    }
  }
}
```

### List All Users
```bash
GET /api/users?page=1&per_page=10
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "users": [...],
    "pagination": {...}
  }
}
```

### Update User Profile
```bash
PUT /api/users/{user_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe"
}

Response (200):
{
  "status": "success",
  "data": {
    "message": "User updated successfully",
    "user": {...}
  }
}
```

### Get User Tasks
```bash
GET /api/users/{user_id}/tasks?page=1&per_page=10
Authorization: Bearer {access_token}

Response (200):
{
  "status": "success",
  "data": {
    "tasks": [...],
    "pagination": {...}
  }
}
```

## Query Parameters

### Pagination
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 10, max: 100) - Items per page

### Task Filtering
- `status` - Filter by status (pending, in_progress, completed, cancelled)
- `priority` - Filter by priority (low, medium, high)
- `category` - Filter by category
- `search` - Search in title and description

### Sorting
- `sort_by` - Sort field (created_at, due_date, priority, status)
- `sort_order` - Sort order (asc, desc, default: desc)

## Error Responses

### Validation Error (400)
```json
{
  "status": "error",
  "message": "Validation failed",
  "errors": {
    "title": ["Title is required", "Title must be at least 3 characters"],
    "priority": ["Priority must be one of: low, medium, high"]
  }
}
```

### Unauthorized (401)
```json
{
  "status": "error",
  "message": "Missing or invalid token"
}
```

### Forbidden (403)
```json
{
  "status": "error",
  "message": "Not authorized to perform this action"
}
```

### Not Found (404)
```json
{
  "status": "error",
  "message": "Task not found"
}
```

### Rate Limited (429)
```json
{
  "status": "error",
  "message": "Rate limit exceeded"
}
```

### Server Error (500)
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

## Database Models

### User Model
- `id` - Primary key
- `username` - Unique username (3-80 chars, alphanumeric + underscore)
- `email` - Unique email address
- `password_hash` - Bcrypt hashed password
- `first_name` - User's first name
- `last_name` - User's last name
- `is_active` - Account status
- `created_at` - Registration timestamp
- `updated_at` - Last update timestamp
- **Relationships**: tasks (owned), comments (authored), assigned_tasks

### Task Model
- `id` - Primary key
- `title` - Task title (3-200 chars, required)
- `description` - Task description (max 5000 chars)
- `status` - Status (pending, in_progress, completed, cancelled)
- `priority` - Priority (low, medium, high)
- `category` - Task category
- `due_date` - Due date/time
- `owner_id` - Task owner (Foreign Key to User)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `completed_at` - Completion timestamp
- **Relationships**: owner (User), comments, assignees (many-to-many)

### Comment Model
- `id` - Primary key
- `content` - Comment text (1-1000 chars, required)
- `task_id` - Task reference (Foreign Key to Task)
- `author_id` - Comment author (Foreign Key to User)
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- **Relationships**: task (Task), author (User)

## Validation Rules

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one digit (0-9)

### Username
- 3-80 characters
- Alphanumeric and underscore only
- Must be unique

### Email
- Valid email format
- Must be unique

### Task Title
- Required field
- 3-200 characters
- Must be unique per user

## Rate Limiting

Default limits per IP address:
- **Global**: 200 requests per day, 50 per hour
- **Task Creation**: 10 requests per minute

## Testing

### Run All Tests
```bash
pytest
```

### Run Specific Test Class
```bash
pytest tests/conftest.py::TestAuth
pytest tests/conftest.py::TestTasks
pytest tests/conftest.py::TestUsers
```

### Run with Coverage
```bash
pytest --cov=app --cov-report=html
```

### Test Coverage Report
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

```bash
docker build -t task-api .
docker run -p 8000:8000 -e FLASK_ENV=production task-api
```

## Project Structure

```
week9-task-api/
├── app/                          # Application package
│   ├── __init__.py              # App factory
│   ├── models.py                # Database models
│   ├── extensions.py            # Flask extensions
│   ├── auth/
│   │   ├── __init__.py
│   │   └── routes.py            # Auth endpoints
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── routes.py            # Task endpoints
│   ├── users/
│   │   ├── __init__.py
│   │   └── routes.py            # User endpoints
│   └── utils/
│       ├── __init__.py
│       ├── validators.py        # Input validation
│       └── responses.py         # Response formatting
├── tests/
│   ├── __init__.py
│   └── conftest.py              # Tests & fixtures
├── docs/
│   ├── api.md                   # API documentation
│   ├── swagger.yaml             # OpenAPI spec
│   └── postman_collection.json  # Postman collection
├── config.py                    # Configuration
├── requirements.txt             # Dependencies
├── run.py                       # Entry point
├── README.md                    # Readme
├── .env.example                 # Environment template
└── .gitignore                   # Git ignore
```

## Best Practices

### Security
1. Change default secrets in production
2. Use environment variables for sensitive data
3. Implement HTTPS in production
4. Validate all inputs
5. Use strong passwords
6. Rotate tokens periodically
7. Implement proper CORS policies
8. Use secure headers

### Performance
1. Use pagination for large datasets
2. Add database indexes on frequently queried columns
3. Implement caching for read-heavy operations
4. Use connection pooling for databases
5. Monitor API response times

### API Design
1. Use consistent response format
2. Provide clear error messages
3. Version your API
4. Document all endpoints
5. Use semantic HTTP status codes
6. Implement proper logging

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

MIT License - See LICENSE file for details

## Support & Contact

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: support@example.com

## Version History

### v1.0.0 (Current)
- Initial release
- Complete CRUD operations
- JWT authentication
- Filtering and pagination
- Task commenting
- Comprehensive testing
- Full API documentation

## Acknowledgments

- Flask team for the excellent framework
- SQLAlchemy for ORM
- JWT-Extended for JWT handling
- Pytest for testing framework
- All contributors and users
