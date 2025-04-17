from click import password_option
from flask import Flask, request, jsonify, Blueprint
from config import get_db_connection


views_bp = Blueprint("views", __name__)

@views_bp.route('/api/views/courses_with_50_or_more_students', methods=['GET'])
def get_courses_with_50_or_more_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM courseswith50ormorestudents")
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/api/views/students_with_5_or_more_courses', methods=['GET'])
def get_students_with_5_or_more_courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM studentswith5ormorecourses")
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


@views_bp.route('/api/views/lecturers_with_3_or_more_courses', methods=['GET'])
def get_lecturers_with_3_or_more_courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM lecturerswith3ormorecourses")
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/api/views/top_10_students_with_highest_average', methods=['GET'])
def get_top_10_students_with_highest_average():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM top10studentswithhighestaverages")
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@views_bp.route('/api/views/top_10_most_enrolled_courses', methods=['GET'])
def get_top_10_most_enrolled_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM top10mostenrolledcourses")
        results = cursor.fetchall()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#
# if __name__ == "__main__":
#     app.run(port=8080, debug=True)