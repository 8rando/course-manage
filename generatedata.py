import random
import pymysql
from faker import Faker
from tqdm import  tqdm
from config import get_db_connection
from datetime import  datetime
fake = Faker()

NUM_STUDENTS = 200  #200000
NUM_LECTURERS = 20 #2000
NUM_COURSES = 201
NUM_ASSIGNMENTS = 500
NUM_ADMINS = 10
NUM_MAINTAINERS = 10

# =========================== Insert Students ===========================


def insert_students(NUM_STUDENTS):
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Inserting {NUM_STUDENTS} students...")

    for i in tqdm(range(NUM_STUDENTS)):
        fname = fake.first_name()
        lname = fake.last_name()
        password = "password123"

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
        password = "password123"

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
        password = "password123"

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

    course_names = [f"{fake.word().capitalize()} {fake.word().capitalize()}" for _ in range(NUM_COURSES)]

    for cname in tqdm(course_names):
        cursor.execute('INSERT INTO Course (cname) VALUES (%s)', (cname,))

    conn.commit()
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
        for _ in range(random.randint(2,5)): # Each course 2-5 sections
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

    for sid in tqdm(students):
        num_courses = random.randint(3, 6)  # Each student takes 3-6 courses

        # Create a pool of available courses for this student
        available_courses = [(sid, cid) for cid in courses if (sid, cid) not in enrolled_pairs]

        # If we have enough available courses, sample from them
        if len(available_courses) >= num_courses:
            selected_courses = random.sample(available_courses, num_courses)

            for sid, cid in selected_courses:
                try:
                    cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
                    enrolled_pairs.add((sid, cid))
                except pymysql.err.IntegrityError as e:
                    print(f"Warning: Could not enroll student {sid} in course {cid}: {e}")
        else:
            # If not enough courses available, add as many as we can
            for sid, cid in available_courses:
                try:
                    cursor.execute("INSERT INTO StudentCourse (sid, cid) VALUES (%s, %s)", (sid, cid))
                    enrolled_pairs.add((sid, cid))
                except pymysql.err.IntegrityError as e:
                    print(f"Warning: Could not enroll student {sid} in course {cid}: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Students enrolled successfully.")


# =========================== Assign Lecturers to Courses ===========================

def assign_lecturers_to_courses():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Assigning lecturers to courses...")

    # Get valid lecturer IDs
    cursor.execute("SELECT lid FROM Lecturer")
    lecturers = [row['lid'] for row in cursor.fetchall()]

    if not lecturers:
        print("Error: No lecturers found in the database. Ensure lecturers are inserted before running this script.")
        conn.close()
        return

    # Get valid course IDs
    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    if not courses:
        print("Error: No courses found in the database.")
        conn.close()
        return

    assigned_pairs = set()

    for i, cid in enumerate(tqdm(courses)):
        lid = lecturers[i % len(lecturers)]  # Assign lecturers round-robin
        assigned_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        pair = (lid, cid)
        if pair not in assigned_pairs:
            assigned_pairs.add(pair)
            cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)",
                           (lid, cid, assigned_date))

    conn.commit()
    cursor.close()
    conn.close()
    print("Lecturers assigned successfully.")

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

# =========================== Insert Calendar Events ===========================
def insert_calendar_events():
    conn = get_db_connection()
    cursor = conn.cursor()

    print("Inserting calendar events...")
    
    # Get all course IDs
    cursor.execute("SELECT cid FROM Course")
    courses = [row['cid'] for row in cursor.fetchall()]

    for cid in tqdm(courses):
        # Each course gets 3-5 calendar events
        for i in range(random.randint(3, 5)):
            event_name = fake.bs()
            event_date = fake.date_between(start_date='-30d', end_date='+60d')
            event_data = fake.paragraph()

            cursor.execute("INSERT INTO CalendarEvent (data, calname, event_date, cid) VALUES (%s, %s, %s, %s)",
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
    sections= [row['secid'] for row in cursor.fetchall()]
    
    item_types = ['document', 'link', 'lecture_slide']

    for secid in tqdm(sections):

        for i in range(random.randint(2,5)):
            item_name = fake.catch_phrase()
            item_type = random.choice(item_types)

            cursor.execute("INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, %s)",
                           (item_name, secid, item_type))
            
            item_id = cursor.lastrowid

            # Create appropriate type-specific record
            if item_type == 'document':
                file_path = f"/files/documents/{fake.file_name(extension='pdf')}"
                cursor.execute("INSERT INTO Document (docid, docname, file_path) VALUES (%s, %s, %s)", (item_id, item_name, file_path))

            elif item_type == 'link':
                link_url = fake.url()
                cursor.execute("INSERT INTO Link (linkid, linkname, hyplink) VALUES (%s, %s, %s)", (item_id, item_name, link_url))
            elif item_type == 'lecture_slide':
                file_path = f"/files/slides/{fake.file_name(extension='pptx')}"
                cursor.execute("INSERT INTO LectureSlide (lsid, lsname, file_path) VALUES (%s, %s, %s)", (item_id, item_name, file_path))

    conn.commit()
    cursor.close()
    conn.close()
    print("Section items inserted successfully.")

#
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
    insert_section_items()  # Fixed function
    insert_assignments(NUM_ASSIGNMENTS)
    
    # Additional features
    insert_discussion_forums()
    insert_discussion_threads()
    insert_calendar_events()
    
    # Finalization
    insert_assignment_submissions()
    ensure_popular_courses()
    

    print("Data generation completed!")