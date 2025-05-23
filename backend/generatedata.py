import random
import pymysql
from hashlib import blake2b
from faker import Faker
from tqdm import  tqdm
from config import get_db_connection
from datetime import  datetime, timedelta

fake = Faker()

NUM_STUDENTS = 200000  #200000
NUM_LECTURERS = 15000 #2000
NUM_COURSES = 600
NUM_ASSIGNMENTS = 500
NUM_ADMINS = 50
 


prefixes = ['Intro to', 'Advanced', 'Fundamentals of', 'Principles of', 'Basics of', 'Applied', 'Studies in',
                 'Research Methods in', 'Applied', 'Theories of', 'Concepts in', 'Introduction to']
suffixes =['Science', 'Mathematics', 'Engineering', 'Computing', 'Biology', 'Physics', 'Chemistry', 'Economics', 'Psychology', 'Distributed Systems', 'Database Management Systems',
                'Machine Learning', 'Artificial Intelligence', 'Software Engineering', 'Web Development', 'Data Science', 'Cybersecurity', 'Networking', 'Human-Computer Interaction', 
                'Cloud Computing', 'Information Systems']
    

# =========================== Insert Students ===========================


def insert_students(NUM_STUDENTS):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {NUM_STUDENTS} students...")

    for i in tqdm(range(NUM_STUDENTS)):
        fname = fake.first_name()
        lname = fake.last_name()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        # Hash the password using Blake2b
        password= blake2b(password.encode(), digest_size=32).hexdigest()
        # Insert into Account
        cursor.execute("INSERT INTO Account (password, type, fname, lname) values (%s, 'student', %s, %s)",
                       (password, fname, lname))
        student_id = cursor.lastrowid

        # Insert into Student
        cursor.execute("INSERT INTO Student (sid) VALUES (%s)", (student_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("Students inserted successfully.")

# =========================== Insert Lecturers ===========================

def insert_lecturers(NUM_LECTURERS):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {NUM_LECTURERS} lecturers...")


    for _ in tqdm(range(NUM_LECTURERS)):
        fname = fake.first_name()
        lname = fake.last_name()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        # Hash the password using Blake2b
        password= blake2b(password.encode(), digest_size=32).hexdigest()

        cursor.execute("INSERT INTO Account (password, type, fname, lname) VALUES (%s, 'lecturer', %s, %s)",
                       (password,fname,lname))
        lecturer_id = cursor.lastrowid

        cursor.execute("INSERT INTO Lecturer (lid) VALUES (%s)", (lecturer_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("Lecturers inserted successfully.")

# =========================== Insert Admins ===========================

def insert_admins(NUM_ADMINS):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {NUM_ADMINS} admins...")

    for _ in tqdm(range(NUM_ADMINS)):
        fname = fake.first_name()
        lname = fake.last_name()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        # Hash the password using Blake2b
        password= blake2b(password.encode(), digest_size=32).hexdigest()

        cursor.execute("INSERT INTO Account (password, type, fname, lname) VALUES (%s, 'admin', %s, %s)",
                       (password, fname, lname))
        admin_id = cursor.lastrowid

        cursor.execute("INSERT INTO Admin (adid) VALUES (%s)", (admin_id,))

    conn.commit()
    cursor.close()
    conn.close()
    print("Admins inserted successfully.")

# =========================== Insert Assignments ===========================


def insert_assignments(NUM_ASSIGNMENTS):
    conn = get_db_connection()
    cursor = conn.cursor()
    print(f"Inserting {NUM_ASSIGNMENTS} assignments...")

    # Clear existing assignments to avoid conflicts
    try:
        cursor.execute("DELETE FROM Assignment")
        print("Cleared existing assignments.")
    except pymysql.MySQLError as e:
        print(f"Warning: Could not clear existing assignments: {e}")

    cursor.execute("SELECT secid FROM Section")
    sections = [row["secid"] for row in cursor.fetchall()]

    if not sections:
        print("No sections found. Skipping assignment insertion.")
        return

    for i in tqdm(range(NUM_ASSIGNMENTS)):
        secid = random.choice(sections)
        try:
            cursor.execute("INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, 'assignment')",
                       (fake.catch_phrase(), secid))
            itemid = cursor.lastrowid
            cursor.execute("INSERT INTO Assignment (asid, submitbox, max_score, due_date) VALUES (%s, '', 100.0, NOW())",
                       (itemid,))
        except pymysql.MySQLError as e:
            print(f"Error inserting assignment {i}: {e}")
            continue

    conn.commit()
    cursor.close()
    conn.close()
    print("Assignments inserted successfully.")

# =========================== Insert Courses ===========================
def insert_courses(NUM_COURSES):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {NUM_COURSES} courses...")

    
    # Generate course names
    course_names = []
    used_combinations = set()

    all_combinations = [(p,s) for p in prefixes for s in suffixes]
    random.shuffle(all_combinations)

    max_possible = min(NUM_COURSES, len(all_combinations))
    selected_combinations = all_combinations[:max_possible]

    course_names = [f'{prefix} {suffix}' for prefix, suffix in selected_combinations]

    print(f"Generated {len(course_names)} unique course names.")

    try:
        batch = 100
        for i in range(0, len(course_names), batch):
            batch_names = course_names[i:i+batch]
            args = [(name,) for name in batch_names]
            cursor.executemany("INSERT INTO Course (cname) VALUES (%s)", args)
            conn.commit()
            print(f"Inserted batch {i//batch + 1}/{(len(course_names)-1)//batch + 1} " f"({len(batch_names)} courses)")
    except Exception as e:
        print(f"Error inserting courses: {e}")
    finally:
        cursor.close()
        conn.close()
    print("Courses inserted successfully.")


# =========================== Insert Sections ===========================
def insert_sections():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Inserting sections...")

    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    for cid in courses:
        for i in range(random.randint(2,5)): # Each course 2-5 sections
            secname = fake.catch_phrase()
            cursor.execute("INSERT INTO Section (secname, cid) VALUES (%s, %s)", (secname, cid))

    conn.commit()
    cursor.close()
    conn.close()
    print("Sections inserted.")

# =========================== Enroll Students in Courses ===========================
def enroll_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Enrolling students in courses...")

    # Clear existing enrollments to avoid conflicts
    try:
        cursor.execute("DELETE FROM StudentCourse")
        print("Cleared existing student enrollments.")
    except pymysql.MySQLError as e:
        print(f"Warning: Could not clear existing enrollments: {e}")

    cursor.execute("SELECT sid FROM Student")
    students = [row['sid'] for row in cursor.fetchall()]

    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    # Track already assigned enrollments
    enrolled_pairs = set()
    
    # First, ensure each course has at least 10 students
    print("Ensuring each course has at least 10 students...")
    for cid in tqdm(courses):
        enrolled_count = 0
        
        # Enroll at least 10 students in each course
        for _ in range(10):
            # Find a student with fewer than 6 courses
            eligible_students = []
            for sid in students:
                student_courses = sum(1 for pair in enrolled_pairs if pair[0] == sid)
                if student_courses < 6:
                    eligible_students.append(sid)
            
            if not eligible_students:
                print(f"Warning: Not enough eligible students for course {cid}. Try increasing NUM_STUDENTS.")
                break
                
            sid = random.choice(eligible_students)
            pair = (sid, cid)
            
            if pair not in enrolled_pairs:
                try:
                    cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
                    enrolled_pairs.add(pair)
                    enrolled_count += 1
                except pymysql.err.IntegrityError as e:
                    print(f"Warning: Could not enroll student {sid} in course {cid}: {e}")
    
    # Now, ensure each student has at least 3 courses (but no more than 6)
    print("Ensuring each student has at least 3 courses...")
    for sid in tqdm(students):
        # Count current enrollment for this student
        student_courses = sum(1 for pair in enrolled_pairs if pair[0] == sid)
        
        # If student has fewer than 3 courses, enroll them in more
        if student_courses < 3:
            # Calculate how many more courses this student needs
            needed_courses = 3 - student_courses
            
            # Find courses this student is not yet enrolled in
            available_courses = [cid for cid in courses if (sid, cid) not in enrolled_pairs]
            
            # Randomly select courses to enroll this student in
            if available_courses:
                to_enroll = min(needed_courses, len(available_courses), 6 - student_courses)
                for cid in random.sample(available_courses, to_enroll):
                    try:
                        cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
                        enrolled_pairs.add((sid, cid))
                    except pymysql.err.IntegrityError as e:
                        print(f"Warning: Could not enroll student {sid} in course {cid}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Students enrolled successfully.")

# Add this new function to verify and fix any remaining issues
def verify_enrollment_constraints():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Verifying enrollment constraints...")
    
    # Check for students with more than 6 courses
    cursor.execute("""
        SELECT sc.sid, COUNT(sc.cid) AS course_count
        FROM StudentCourse sc
        GROUP BY sc.sid
        HAVING COUNT(sc.cid) > 6
    """)
    
    violations = cursor.fetchall()
    if violations:
        print(f"Found {len(violations)} students enrolled in more than 6 courses. Fixing...")
        
        for row in violations:
            sid = row['sid']
            course_count = row['course_count']
            to_remove = course_count - 6
            
            # Find courses for this student that have more than 10 students
            cursor.execute("""
                SELECT sc.cid 
                FROM StudentCourse sc
                JOIN (
                    SELECT cid, COUNT(sid) as student_count
                    FROM StudentCourse
                    GROUP BY cid
                    HAVING COUNT(sid) > 10
                ) c ON sc.cid = c.cid
                WHERE sc.sid = %s
            """, (sid,))
            
            safe_to_remove = [row['cid'] for row in cursor.fetchall()]
            
            if len(safe_to_remove) >= to_remove:
                # Remove excess enrollments only from courses that have more than 10 students
                for cid in random.sample(safe_to_remove, to_remove):
                    cursor.execute("DELETE FROM StudentCourse WHERE sid = %s AND cid = %s", (sid, cid))
            else:
                # Not enough safe courses, remove from any course
                cursor.execute("SELECT cid FROM StudentCourse WHERE sid = %s", (sid,))
                all_courses = [row['cid'] for row in cursor.fetchall()]
                for cid in random.sample(all_courses, to_remove):
                    cursor.execute("DELETE FROM StudentCourse WHERE sid = %s AND cid = %s", (sid, cid))
    
    # Check for courses with fewer than 10 students
    cursor.execute("""
        SELECT c.cid, c.cname, COUNT(sc.sid) AS student_count
        FROM Course c
        LEFT JOIN StudentCourse sc ON c.cid = sc.cid
        GROUP BY c.cid, c.cname
        HAVING COUNT(sc.sid) < 10
    """)
    
    under_enrolled = cursor.fetchall()
    if under_enrolled:
        print(f"Found {len(under_enrolled)} courses with fewer than 10 students. Fixing...")
        
        # Get students with fewer than 6 courses
        cursor.execute("""
            SELECT s.sid, COUNT(sc.cid) AS course_count
            FROM Student s
            LEFT JOIN StudentCourse sc ON s.sid = sc.sid
            GROUP BY s.sid
            HAVING COUNT(sc.cid) < 6
            ORDER BY course_count ASC
        """)
        
        eligible_students = cursor.fetchall()
        if not eligible_students:
            print("No eligible students found with fewer than 6 courses. Cannot fix under-enrolled courses.")
            conn.close()
            return
        
        student_pool = [row['sid'] for row in eligible_students]
        student_index = 0
        
        for row in under_enrolled:
            cid = row['cid']
            current_count = row['student_count'] if row['student_count'] is not None else 0
            needed = 10 - current_count
            
            print(f"Course {cid} ({row['cname']}) has {current_count} students, needs {needed} more.")
            
            for _ in range(needed):
                if student_index >= len(student_pool):
                    # Reset to beginning if we've gone through all eligible students
                    student_index = 0
                    # Shuffle to avoid always picking the same students
                    random.shuffle(student_pool)
                
                sid = student_pool[student_index]
                student_index += 1
                
                # Check if this student is already in this course
                cursor.execute("SELECT 1 FROM StudentCourse WHERE sid = %s AND cid = %s", (sid, cid))
                if cursor.fetchone():
                    # Skip this student-course pair as it already exists
                    continue
                
                # Enroll the student
                cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
                
                # Update this student's course count
                cursor.execute("SELECT COUNT(cid) AS count FROM StudentCourse WHERE sid = %s", (sid,))
                count = cursor.fetchone()['count']
                
                # If student now has 6 courses, remove them from the pool
                if count >= 6:
                    if sid in student_pool:
                        student_pool.remove(sid)
            
            # Verify this course now has at least 10 students
            cursor.execute("SELECT COUNT(sid) AS count FROM StudentCourse WHERE cid = %s", (cid,))
            new_count = cursor.fetchone()['count']
            print(f"Course {cid} now has {new_count} students.")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Enrollment constraints verified and fixed.")


# =========================== Assign Lecturers to Courses ===========================

def assign_lecturers_to_courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Assigning lecturers to courses...")

    # Retrieve valid lecturer IDs
    cursor.execute("SELECT lid FROM Lecturer")
    lecturers = [row['lid'] for row in cursor.fetchall()]

    if not lecturers:
        print("Error: No lecturers found in the database. Ensure lecturers are inserted before running this function.")
        conn.close()
        return
    
    # Retrieve valid course IDs
    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    if not courses:
        print("Error: No courses found in the database. Ensure courses are inserted before running this function.")
        conn.close()
        return
    
    try:
        cursor.execute("DELETE FROM LecturerCourse")
        print("Cleared existing lecturer-course assignments.")
    except Exception as e:
        print(f"Warning: Could not clear existing assignments: {e}")

    # Creating special distribution such that lecturers will have 3+ courses
    # First 100 lecturers will be assigned to 3 courses each
    special_lecturers = lecturers[:100] if len(lecturers) >= 100 else lecturers
    regular_lecturers = lecturers[100:] if len(lecturers) >= 100 else []

    assigned_pairs = set()
    assigned_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    course_index = 0
    for lid in tqdm(special_lecturers, desc = "Assigning special lecturers"):
        courses_assigned = 0
        while courses_assigned < 3 and course_index < len(courses):
            cid = courses[course_index]
            pair = (lid, cid)

            if pair not in assigned_pairs:
                try:
                    cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)", 
                                   (lid, cid, assigned_date))
                    assigned_pairs.add(pair)
                    courses_assigned += 1
                except Exception as e:
                    print(f"Error assigning lecturer {lid} to course {cid}: {e}")
            course_index += 1

    # Create a set to track lecturers who have been assigned at least one course
    lecturers_with_courses = {lid for lid, _ in assigned_pairs}
    
    # First, ensure every lecturer has at least one course
    remaining_courses = courses[course_index:] if course_index < len(courses) else []
    
    # Assign one course to each remaining lecturer who doesn't have any
    unassigned_lecturers = [lid for lid in regular_lecturers if lid not in lecturers_with_courses]
    
    print(f"Ensuring {len(unassigned_lecturers)} lecturers have at least one course...")
    
    # Handle case where we might not have enough courses
    if len(unassigned_lecturers) > len(remaining_courses):
        print(f"Warning: Not enough courses ({len(remaining_courses)}) for all unassigned lecturers ({len(unassigned_lecturers)})")
        print("Creating additional courses...")
        
        needed_courses = len(unassigned_lecturers) - len(remaining_courses)
        
        # Create additional courses if needed
        for i in range(needed_courses):
            prefix = random.choice(prefixes)
            suffix = random.choice(suffixes)
            course_name = f"{prefix} {suffix} (Additional {i+1})"
            
            cursor.execute("INSERT INTO Course (cname) VALUES (%s)", (course_name,))
            new_cid = cursor.lastrowid
            remaining_courses.append(new_cid)
    
    # Now assign one course to each unassigned lecturer
    for i, lid in enumerate(tqdm(unassigned_lecturers, desc="Assigning courses to unassigned lecturers")):
        if i < len(remaining_courses):
            cid = remaining_courses[i]
            pair = (lid, cid)
            
            if pair not in assigned_pairs:
                try:
                    cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)",
                                   (lid, cid, assigned_date))
                    assigned_pairs.add(pair)
                    lecturers_with_courses.add(lid)
                except Exception as e:
                    print(f"Error assigning lecturer {lid} to course {cid}: {e}")
    
    # Distribute any remaining courses
    still_remaining_courses = remaining_courses[len(unassigned_lecturers):]
    
    for i, cid in enumerate(tqdm(still_remaining_courses, desc="Assigning remaining courses")):
        # Distribute remaining courses among all lecturers, prioritizing those with fewer courses
        cursor.execute("""
            SELECT l.lid, COUNT(lc.cid) AS course_count
            FROM Lecturer l
            LEFT JOIN LecturerCourse lc ON l.lid = lc.lid
            GROUP BY l.lid
            ORDER BY course_count ASC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        if result:
            lid = result['lid']
        else:
            # Fallback if the query doesn't work as expected
            lid = lecturers[i % len(lecturers)]
        
        pair = (lid, cid)
        
        if pair not in assigned_pairs:
            try:
                cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)",
                               (lid, cid, assigned_date))
                assigned_pairs.add(pair)
            except Exception as e:
                print(f"Error assigning lecturer {lid} to course {cid}: {e}")
    
    # Final verification - check if any lecturers still don't have courses
    cursor.execute("""
        SELECT l.lid
        FROM Lecturer l
        LEFT JOIN LecturerCourse lc ON l.lid = lc.lid
        WHERE lc.lid IS NULL
    """)
    
    unassigned = cursor.fetchall()
    if unassigned:
        print(f"Warning: There are still {len(unassigned)} lecturers without courses. Creating emergency courses...")
        
        for row in unassigned:
            lid = row['lid']
            emergency_course_name = f"Emergency Course for Lecturer {lid}"
            
            # Create an emergency course
            cursor.execute("INSERT INTO Course (cname) VALUES (%s)", (emergency_course_name,))
            new_cid = cursor.lastrowid
            
            # Assign the lecturer to this course
            cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)",
                           (lid, new_cid, assigned_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Lecturers assigned to courses successfully.")
# =========================== Insert Assignment Submissions ===========================

def insert_assignment_submissions():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Inserting assignment submissions...")

    try:
        # Fetch all assignment IDs and student IDs
        cursor.execute("SELECT asid FROM Assignment")
        assignments = [row['asid'] for row in cursor.fetchall()]

        cursor.execute("SELECT sid FROM Student")
        students = [row['sid'] for row in cursor.fetchall()]

        if not assignments or not students:
            print("No assignments or students found. Skipping submission insertion.")
            return

        # Insert 5000 assignment submissions
        for i in tqdm(range(5000)):
            asid = random.choice(assignments)
            sid = random.choice(students)
            grade = random.randint(50, 100)  # Generate grades

            cursor.execute("""
                INSERT INTO AssignmentSubmission (asid, sid, submission_date, file_path, grade) 
                VALUES (%s, %s, NOW(), '', %s)
            """, (asid, sid, grade))

        conn.commit()
        print("Assignment submissions inserted successfully.")

    except pymysql.MySQLError as e:
        print(f"MySQL Error: {e}")
    finally:
        cursor.close()
        conn.close()



# =========================== Insert Discussion Forums ===========================
def insert_discussion_forums():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Inserting discussion forums...")

    # Get all course IDs
    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    for cid in tqdm(courses):
        for i in range(random.randint(1, 3)):
            forum_name = fake.catch_phrase()
            cursor.execute("INSERT INTO DiscussionForum (dfname, cid) VALUES (%s, %s)", (forum_name, cid))
        
    conn.commit()
    cursor.close()
    conn.close()
    print("Discussion forums inserted successfully.")

def insert_discussion_threads():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Inserting discussion threads...")

    # Get all forum IDs
    cursor.execute("SELECT dfid FROM DiscussionForum")
    forums = [row['dfid'] for row in cursor.fetchall()]

    # Get account IDs
    cursor.execute("SELECT aid FROM Account LIMIT 1000")
    accounts = [row['aid'] for row in cursor.fetchall()]

    for dfid in tqdm(forums):
        for i in range(random.randint(3, 5)):
            thread_title = fake.sentence()
            thread_text = fake.paragraph()
            aid = random.choice(accounts)
            cursor.execute("INSERT INTO DiscussionThread (dtname, dttext,dfid, aid, parent_dtid) VALUES (%s, %s, %s, %s, NULL)", 
                           (thread_title, thread_text, dfid, aid))

    conn.commit()
    cursor.close()
    conn.close()
    print("Discussion threads inserted successfully.")

# =========================== Link Assignments to Calendar Events ===========================
def link_assignments_to_calendar_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Linking assignments to calendar events...")

    # Get all assignments
    cursor.execute("SELECT asid, due_date FROM Assignment")
    assignments = cursor.fetchall()

    if not assignments:
        print("No assignments found. Skipping assignment-calendar linking.")
        return

    for assignment in tqdm(assignments):
        asid = assignment['asid']
        due_date = assignment['due_date']
        
        # Create a calendar event for each assignment due date
        cursor.execute("""
            INSERT INTO CalendarEvent (data, calname, event_date, cid) 
            SELECT 'Assignment due date', 
                   CONCAT('Due: ', si.itemname), 
                   %s, 
                   s.cid
            FROM SectionItem si
            JOIN Section s ON si.secid = s.secid
            WHERE si.itemid = %s
        """, (due_date, asid))
        
        # Get the calendar event ID
        evid = cursor.lastrowid
        
        # Link assignment to calendar event
        cursor.execute("INSERT INTO AssignmentCalendarEvent (asid, evid) VALUES (%s, %s)",
                      (asid, evid))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Assignments linked to calendar events successfully.")

# =========================== Update Student Grades ===========================
def update_student_grades():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Updating student grades based on assignment submissions...")

    try:
        # Update student grades based on average of their submissions
        cursor.execute("""
            UPDATE Student s
            SET grade = (
                SELECT AVG(grade)
                FROM AssignmentSubmission asm
                WHERE asm.sid = s.sid AND asm.grade IS NOT NULL
                GROUP BY asm.sid
            )
            WHERE EXISTS (
                SELECT 1
                FROM AssignmentSubmission asm
                WHERE asm.sid = s.sid AND asm.grade IS NOT NULL
            )
        """)
        
        count = cursor.rowcount
        conn.commit()
        print(f"Updated grades for {count} students.")
    except Exception as e:
        print(f"Error updating student grades: {e}")
    finally:
        cursor.close()
        conn.close()

# =========================== Insert Calendar Events ===========================
def insert_calendar_events():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Inserting calendar events...")
    
    # Get all course IDs
    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    # Event types with corresponding prefixes/formats
    event_types = [
        {"type": "Lecture", "data": "Regularly weekly lecture covering key course topics."},
        {"type": "Tutorial", "data": "Short assessment to test knowledge of recent material."},
        {"type": "Midterm Exam", "data": "Major Examination covering all material up to this point."},
        {"type": "Final Exam", "data": "Final exam covering all material in the course."},
        {"type": "Project Presentation", "data": "Presentation of group project."},
        {"type": "Guest Lecture", "data": "Special guest lecture on a relevant topic."},
        {"type": "Office Hours", "data": "Time for students to meet with the lecturer."},
        {"type": "Assignment Due Date", "data": "Due date for assignments."}
    ]


    # Generate dates in the current academic term
    term_start = datetime(2025,1,20)
    term_end = datetime(2025,5,15)

    for cid in tqdm(courses):
        # Each course gets 5-15 calendar events
        for i in range(random.randint(5, 15)):
            event = random.choice(event_types)

            event_name = f"{event['type']}: {fake.catch_phrase()}"

            days_range= (term_end - term_start).days
            random_day =random.randint(0, days_range)
            event_date = term_start + timedelta(days=random_day)

            event_data = f"{event['data']} Course ID: {cid}."

            cursor.execute("""INSERT INTO CalendarEvent (data, calname, event_date, cid) VALUES (%s, %s, %s, %s)""",
                           (event_data, event_name, event_date, cid))
            
    conn.commit()
    cursor.close()
    conn.close()
    print("Calendar events inserted successfully.")

# 
def insert_section_items():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Creating section items...")

    # Get all section IDs
    cursor.execute("SELECT secid FROM Section")
    sections = [row['secid'] for row in cursor.fetchall()]
    
    # Define prefixes and suffixes for content items
    doc_prefixes = ["Lecture Notes on", "Guide to", "Introduction to", "Summary of", 
                   "Research Paper:", "Workshop on", "Study Materials for", "Handbook of"]
    
    doc_suffixes = ["Core Concepts", "Practical Applications", "Theoretical Foundations", 
                   "Common Problems", "Key Techniques", "Essential Principles", 
                   "Historical Overview", "Modern Approaches", "Best Practices"]
    
    slide_prefixes = ["Week", "Lecture", "Tutorial", "Module", "Session", "Class", "Unit", "Workshop"]
    
    slide_suffixes = ["Overview", "Introduction", "Key Concepts", "Advanced Topics", 
                     "Review", "Case Study", "Practice Problems", "Discussion Points"]
    
    link_prefixes = ["Resource:", "External Link:", "Website:", "Reference:", "Tutorial:", 
                    "Video:", "Tool:", "Article:"]
    
    link_suffixes = ["Additional Reading", "Interactive Demo", "Practice Exercise", 
                    "Visualization", "Reference Implementation", "Documentation", 
                    "Research Paper", "Industry Example"]
    
    item_types = ['document', 'link', 'lecture_slide']

    for secid in tqdm(sections):
        for i in range(random.randint(2, 5)):
            item_type = random.choice(item_types)
            
            # Generate a name appropriate for the content type
            if item_type == 'document':
                prefix = random.choice(doc_prefixes)
                suffix = random.choice(doc_suffixes)
                item_name = f"{prefix} {suffix}"
                file_path = f"/files/documents/{suffix.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.pdf"
            
            elif item_type == 'lecture_slide':
                prefix = random.choice(slide_prefixes)
                suffix = random.choice(slide_suffixes)
                item_name = f"{prefix} {random.randint(1, 12)}: {suffix}"
                file_path = f"/files/slides/{prefix.lower()}_{suffix.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.pptx"
            
            elif item_type == 'link':
                prefix = random.choice(link_prefixes)
                suffix = random.choice(link_suffixes)
                item_name = f"{prefix} {suffix}"
                link_url = f"https://{fake.domain_name()}/{suffix.lower().replace(' ', '-')}"
            
            # Insert the section item
            cursor.execute("INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, %s)",
                          (item_name, secid, item_type))
            
            item_id = cursor.lastrowid

            # Create appropriate type-specific record
            if item_type == 'document':
                cursor.execute("INSERT INTO Document (docid, docname, file_path) VALUES (%s, %s, %s)", 
                              (item_id, item_name, file_path))
            
            elif item_type == 'link':
                cursor.execute("INSERT INTO Link (linkid, linkname, hyplink) VALUES (%s, %s, %s)", 
                              (item_id, item_name, link_url))
            
            elif item_type == 'lecture_slide':
                cursor.execute("INSERT INTO LectureSlide (lsid, lsname, file_path) VALUES (%s, %s, %s)", 
                              (item_id, item_name, file_path))

    conn.commit()
    cursor.close()
    conn.close()
    print("Section items inserted successfully.")

# =========================== Ensure Popular Courses ===========================
def ensure_popular_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Ensuring courses have 50+ students...")

    # Get students
    cursor.execute("SELECT sid FROM Student LIMIT 10000")
    students = [row['sid'] for row in cursor.fetchall()]


    # Get courses with fewer than 50 students
    cursor.execute("""
        SELECT c.cid, COUNT(sc.sid) as count
        FROM Course c
        LEFT JOIN StudentCourse sc ON c.cid = sc.cid
        GROUP BY c.cid
        HAVING COUNT(sc.sid) < 50
        LIMIT 20
""")
    
    courses = cursor.fetchall()

    for course in tqdm(courses):
        cid = course['cid']
        needed = 50 - course['count']

        # Find students not in this course
        cursor.execute("SELECT sid FROM StudentCourse WHERE cid = %s", (cid,))
        existing = {row['sid'] for row in cursor.fetchall()}

        avaliable = [s for s in students if s not in existing]
        to_add = min(needed, len(avaliable))

        for sid in random.sample(avaliable, to_add):
            cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))

    conn.commit()
    cursor.close()
    conn.close()
    print("Course enrollment adjusted successfully.")




# =========================== Insert Student Replies Function ===========================
def insert_student_replies():
    conn = get_db_connection()
    cursor = conn.cursor()
    print("Inserting student replies...")

    # Get discussion threads
    cursor.execute("SELECT dtid FROM DiscussionThread LIMIT 5000")
    threads = [row['dtid'] for row in cursor.fetchall()]
    
    # Get student IDs
    cursor.execute("SELECT sid FROM Student LIMIT 10000")
    students = [row['sid'] for row in cursor.fetchall()]
    
    if not threads:
        print("No discussion threads found. Skipping student replies.")
        return
        
    # Create a tracking set to avoid duplicates
    reply_pairs = set()
    
    # Insert approximately 20,000 student replies
    for i in tqdm(range(20000)):
        dtid = random.choice(threads)
        sid = random.choice(students)
        
        # Check if this pair already exists
        pair = (sid, dtid)
        if pair in reply_pairs:
            continue
            
        reply_pairs.add(pair)
        
        try:
            cursor.execute("INSERT INTO StudentReply (sid, dtid) VALUES (%s, %s)", 
                          (sid, dtid))
            # Commit every 1000 insertions
            if i % 1000 == 0:
                conn.commit()
        except pymysql.err.IntegrityError as e:
            # Skip duplicates silently
            continue
    
    conn.commit()
    print(f"Inserted {len(reply_pairs)} student replies.")
    cursor.close()
    conn.close()



def update_course_participants():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print("Updating course participant counts...")
    
    try:
        # Update participants field based on actual enrollments
        cursor.execute("""
            UPDATE Course c
            SET participants = (
                SELECT COUNT(sc.sid)
                FROM StudentCourse sc
                WHERE sc.cid = c.cid
            )
        """)
        
        rows_updated = cursor.rowcount
        conn.commit()
        print(f"Updated participant counts for {rows_updated} courses.")
    except Exception as e:
        print(f"Error updating course participants: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    # Base data
    insert_students(NUM_STUDENTS)
    insert_lecturers(NUM_LECTURERS)
    insert_admins(NUM_ADMINS)
    
    # Courses and their components
    insert_courses(NUM_COURSES)
    insert_sections()
    
    # Relationships
    enroll_students()
    assign_lecturers_to_courses()
    
    # Course content
    insert_section_items()
    insert_assignments(NUM_ASSIGNMENTS)
    
    # Additional features
    insert_discussion_forums()
    insert_discussion_threads()
    insert_student_replies()
    insert_calendar_events()
    
    # Assignment-related data
    insert_assignment_submissions()
    link_assignments_to_calendar_events()
    update_student_grades()
    
    # Finalization and constraint verification
    verify_enrollment_constraints()  # Add this new function call
    ensure_popular_courses()
    update_course_participants()

    print("Data generation completed!")
