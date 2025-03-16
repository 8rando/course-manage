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

# =========================== Insert Maintainers ===========================

# def insert_maintainers(NUM_MAINTAINERS):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     print(f"Inserting {NUM_MAINTAINERS} maintainers...")

#     for _ in tqdm(range(NUM_MAINTAINERS)):
#         fname = fake.first_name()
#         lname = fake.last_name()
#         password = "password123"

#         cursor.execute("INSERT INTO Account (password, type, fname, lname) VALUES (%s, 'admin', %s, %s)",
#                        (password, fname, lname))
#         maintainer_id = cursor.lastrowid

#         cursor.execute("INSERT INTO Maintainer (cmid) VALUES (%s)", (maintainer_id,))

#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("Maintainers inserted successfully.")

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


# def assign_lecturers_to_courses():
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     print("Assigning lecturers to courses...")

#     cursor.execute("SELECT lid FROM Lecturer")
#     lecturers = [row[0] for row in cursor.fetchall()]

#     cursor.execute("SELECT cid FROM Course")
#     courses = [row[0] for row in cursor.fetchall()]

#     # Clear existing associations to avoid conflicts
#     try:
#         cursor.execute("DELETE FROM LecturerCourse")
#         print("Cleared existing lecturer-course assignments.")
#     except pymysql.MySQLError as e:
#         print(f"Warning: Could not clear existing assignments: {e}")

#     # Create a set to track already assigned combinations
#     assigned_pairs = set()

#     for i, cid in enumerate(tqdm(courses)):
#         # Rotate through lecturers but ensure unique combinations
#         for attempt in range(len(lecturers)):
#             lid = lecturers[(i + attempt) % len(lecturers)]
#             pair = (lid, cid)

#             if pair not in assigned_pairs:
#                 assigned_pairs.add(pair)
#                 assigned_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#                 try:
#                     cursor.execute("INSERT INTO LecturerCourse (lid, cid, assigned_date) VALUES (%s, %s, %s)",
#                                    (lid, cid, assigned_date))
#                     break  # Successfully inserted, move to next course
#                 except pymysql.err.IntegrityError as e:
#                     print(f"Warning: Could not assign lecturer {lid} to course {cid}: {e}")
#                     continue  # Try another lecturer

#     conn.commit()
#     cursor.close()
#     conn.close()
#     print("Lecturers assigned successfully.")


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




if __name__ == '__main__':
    insert_students(NUM_STUDENTS)
    insert_lecturers(NUM_LECTURERS)
    insert_assignments(NUM_ASSIGNMENTS)
    insert_admins(NUM_ADMINS)
    # insert_maintainers(NUM_MAINTAINERS)
    insert_courses(NUM_COURSES)
    enroll_students()
    assign_lecturers_to_courses()
    insert_assignment_submissions()
    insert_sections()
    print("Data generation completed!")