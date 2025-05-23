from os import execle

from click import password_option
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from config import get_db_connection
from views_routes import views_bp

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Register the views blueprint
app.register_blueprint(views_bp)


@app.route("/")
def home():
    return jsonify({"message": "Course Management API is running!"})


# =================================== Registers User ===================================

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    fname = data.get('fname')
    lname = data.get('lname')
    password = data.get('password')
    user_type = data.get('user_type')

    if not all([fname,lname,password,user_type]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(str(password)).decode('utf-8')
    conn = get_db_connection()
    cursor = conn.cursor()


    try:
        cursor.execute("INSERT INTO Account (password, type, fname, lname) VALUES(%s, %s, %s, %s)",
                       (hashed_password, user_type, fname,lname))
        conn.commit()
        user_id = cursor.lastrowid

        if user_type == "admin":
            cursor.execute("INSERT INTO Admin (adid) VALUES (%s)", (user_id,))
        elif user_type == "lecturer":
            cursor.execute("INSERT INTO Lecturer (lid) VALUES (%s)", (user_id,))
        elif user_type == "student":
            cursor.execute("INSERT INTO Student (sid) VALUES (%s)", (user_id,))

        conn.commit()
        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== User Login ===================================

@app.route("/api/login", methods=['POST'])
def login():
    data = request.json
    fname = data.get("fname")
    lname = data.get("lname")
    password = data.get("password")

    if not all([fname,lname,password]):
        return jsonify({"error": "Missing credentials"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT aid, password, type FROM Account WHERE fname = %s AND lname = %s", (fname, lname))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # Fix: Access dictionary fields by name instead of position
    if user and bcrypt.check_password_hash(user["password"], password):
        return jsonify({"message": "Login successful", "user_id": user["aid"], "type": user["type"]}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

# =================================== Retrieve User Information ===================================


@app.route("/api/user/<int:user_id>", methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT aid, fname, lname, type, created_at FROM Account WHERE aid = %s", (user_id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()


    if user:
        return jsonify({
            'user_id': user["aid"],
            'fname': user["fname"],
            'lname': user["lname"],
            'type': user["type"],
            'created_at': user["created_at"].strftime('%Y-%m-%d %H:%M:%S')
        }), 200
    else:
        return jsonify({"error":"User not found"}), 404



# =================================== Course Creation ===================================

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    cname = data.get("cname")
    user_type = data.get("user_type")

    if not cname or user_type != "admin":
        return jsonify({"error":"Invalid request. Only admins can create courses."})

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO Course (cname) VALUES (%s)", (cname,))
        conn.commit()
        return jsonify({"message": "Course created successfully"})

    except Exception as e:
        return jsonify({"error":str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Retrieve Courses ===================================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    user_type = request.args.get("user_type")
    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if user_type == "student":
            cursor.execute("""
            SELECT c.cid, c.cname FROM Course c
            JOIN StudentCourse sc ON c.cid = sc.cid
            WHERE sc.sid = %s
            """, (user_id,))
        elif user_type == "lecturer":
            cursor.execute("""
            SELECT c.cid, c.cname FROM Course c
            JOIN LecturerCourse lc ON c.cid = lc.cid
            WHERE lc.lid = %s
            """, (user_id,))
        else:
            cursor.execute("SELECT c.cid, c.cname FROM Course c")

        courses = cursor.fetchall()
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Student Enrollment ===================================

@app.route('/api/enroll', methods=['POST'])
def enroll_student():
    data = request.json
    sid = data.get("sid")
    cid = data.get("cid")

    if not sid or not cid:
        return jsonify({"error": "Student ID and Course ID are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM StudentCourse WHERE sid = %s AND cid = %s", (sid, cid))
        if cursor.fetchone():
            return jsonify({"error": "Student is already in this course"}), 409
        
        # Insert student into the course
        cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
        conn.commit()
        
        cursor.execute("UPDATE Course SET participants = participants + 1 WHERE cid = %s", (cid,))

        conn.commit()
        # Note: The trigger will automatically update the participants count
        return jsonify({"message": "Student enrolled successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Assign Lecturer to Course ===================================

@app.route('/api/assign_lecturer', methods=['POST'])
def assign_lecturer():
    data = request.json
    lid = data.get('lid')
    cid = data.get('cid')
    user_type = data.get('user_type')

    if user_type != 'admin':
        return jsonify({"error": "Only admins can assign lecturers"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO LecturerCourse (lid, cid) VALUES (%s,%s)", (lid, cid))
        conn.commit()
        return jsonify({"message": "Lecturer assigned successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Retrieve Members ===================================

@app.route('/api/course/<int:course_id>/members', methods=['GET'])
def get_course_members(course_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT a.aid, a.fname, a.lname, 'student' AS role
        FROM Account a
        JOIN StudentCourse sc on a.aid = sc.sid
        WHERE sc.cid = %s
        UNION ALL
        SELECT a.aid, a.fname, a.lname, 'lecturer' AS role
        FROM Account a
        JOIN LecturerCourse lc ON a.aid = lc.lid
        WHERE lc.cid = %s
        """, (course_id, course_id))

        members = cursor.fetchall()
        return jsonify(members), 200
    except Exception as e:
        return jsonify ({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Retrieve Calendar Events ===================================
@app.route('/api/calendar_events', methods=['GET'])
def get_calendar_events():
    data = request.json if request.is_json else {}
    
    course_id = data.get("course_id") or request.args.get("course_id")
    date = data.get("date") or request.args.get("date")
    student_id = data.get("student_id") or request.args.get("student_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if course_id:
            cursor.execute("SELECT * FROM CalendarEvent WHERE cid = %s", (course_id,))
        elif date and student_id:
            cursor.execute("""
                SELECT ce.* FROM CalendarEvent ce
                JOIN StudentCourse sc ON ce.cid = sc.cid
                WHERE sc.sid = %s AND ce.event_date = %s
            """, (student_id, date))
        else:
            return jsonify({"error": "Invalid query parameters"}), 400

        events = cursor.fetchall()
        
        # Format the dates for JSON serialization
        formatted_events = []
        for event in events:
            event_dict = dict(event)
            if 'event_date' in event_dict and event_dict['event_date']:
                event_dict['event_date'] = event_dict['event_date'].strftime('%Y-%m-%d')
            if 'created_at' in event_dict and event_dict['created_at']:
                event_dict['created_at'] = event_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            formatted_events.append(event_dict)
            
        return jsonify(formatted_events), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
# =================================== Create Calendar Events ===================================
@app.route('/api/calendar_events', methods=['POST'])
def create_calendar_event():
    data = request.json
    description = data.get("data")  # Added this line to match table
    calname = data.get("calname")
    event_date = data.get("event_date")
    cid = data.get("cid")
    event_data = data.get("data", "")

    if not all([calname, event_date, cid]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Updated to include the 'data' column
        cursor.execute("INSERT INTO CalendarEvent (data, calname, event_date, cid) VALUES (%s, %s, %s, %s)",
                      (description, calname, event_date, cid))
        conn.commit()
        return jsonify({"message": "Calendar event created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Retrieve Forums ===================================

@app.route('/api/forums', methods=['GET'])
def get_forums():
    course_id = request.args.get("course_id")

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        if course_id:
            cursor.execute("SELECT dfid, dfname FROM DiscussionForum WHERE cid = %s", (course_id,))
        else:
            cursor.execute("SELECT dfid, dfname, cid FROM DiscussionForum")

        forums = cursor.fetchall()
        return jsonify(forums), 200
    except Exception as e:
        return jsonify({"error": str(e)}),500
    finally:
        cursor.close()
        conn.close()

# =================================== Create Forums ===================================

@app.route('/api/forums', methods=['POST'])
def create_forum():
    data = request.json
    dfname = data.get("dfname")
    cid = data.get("cid")
    user_type = data.get("user_type")

    if user_type not in ['admin', 'lecturer']:
        return jsonify({"error": "Only admins and lecturers can create forums."}), 403

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO DiscussionForum (dfname, cid) VALUES (%s, %s)", (dfname, cid))
        conn.commit()
        return jsonify({"message": "Forum created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Retrieve Discussion Threads ===================================
@app.route('/api/threads', methods=['GET'])
def get_threads():
    # Get forum_id from either query parameter name
    data = request.json if request.is_json else {}
    forum_id = request.args.get("dfid") or request.args.get("forum_id") or data.get("dfid") or data.get("forum_id")
    
    if not forum_id:
        return jsonify({"error": "Forum ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT dtid, dtname, dttext, dfid, aid, parent_dtid, created_at 
            FROM DiscussionThread 
            WHERE dfid = %s
        """, (forum_id,))
            
        threads = cursor.fetchall()
        
        # Format the dates for JSON serialization
        formatted_threads = []
        for thread in threads:
            thread_dict = dict(thread)
            if 'created_at' in thread_dict and thread_dict['created_at']:
                thread_dict['created_at'] = thread_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            formatted_threads.append(thread_dict)
            
        return jsonify(formatted_threads), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Retrieve Discussion Threads ===================================
@app.route('/api/threads/reply', methods=['POST'])
def reply_to_thread():
    data = request.json
    dtid = data.get("dtid")
    aid = data.get("aid")
    dttext = data.get("dttext")

    if not all([dtid, aid, dttext]):
        return jsonify({"error": "Missing required fields"}), 400
    

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # First, get the parent thread's forum ID
        cursor.execute("SELECT dfid FROM DiscussionThread WHERE dtid = %s", (dtid,))
        parent_thread = cursor.fetchone()
        
        if not parent_thread:
            return jsonify({"error": "Parent thread not found"}), 404
            
        dfid = parent_thread["dfid"]
        
        # Now insert the reply with proper values
        cursor.execute("""
            INSERT INTO DiscussionThread (dtname, dttext, dfid, aid, parent_dtid) 
            VALUES (%s, %s, %s, %s, %s)
        """, (f"RE: Thread {dtid}", dttext, dfid, aid, dtid))
        
        conn.commit()
        return jsonify({"message": "Reply added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Course Content ===================================
@app.route('/api/content', methods=['POST'])
def add_course_content():
    data = request.json
    itemname = data.get('itemname')
    secid = data.get("secid")
    content_type = data.get("type") or data.get("content_type")
    # Added this line to match table
    file_path = data.get("file_path", None)
    hyplink = data.get("hyplink", None)

    if not all([itemname, secid, content_type]):
        return jsonify({"error": "Missing required fields"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, %s)",
                       (itemname, secid, content_type))
        conn.commit()
        itemid = cursor.lastrowid

        if content_type == 'document' and file_path:
            cursor.execute("INSERT INTO Document (docid, docname, file_path) VALUES (%s, %s, %s)",
                           (itemid, itemname, file_path))
        elif content_type == 'lecture_slide' and file_path:
            cursor.execute("INSERT INTO LectureSlide (lsid, lsname, file_path) VALUES (%s, %s, %s)",
                           (itemid, itemname, file_path))
        elif content_type == 'link' and hyplink:
            cursor.execute("INSERT INTO Link (linkid, linkname, hyplink) VALUES (%s, %s, %s)",
                           (itemid, itemname, hyplink))
        conn.commit()
        return jsonify({"message": "Course content added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Retrieve Course Content ===================================
@app.route('/api/content', methods=['GET'])
def get_course_content():
    course_id = request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "Course ID is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT si.itemid, si.itemname, si.type, d.file_path AS document_path, ls.file_path AS slide_path, l.hyplink AS link
            FROM SectionItem si
            LEFT JOIN Document d ON si.itemid = d.docid
            LEFT JOIN LectureSlide ls ON si.itemid = ls.lsid
            LEFT JOIN Link l on si.itemid = l.linkid
            JOIN Section s ON si.secid = s.secid
            WHERE s.cid = %s
        """, (course_id,))
        content = cursor.fetchall()
        return jsonify(content), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Assignments Creation ===================================

@app.route('/api/assignments', methods=['POST'])
def create_assignment():
    data = request.json
    itemid = data.get("itemid")
    submitbox = data.get("submitbox")
    max_score = data.get("max_score")
    due_date = data.get("due_date")

    if not all([itemid, due_date]):
        return jsonify({"error": "Missing required fields."}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        # Check if the itemid exists in SectionItem
        cursor.execute("SELECT itemid FROM SectionItem WHERE itemid = %s", (itemid,))
        if not cursor.fetchone():
            return jsonify({"error": "Item ID does not exist in SectionItem."}), 404

        cursor.execute("INSERT INTO Assignment (asid, submitbox, max_score, due_date) VALUES (%s, %s, %s, %s)",
                       (itemid, submitbox, max_score, due_date))
        conn.commit()
        return jsonify({"message": "Assignment created successfully."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Retrieve Assignments ===================================
@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    data = request.json if request.is_json else {}
    course_id = data.get("course_id") or request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "CourseID is required."}), 400
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
        SELECT a.asid, si.itemname, a.max_score, a.due_date
        FROM Assignment a 
        JOIN SectionItem si ON a.asid = si.itemid
        JOIN Section s ON si.secid = s.secid
        WHERE s.cid = %s 
        """, (course_id,))
        assignments = cursor.fetchall()
        return jsonify(assignments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# =================================== Submit Assignments ===================================
@app.route('/api/submit_assignment', methods=['POST'])
def submit_assignment():
    data = request.json
    asid = data.get("asid")
    sid = data.get("sid")
    file_path = data.get("file_name", "assignment")

    if not all([asid, sid]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    file_path = f"uploads/{asid}/{sid}/{file_path}"
    try:
        cursor.execute("INSERT INTO AssignmentSubmission (asid, sid, file_path) VALUES (%s, %s, %s)",
                       (asid, sid, file_path))
        conn.commit()
        return jsonify({"message": "Assignment submitted successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Grade Assignments ===================================
@app.route('/api/grade_assignment', methods= ['POST'])
def grade_assignment():
    data = request.json
    submission_id = data.get("submission_id")
    grade = data.get("grade")

    if not all([submission_id, grade]):
        return jsonify({"error": "Missing required fields"}), 400
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE AssignmentSubmission SET grade = %s WHERE submission_id= %s",
                       (grade, submission_id))
        conn.commit()
        return jsonify({"message": "Assignment graded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# =================================== Utility Functions ===================================
@app.route('/api/admin/fix_participant_counts', methods=['POST'])
def fix_participant_counts():
    user_type = request.json.get("user_type")
    
    if user_type != "admin":
        return jsonify({"error": "Only admins can run maintenance functions"}), 403
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
        UPDATE Course c
        SET c.participants = (
            SELECT COUNT(*) 
            FROM StudentCourse sc 
            WHERE sc.cid = c.cid
        )
        """)
        conn.commit()
        return jsonify({"message": "Participant counts updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(port=5000,debug=True)