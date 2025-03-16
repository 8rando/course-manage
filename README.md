# Course Management System

A comprehensive API for managing educational courses, with support for students, lecturers, and administrators.

## Project Overview

This system provides a REST API that allows:
- User management (students, lecturers, administrators)
- Course creation and enrollment
- Discussion forums and threads
- Course content management
- Assignment submission and grading
- Calendar events
- Comprehensive reporting

## Prerequisites

- Python 3.9+ 
- MySQL 8.0+
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd course-manage
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Database Setup

1. Ensure MySQL is running on your system

2. Create a database and user:
   ```sql
   CREATE DATABASE course_management;
   CREATE USER 'courseadmin'@'localhost' IDENTIFIED BY '1234';
   GRANT ALL PRIVILEGES ON course_management.* TO 'courseadmin'@'localhost';
   FLUSH PRIVILEGES;
   ```

3. Initialize the database schema:
   ```bash
   mysql -u courseadmin -p course_management < creation_fileactual.sql
   ```

4. Generate sample data (optional but recommended):
   ```bash
   python generatedata.py
   ```
   Note: You can adjust the sample data size in generatedata.py by modifying the constants at the top of the file.

## Environment Configuration

Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=courseadmin
DB_PASSWORD=1234
DB_DATABASE=course_management
```

## Running the Application

Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:8080`

## API Endpoints

### User Management
- `POST /api/register` - Register a new user (student, lecturer, admin)
- `POST /api/login` - Login with credentials
- `GET /api/user/<id>` - Get user information

### Course Management
- `POST /api/courses` - Create a course (admin only)
- `GET /api/courses` - Get all courses or courses for a specific user
- `POST /api/enroll` - Enroll a student in a course
- `POST /api/assign_lecturer` - Assign a lecturer to a course
- `GET /api/course/<id>/members` - Get members of a course

### Course Content
- `POST /api/content` - Add course content (documents, links, slides)
- `GET /api/content?course_id=<id>` - Get content for a specific course

### Discussions
- `GET /api/forums?course_id=<id>` - Get forums for a course
- `POST /api/forums` - Create a forum for a course
- `GET /api/threads?forum_id=<id>` - Get threads in a forum
- `POST /api/threads/reply` - Reply to a thread

### Assignments
- `POST /api/assignments` - Create an assignment
- `GET /api/assignments?course_id=<id>` - Get assignments for a course
- `POST /api/submit_assignment` - Submit an assignment
- `POST /api/grade_assignment` - Grade a submission

### Calendar
- `GET /api/calendar_events` - Get events for a course or student
- `POST /api/calendar_events` - Create a calendar event

### Reports
- `GET /api/views/courses_with_50_or_more_students` - Courses with 50+ students
- `GET /api/views/students_with_5_or_more_courses` - Students with 5+ courses
- `GET /api/views/lecturers_with_3_or_more_courses` - Lecturers with 3+ courses
- `GET /api/views/top_10_students_with_highest_average` - Top students by grades
- `GET /api/views/top_10_most_enrolled_courses` - Most popular courses

## Troubleshooting

- **Database Connection Issues**: Verify MySQL is running and credentials are correct in your .env file
- **Empty Tables**: Run `generatedata.py` to populate the database with sample data
- **API Errors**: Check the Flask server console for detailed error messages

## License

This project is educational and open-source.
