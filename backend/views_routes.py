from flask import jsonify, Blueprint
from config import execute_query

views_bp = Blueprint("views", __name__)

@views_bp.route('/api/views/courses_with_50_or_more_students', methods=['GET'])
def get_courses_with_50_or_more_students():
    try:
        results = execute_query("SELECT * FROM CoursesWith50OrMoreStudents")
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@views_bp.route('/api/views/students_with_5_or_more_courses', methods=['GET'])
def get_students_with_5_or_more_courses():
    try:
        results = execute_query("SELECT * FROM StudentsWith5OrMoreCourses")
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@views_bp.route('/api/views/lecturers_with_3_or_more_courses', methods=['GET'])
def get_lecturers_with_3_or_more_courses():
    try:
        results = execute_query("SELECT * FROM LecturersWith3OrMoreCourses")
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@views_bp.route('/api/views/top_10_students_with_highest_average', methods=['GET'])
def get_top_10_students_with_highest_average():
    try:
        results = execute_query("SELECT * FROM Top10StudentsWithHighestAverages")
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@views_bp.route('/api/views/top_10_most_enrolled_courses', methods=['GET'])
def get_top_10_most_enrolled_courses():
    try:
        results = execute_query("SELECT * FROM Top10MostEnrolledCourses")
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
