import os
import sys

def generate_sql():
    """
    Generate SQL statements from the data generation functions in generatedata.py
    instead of executing them directly.
    """
    sql_statements = []
    
    # Import constants from generatedata.py
    from generatedata import (
        NUM_STUDENTS, NUM_LECTURERS, NUM_COURSES, NUM_ASSIGNMENTS,
        NUM_ADMINS, NUM_MAINTAINERS, prefixes, suffixes
    )
    
    # Header
    sql_statements.append("-- Generated initialization data")
    sql_statements.append("-- This file was automatically generated from generatedata.py")
    sql_statements.append("\n")
    
    # Generate SQL for students
    sql_statements.append(f"-- Inserting {NUM_STUDENTS} students")
    for i in range(NUM_STUDENTS):
        # We'll use a much smaller sample size for the SQL output
        if i >= 500:  # Limit to 500 students for SQL file
            sql_statements.append(f"-- Remaining {NUM_STUDENTS - 500} students omitted for file size")
            break
            
        # Generate a student with ID offset to avoid conflicts
        student_id = 10000 + i
        sql_statements.append(f"INSERT INTO Account (aid, password, type, fname, lname) VALUES ({student_id}, 'password123', 'student', CONCAT('Student', {i}), CONCAT('Last', {i}));")
        sql_statements.append(f"INSERT INTO Student (sid) VALUES ({student_id});")
    
    # Generate SQL for lecturers (similar pattern)
    sql_statements.append(f"\n-- Inserting {NUM_LECTURERS} lecturers")
    for i in range(min(100, NUM_LECTURERS)):  # Limit to 100 for SQL file
        lecturer_id = 20000 + i
        sql_statements.append(f"INSERT INTO Account (aid, password, type, fname, lname) VALUES ({lecturer_id}, 'password123', 'lecturer', CONCAT('Lecturer', {i}), CONCAT('Prof', {i}));")
        sql_statements.append(f"INSERT INTO Lecturer (lid) VALUES ({lecturer_id});")
    
    # Generate SQL for admins
    sql_statements.append(f"\n-- Inserting {NUM_ADMINS} admins")
    for i in range(NUM_ADMINS):
        admin_id = 30000 + i
        sql_statements.append(f"INSERT INTO Account (aid, password, type, fname, lname) VALUES ({admin_id}, 'password123', 'admin', CONCAT('Admin', {i}), CONCAT('Manager', {i}));")
        sql_statements.append(f"INSERT INTO Admin (adid) VALUES ({admin_id});")
    
    # Generate SQL for courses
    sql_statements.append(f"\n-- Inserting {NUM_COURSES} courses")
    for i in range(min(100, NUM_COURSES)):  # Limit to 100 for SQL file
        prefix = prefixes[i % len(prefixes)]
        suffix = suffixes[i % len(suffixes)]
        course_name = f"{prefix} {suffix} {i}"
        sql_statements.append(f"INSERT INTO Course (cname) VALUES ('{course_name}');")
    
    # Add sections for each course
    sql_statements.append(f"\n-- Inserting sections for courses")
    sql_statements.append("INSERT INTO Section (secname, cid) SELECT CONCAT('Section A: ', cid), cid FROM Course;")
    sql_statements.append("INSERT INTO Section (secname, cid) SELECT CONCAT('Section B: ', cid), cid FROM Course;")
    
    # Add enrollments
    sql_statements.append(f"\n-- Enrolling students in courses")
    sql_statements.append("INSERT INTO StudentCourse (sid, cid) SELECT s.sid, c.cid FROM Student s JOIN Course c WHERE s.sid % 5 = c.cid % 5 LIMIT 1000;")
    
    # Assign lecturers to courses
    sql_statements.append(f"\n-- Assigning lecturers to courses")
    sql_statements.append("INSERT INTO LecturerCourse (lid, cid, assigned_date) SELECT l.lid, c.cid, NOW() FROM Lecturer l JOIN Course c WHERE l.lid % 3 = c.cid % 3 LIMIT 500;")
    
    # Create section items
    sql_statements.append(f"\n-- Creating section items")
    sql_statements.append("INSERT INTO SectionItem (itemname, secid, type) SELECT CONCAT('Lecture Notes: ', s.secname), s.secid, 'document' FROM Section s LIMIT 200;")
    
    # Create documents for section items
    sql_statements.append(f"\n-- Creating documents")
    sql_statements.append("INSERT INTO Document (docid, docname, file_path) SELECT si.itemid, si.itemname, CONCAT('/files/doc_', si.itemid, '.pdf') FROM SectionItem si WHERE si.type = 'document';")
    
    # Create assignments
    sql_statements.append(f"\n-- Creating assignments")
    sql_statements.append("INSERT INTO SectionItem (itemname, secid, type) SELECT CONCAT('Assignment: ', s.secname), s.secid, 'assignment' FROM Section s LIMIT 50;")
    sql_statements.append("INSERT INTO Assignment (asid, submitbox, max_score, due_date) SELECT si.itemid, '', 100.0, DATE_ADD(NOW(), INTERVAL RAND()*30 DAY) FROM SectionItem si WHERE si.type = 'assignment';")
    
    # Create forums
    sql_statements.append(f"\n-- Creating discussion forums")
    sql_statements.append("INSERT INTO DiscussionForum (dfname, cid) SELECT CONCAT('Forum for ', c.cname), c.cid FROM Course c LIMIT 100;")
    
    # Create discussion threads
    sql_statements.append(f"\n-- Creating discussion threads")
    sql_statements.append("INSERT INTO DiscussionThread (dtname, dttext, dfid, aid, parent_dtid) SELECT CONCAT('Thread: ', df.dfname), 'Initial post content', df.dfid, a.aid, NULL FROM DiscussionForum df JOIN Account a WHERE a.type = 'student' LIMIT 200;")
    
    # Create calendar events
    sql_statements.append(f"\n-- Creating calendar events")
    sql_statements.append("INSERT INTO CalendarEvent (data, calname, event_date, cid) SELECT 'Event data', CONCAT('Lecture: ', c.cname), DATE_ADD(NOW(), INTERVAL RAND()*60 DAY), c.cid FROM Course c LIMIT 100;")
    
    return "\n".join(sql_statements)

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "init-data.sql"
    
    # Generate SQL and write to file
    sql_content = generate_sql()
    
    with open(output_file, 'w') as f:
        f.write(sql_content)
    
    print(f"SQL data written to {output_file}")
