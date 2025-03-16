-- Drop tables if they exist (in reverse order of dependencies)

DROP TABLE IF EXISTS StudentReply;

DROP TABLE IF EXISTS AssignmentCalendarEvent;

DROP TABLE IF EXISTS AssignmentSubmission;

DROP TABLE IF EXISTS Document;

DROP TABLE IF EXISTS LectureSlide;

DROP TABLE IF EXISTS Link;

DROP TABLE IF EXISTS Assignment;

DROP TABLE IF EXISTS SectionItem;

DROP TABLE IF EXISTS Section;

DROP TABLE IF EXISTS CalendarEvent;

DROP TABLE IF EXISTS DiscussionThread;

DROP TABLE IF EXISTS DiscussionForum;

DROP TABLE IF EXISTS StudentCourse;

DROP TABLE IF EXISTS LecturerCourse;

DROP TABLE IF EXISTS Course;

DROP TABLE IF EXISTS CourseMaintainer;

DROP TABLE IF EXISTS Student;

DROP TABLE IF EXISTS Lecturer;

DROP TABLE IF EXISTS Admin;

DROP TABLE IF EXISTS Account;



-- Create tables based on the provided schema

CREATE TABLE Account (

    aid INT AUTO_INCREMENT PRIMARY KEY,

    password VARCHAR(255) NOT NULL,

    type ENUM('admin', 'lecturer', 'student') NOT NULL,

    fname VARCHAR(100) NOT NULL,

    lname VARCHAR(100) NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



CREATE TABLE Admin (

    adid INT PRIMARY KEY,

    FOREIGN KEY (adid) REFERENCES Account(aid) ON DELETE CASCADE

);



CREATE TABLE Lecturer (

    lid INT PRIMARY KEY,

    FOREIGN KEY (lid) REFERENCES Account(aid) ON DELETE CASCADE

);



CREATE TABLE Student (

    sid INT PRIMARY KEY,

    grade DECIMAL(5,2) DEFAULT 0.0,

    FOREIGN KEY (sid) REFERENCES Account(aid) ON DELETE CASCADE

);



CREATE TABLE CourseMaintainer (

    cmid INT PRIMARY KEY,

    FOREIGN KEY (cmid) REFERENCES Account(aid) ON DELETE CASCADE

);



CREATE TABLE Course (

    cid INT AUTO_INCREMENT PRIMARY KEY,

    cname VARCHAR(255) NOT NULL,

    participants INT DEFAULT 0

);



-- Many-to-many relationship between students and courses

CREATE TABLE StudentCourse (

    sid INT,

    cid INT,

    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (sid, cid),

    FOREIGN KEY (sid) REFERENCES Student(sid) ON DELETE CASCADE,

    FOREIGN KEY (cid) REFERENCES Course(cid) ON DELETE CASCADE

);



-- One-to-many relationship between lecturers and courses

CREATE TABLE LecturerCourse (

    lid INT,

    cid INT,

    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (cid),  -- One lecturer per course

    FOREIGN KEY (lid) REFERENCES Lecturer(lid) ON DELETE CASCADE,

    FOREIGN KEY (cid) REFERENCES Course(cid) ON DELETE CASCADE

);



CREATE TABLE DiscussionForum (

    dfid INT AUTO_INCREMENT PRIMARY KEY,

    dfname VARCHAR(255) NOT NULL,

    numthread INT DEFAULT 0,

    cid INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cid) REFERENCES Course(cid) ON DELETE CASCADE

);



CREATE TABLE DiscussionThread (

    dtid INT AUTO_INCREMENT PRIMARY KEY,

    dtname VARCHAR(255) NOT NULL,

    dttext TEXT NOT NULL,

    dfid INT,

    aid INT,  -- Author of the thread

    parent_dtid INT NULL,  -- For replies to other threads (NULL if it's a top-level thread)

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (dfid) REFERENCES DiscussionForum(dfid) ON DELETE CASCADE,

    FOREIGN KEY (aid) REFERENCES Account(aid) ON DELETE CASCADE,

    FOREIGN KEY (parent_dtid) REFERENCES DiscussionThread(dtid) ON DELETE CASCADE

);



-- For tracking student replies specifically

CREATE TABLE StudentReply (

    replyid INT AUTO_INCREMENT PRIMARY KEY,

    sid INT,

    dtid INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (sid) REFERENCES Student(sid) ON DELETE CASCADE,

    FOREIGN KEY (dtid) REFERENCES DiscussionThread(dtid) ON DELETE CASCADE

);



CREATE TABLE CalendarEvent (

    evid INT AUTO_INCREMENT PRIMARY KEY,

    data TEXT NOT NULL,

    calname VARCHAR(255) NOT NULL,

    event_date DATE NOT NULL,

    cid INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cid) REFERENCES Course(cid) ON DELETE CASCADE

);



CREATE TABLE Section (

    secid INT AUTO_INCREMENT PRIMARY KEY,

    secname VARCHAR(255) NOT NULL,

    cid INT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (cid) REFERENCES Course(cid) ON DELETE CASCADE

);



CREATE TABLE SectionItem (

    itemid INT AUTO_INCREMENT PRIMARY KEY,

    itemname VARCHAR(255) NOT NULL,

    datecreated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    secid INT,

    type ENUM('link', 'document', 'lecture_slide', 'assignment') NOT NULL,

    FOREIGN KEY (secid) REFERENCES Section(secid) ON DELETE CASCADE

);



CREATE TABLE Assignment (

    asid INT PRIMARY KEY,

    submitbox TEXT,

    max_score DECIMAL(5,2) DEFAULT 100.0,

    due_date DATE,

    FOREIGN KEY (asid) REFERENCES SectionItem(itemid) ON DELETE CASCADE

);



-- Relationship between Assignment and CalendarEvent (due date)

CREATE TABLE AssignmentCalendarEvent (

    asid INT,

    evid INT,

    PRIMARY KEY (asid),

    FOREIGN KEY (asid) REFERENCES Assignment(asid) ON DELETE CASCADE,

    FOREIGN KEY (evid) REFERENCES CalendarEvent(evid) ON DELETE CASCADE

);



CREATE TABLE Link (

    linkid INT PRIMARY KEY,

    hyplink TEXT NOT NULL,

    linkname VARCHAR(255) NOT NULL,

    FOREIGN KEY (linkid) REFERENCES SectionItem(itemid) ON DELETE CASCADE

);



CREATE TABLE Document (

    docid INT PRIMARY KEY,

    docname VARCHAR(255) NOT NULL,

    file_path VARCHAR(255) NOT NULL,

    FOREIGN KEY (docid) REFERENCES SectionItem(itemid) ON DELETE CASCADE

);



CREATE TABLE LectureSlide (

    lsid INT PRIMARY KEY,

    lsname VARCHAR(255) NOT NULL,

    file_path VARCHAR(255) NOT NULL,

    FOREIGN KEY (lsid) REFERENCES SectionItem(itemid) ON DELETE CASCADE

);



-- Additional table for submission grades

CREATE TABLE AssignmentSubmission (

    submission_id INT AUTO_INCREMENT PRIMARY KEY,

    asid INT,

    sid INT,

    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    file_path VARCHAR(255),

    grade DECIMAL(5,2) DEFAULT NULL,

    FOREIGN KEY (asid) REFERENCES Assignment(asid) ON DELETE CASCADE,

    FOREIGN KEY (sid) REFERENCES Student(sid) ON DELETE CASCADE

);



-- Create views for reporting requirements

-- View 1: Courses with 50 or more students

CREATE VIEW CoursesWith50OrMoreStudents AS

SELECT c.cid, c.cname, COUNT(sc.sid) AS student_count

FROM Course c

JOIN StudentCourse sc ON c.cid = sc.cid

GROUP BY c.cid, c.cname

HAVING COUNT(sc.sid) >= 50;



-- View 2: Students taking 5 or more courses

CREATE VIEW StudentsWith5OrMoreCourses AS

SELECT s.sid, a.fname, a.lname, COUNT(sc.cid) AS course_count

FROM Student s

JOIN Account a ON s.sid = a.aid

JOIN StudentCourse sc ON s.sid = sc.sid

GROUP BY s.sid, a.fname, a.lname

HAVING COUNT(sc.cid) >= 5;



-- View 3: Lecturers teaching 3 or more courses

CREATE VIEW LecturersWith3OrMoreCourses AS

SELECT l.lid, a.fname, a.lname, COUNT(lc.cid) AS course_count

FROM Lecturer l

JOIN Account a ON l.lid = a.aid

JOIN LecturerCourse lc ON l.lid = lc.lid

GROUP BY l.lid, a.fname, a.lname

HAVING COUNT(lc.cid) >= 3;



-- View 4: Top 10 most enrolled courses

CREATE VIEW Top10MostEnrolledCourses AS

SELECT c.cid, c.cname, COUNT(sc.sid) AS enrollment_count

FROM Course c

JOIN StudentCourse sc ON c.cid = sc.cid

GROUP BY c.cid, c.cname

ORDER BY COUNT(sc.sid) DESC

LIMIT 10;



-- View 5: Top 10 students with highest overall averages

CREATE VIEW Top10StudentsWithHighestAverages AS

SELECT s.sid, a.fname, a.lname, AVG(asm.grade) AS average_grade

FROM Student s

JOIN Account a ON s.sid = a.aid

JOIN AssignmentSubmission asm ON s.sid = asm.sid

GROUP BY s.sid, a.fname, a.lname

HAVING COUNT(DISTINCT asm.asid) > 0  -- Only include students who submitted assignments

ORDER BY AVG(asm.grade) DESC

LIMIT 10;