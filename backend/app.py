from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from config import execute_query
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

    if not all([fname, lname, password, user_type]):
        return jsonify({"error": "Missing required fields"}), 400

    hashed_password = bcrypt.generate_password_hash(str(password)).decode('utf-8')
    
    try:
        # Insert into Account table
        query = "INSERT INTO Account (password, type, fname, lname) VALUES(%s, %s, %s, %s)"
        params = (hashed_password, user_type, fname, lname)
        user_id = execute_query(query, params, commit=True)

        # Insert into specific role table
        if user_type == "admin":
            execute_query("INSERT INTO Admin (adid) VALUES (%s)", (user_id,), commit=True)
        elif user_type == "lecturer":
            execute_query("INSERT INTO Lecturer (lid) VALUES (%s)", (user_id,), commit=True)
        elif user_type == "student":
            execute_query("INSERT INTO Student (sid) VALUES (%s)", (user_id,), commit=True)

        return jsonify({"message": "User registered successfully", "user_id": user_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== User Login ===================================

@app.route("/api/login", methods=['POST'])
def login():
    data = request.json
    fname = data.get("fname")
    lname = data.get("lname")
    password = data.get("password")

    if not all([fname, lname, password]):
        return jsonify({"error": "Missing credentials"}), 400

    try:
        query = "SELECT aid, password, type FROM Account WHERE fname = %s AND lname = %s"
        user = execute_query(query, (fname, lname))
        
        if user and len(user) > 0 and bcrypt.check_password_hash(user[0]["password"], password):
            return jsonify({
                "message": "Login successful", 
                "user_id": user[0]["aid"], 
                "type": user[0]["type"]
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve User Information ===================================

@app.route("/api/user/<int:user_id>", methods=['GET'])
def get_user(user_id):
    try:
        query = "SELECT aid, fname, lname, type, created_at FROM Account WHERE aid = %s"
        users = execute_query(query, (user_id,))
        
        if users and len(users) > 0:
            user = users[0]
            return jsonify({
                'user_id': user["aid"],
                'fname': user["fname"],
                'lname': user["lname"],
                'type': user["type"],
                'created_at': user["created_at"].strftime('%Y-%m-%d %H:%M:%S')
            }), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Course Creation ===================================

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    cname = data.get("cname")
    user_type = data.get("user_type")

    if not cname or user_type != "admin":
        return jsonify({"error": "Invalid request. Only admins can create courses."}), 400

    try:
        execute_query("INSERT INTO Course (cname) VALUES (%s)", (cname,), commit=True)
        return jsonify({"message": "Course created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Courses ===================================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    user_type = request.args.get("user_type")
    user_id = request.args.get("user_id")

    try:
        if user_type == "student":
            query = """
            SELECT c.cid, c.cname FROM Course c
            JOIN StudentCourse sc ON c.cid = sc.cid
            WHERE sc.sid = %s
            """
            courses = execute_query(query, (user_id,))
        elif user_type == "lecturer":
            query = """
            SELECT c.cid, c.cname FROM Course c
            JOIN LecturerCourse lc ON c.cid = lc.cid
            WHERE lc.lid = %s
            """
            courses = execute_query(query, (user_id,))
        else:
            courses = execute_query("SELECT c.cid, c.cname FROM Course c")
            
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Student Enrollment ===================================

@app.route('/api/enroll', methods=['POST'])
def enroll_student():
    data = request.json
    sid = data.get("sid")
    cid = data.get("cid")

    if not sid or not cid:
        return jsonify({"error": "Student ID and Course ID are required"}), 400

    try:
        # Check if already enrolled
        query = "SELECT * FROM StudentCourse WHERE sid = %s AND cid = %s"
        existing = execute_query(query, (sid, cid))
        
        if existing and len(existing) > 0:
            return jsonify({"error": "Student is already in this course"}), 409
        
        # Enroll student
        execute_query("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", 
                     (sid, cid), commit=True)
        
        # Note: The trigger will automatically update the participants count
        return jsonify({"message": "Student enrolled successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Assign Lecturer to Course ===================================

@app.route('/api/assign_lecturer', methods=['POST'])
def assign_lecturer():
    data = request.json
    lid = data.get('lid')
    cid = data.get('cid')
    user_type = data.get('user_type')

    if user_type != 'admin':
        return jsonify({"error": "Only admins can assign lecturers"}), 403

    try:
        execute_query("INSERT INTO LecturerCourse (lid, cid) VALUES (%s,%s)", 
                     (lid, cid), commit=True)
        return jsonify({"message": "Lecturer assigned successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Members ===================================

@app.route('/api/course/<int:course_id>/members', methods=['GET'])
def get_course_members(course_id):
    try:
        query = """
        SELECT a.aid, a.fname, a.lname, 'student' AS role
        FROM Account a
        JOIN StudentCourse sc on a.aid = sc.sid
        WHERE sc.cid = %s
        UNION ALL
        SELECT a.aid, a.fname, a.lname, 'lecturer' AS role
        FROM Account a
        JOIN LecturerCourse lc ON a.aid = lc.lid
        WHERE lc.cid = %s
        """
        members = execute_query(query, (course_id, course_id))
        return jsonify(members), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Calendar Events ===================================
@app.route('/api/calendar_events', methods=['GET'])
def get_calendar_events():
    data = request.json if request.is_json else {}
    
    course_id = data.get("course_id") or request.args.get("course_id")
    date = data.get("date") or request.args.get("date")
    student_id = data.get("student_id") or request.args.get("student_id")

    try:
        if course_id:
            query = "SELECT * FROM CalendarEvent WHERE cid = %s"
            events = execute_query(query, (course_id,))
        elif date and student_id:
            query = """
                SELECT ce.* FROM CalendarEvent ce
                JOIN StudentCourse sc ON ce.cid = sc.cid
                WHERE sc.sid = %s AND ce.event_date = %s
            """
            events = execute_query(query, (student_id, date))
        else:
            return jsonify({"error": "Invalid query parameters"}), 400
        
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


# =================================== Create Calendar Events ===================================
@app.route('/api/calendar_events', methods=['POST'])
def create_calendar_event():
    data = request.json
    description = data.get("data")  # Added this line to match table
    calname = data.get("calname")
    event_date = data.get("event_date")
    cid = data.get("cid")

    if not all([calname, event_date, cid]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        query = "INSERT INTO CalendarEvent (data, calname, event_date, cid) VALUES (%s, %s, %s, %s)"
        execute_query(query, (description, calname, event_date, cid), commit=True)
        return jsonify({"message": "Calendar event created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Forums ===================================

@app.route('/api/forums', methods=['GET'])
def get_forums():
    course_id = request.args.get("course_id")

    try:
        if course_id:
            query = "SELECT dfid, dfname FROM DiscussionForum WHERE cid = %s"
            forums = execute_query(query, (course_id,))
        else:
            forums = execute_query("SELECT dfid, dfname, cid FROM DiscussionForum")

        return jsonify(forums), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Create Forums ===================================

@app.route('/api/forums', methods=['POST'])
def create_forum():
    data = request.json
    dfname = data.get("dfname")
    cid = data.get("cid")
    user_type = data.get("user_type")

    if user_type not in ['admin', 'lecturer']:
        return jsonify({"error": "Only admins and lecturers can create forums."}), 403

    try:
        execute_query("INSERT INTO DiscussionForum (dfname, cid) VALUES (%s, %s)", 
                     (dfname, cid), commit=True)
        return jsonify({"message": "Forum created successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Discussion Threads ===================================
@app.route('/api/threads', methods=['GET'])
def get_threads():
    # Get forum_id from either query parameter name
    data = request.json if request.is_json else {}
    forum_id = request.args.get("dfid") or request.args.get("forum_id") or data.get("dfid") or data.get("forum_id")
    
    if not forum_id:
        return jsonify({"error": "Forum ID is required"}), 400

    try:
        query = """
            SELECT dtid, dtname, dttext, dfid, aid, parent_dtid, created_at 
            FROM DiscussionThread 
            WHERE dfid = %s
        """
        threads = execute_query(query, (forum_id,))
        
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


# =================================== Retrieve Discussion Threads ===================================
@app.route('/api/threads/reply', methods=['POST'])
def reply_to_thread():
    data = request.json
    dtid = data.get("dtid")
    aid = data.get("aid")
    dttext = data.get("dttext")

    try:
        query = """
            INSERT INTO DiscussionThread (dtname, dttext, dfid, aid, parent_dtid) 
            VALUES (%s, %s, NULL, %s, %s)
        """
        execute_query(query, ("RE: " + str(dtid), dttext, aid, dtid), commit=True)
        return jsonify({"message": "Reply added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Course Content ===================================
@app.route('/api/content', methods=['POST'])
def add_course_content():
    data = request.json
    itemname = data.get('itemname')
    secid = data.get("secid")
    content_type = data.get("type") or data.get("content_type")
    file_path = data.get("file_path", None)
    hyplink = data.get("hyplink", None)

    if not all([itemname, secid, content_type]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        # Insert base section item
        query = "INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, %s)"
        itemid = execute_query(query, (itemname, secid, content_type), commit=True)

        # Insert specific content type
        if content_type == 'document' and file_path:
            query = "INSERT INTO Document (docid, docname, file_path) VALUES (%s, %s, %s)"
            execute_query(query, (itemid, itemname, file_path), commit=True)
        elif content_type == 'lecture_slide' and file_path:
            query = "INSERT INTO LectureSlide (lsid, lsname, file_path) VALUES (%s, %s, %s)"
            execute_query(query, (itemid, itemname, file_path), commit=True)
        elif content_type == 'link' and hyplink:
            query = "INSERT INTO Link (linkid, linkname, hyplink) VALUES (%s, %s, %s)"
            execute_query(query, (itemid, itemname, hyplink), commit=True)
            
        return jsonify({"message": "Course content added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Course Content ===================================
@app.route('/api/content', methods=['GET'])
def get_course_content():
    course_id = request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "Course ID is required"}), 400

    try:
        query = """
            SELECT si.itemid, si.itemname, si.type, d.file_path AS document_path, 
                   ls.file_path AS slide_path, l.hyplink AS link
            FROM SectionItem si
            LEFT JOIN Document d ON si.itemid = d.docid
            LEFT JOIN LectureSlide ls ON si.itemid = ls.lsid
            LEFT JOIN Link l ON si.itemid = l.linkid
            JOIN Section s ON si.secid = s.secid
            WHERE s.cid = %s
        """
        content = execute_query(query, (course_id,))
        return jsonify(content), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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

    try:
        # Check if the itemid exists in SectionItem
        check_query = "SELECT itemid FROM SectionItem WHERE itemid = %s"
        item = execute_query(check_query, (itemid,))
        
        if not item or len(item) == 0:
            return jsonify({"error": "Item ID does not exist in SectionItem."}), 404

        # Create assignment
        query = "INSERT INTO Assignment (asid, submitbox, max_score, due_date) VALUES (%s, %s, %s, %s)"
        execute_query(query, (itemid, submitbox, max_score, due_date), commit=True)
        
        return jsonify({"message": "Assignment created successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Retrieve Assignments ===================================
@app.route('/api/assignments', methods=['GET'])
def get_assignments():
    data = request.json if request.is_json else {}
    course_id = data.get("course_id") or request.args.get("course_id")

    if not course_id:
        return jsonify({"error": "CourseID is required."}), 400
    
    try:
        query = """
        SELECT a.asid, si.itemname, a.max_score, a.due_date
        FROM Assignment a 
        JOIN SectionItem si ON a.asid = si.itemid
        JOIN Section s ON si.secid = s.secid
        WHERE s.cid = %s 
        """
        assignments = execute_query(query, (course_id,))
        
        # Format dates if needed
        formatted_assignments = []
        for assignment in assignments:
            assignment_dict = dict(assignment)
            if 'due_date' in assignment_dict and assignment_dict['due_date']:
                assignment_dict['due_date'] = assignment_dict['due_date'].strftime('%Y-%m-%d %H:%M:%S')
            formatted_assignments.append(assignment_dict)
        
        return jsonify(formatted_assignments), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Submit Assignments ===================================
@app.route('/api/submit_assignment', methods=['POST'])
def submit_assignment():
    data = request.json
    asid = data.get("asid")
    sid = data.get("sid")
    file_path = data.get("file_path", "")

    if not all([asid, sid]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        query = "INSERT INTO AssignmentSubmission (asid, sid, file_path) VALUES (%s, %s, %s)"
        execute_query(query, (asid, sid, file_path), commit=True)
        return jsonify({"message": "Assignment submitted successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Grade Assignments ===================================
@app.route('/api/grade_assignment', methods=['POST'])
def grade_assignment():
    data = request.json
    submission_id = data.get("submission_id")
    grade = data.get("grade")

    if not all([submission_id, grade]):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        query = "UPDATE AssignmentSubmission SET grade = %s WHERE submission_id = %s"
        execute_query(query, (grade, submission_id), commit=True)
        return jsonify({"message": "Assignment graded successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# =================================== Utility Functions ===================================
@app.route('/api/admin/fix_participant_counts', methods=['POST'])
def fix_participant_counts():
    user_type = request.json.get("user_type")
    
    if user_type != "admin":
        return jsonify({"error": "Only admins can run maintenance functions"}), 403
    
    try:
        query = """
        UPDATE Course c
        SET c.participants = (
            SELECT COUNT(*) 
            FROM StudentCourse sc 
            WHERE sc.cid = c.cid
        )
        """
        execute_query(query, commit=True)
        return jsonify({"message": "Participant counts updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=8080, debug=True)