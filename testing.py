import random
from datetime import datetime
from config import get_db_connection
from faker import Faker

fake = Faker()

def check_dependencies():
    """Check if prerequisite tables have data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) as count FROM Course")
        course_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Section")
        section_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Account")
        account_count = cursor.fetchone()['count']
        
        print(f"Found {course_count} courses, {section_count} sections, and {account_count} accounts")
        
        if course_count == 0 or section_count == 0 or account_count == 0:
            print("ERROR: Missing prerequisite data. Please run generatedata.py first.")
            return False
        return True
    finally:
        cursor.close()
        conn.close()

def create_sections():
    """Create sections for courses"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get courses that don't have sections yet
        cursor.execute("""
            SELECT c.cid FROM Course c
            LEFT JOIN Section s ON c.cid = s.cid
            WHERE s.secid IS NULL
        """)
        courses = [row['cid'] for row in cursor.fetchall()]
        
        if not courses:
            print("All courses already have sections")
            return
            
        print(f"Creating sections for {len(courses)} courses...")
        
        for cid in courses:
            # Create 2-4 sections per course
            for i in range(random.randint(2, 4)):
                section_name = f"Section {i+1}: {fake.catch_phrase()}"
                cursor.execute("INSERT INTO Section (secname, cid) VALUES (%s, %s)", 
                              (section_name, cid))
                
        conn.commit()
        print(f"Created sections successfully")
    finally:
        cursor.close()
        conn.close()

def create_section_items():
    """Create section items and their type-specific records"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all sections
        cursor.execute("SELECT secid FROM Section")
        sections = cursor.fetchall()
        
        if not sections:
            print("No sections found")
            return
            
        print(f"Creating section items for {len(sections)} sections...")
        
        for section in sections:
            secid = section['secid']
            
            # Create 3-5 items per section
            for _ in range(random.randint(3, 5)):
                item_name = fake.catch_phrase()
                item_type = random.choice(['document', 'link', 'lecture_slide'])
                
                cursor.execute(
                    "INSERT INTO SectionItem (itemname, secid, type) VALUES (%s, %s, %s)",
                    (item_name, secid, item_type)
                )
                
                item_id = cursor.lastrowid
                
                # Create type-specific record
                if item_type == 'document':
                    file_path = f"/files/documents/{fake.file_name(extension='pdf')}"
                    cursor.execute(
                        "INSERT INTO Document (docid, docname, file_path) VALUES (%s, %s, %s)",
                        (item_id, item_name, file_path)
                    )
                    
                elif item_type == 'link':
                    link_url = fake.url()
                    cursor.execute(
                        "INSERT INTO Link (linkid, linkname, hyplink) VALUES (%s, %s, %s)",
                        (item_id, item_name, link_url)
                    )
                    
                elif item_type == 'lecture_slide':
                    file_path = f"/files/slides/{fake.file_name(extension='pptx')}"
                    cursor.execute(
                        "INSERT INTO LectureSlide (lsid, lsname, file_path) VALUES (%s, %s, %s)",
                        (item_id, item_name, file_path)
                    )
        
        conn.commit()
        print("Created section items successfully")
    finally:
        cursor.close()
        conn.close()

def create_forums_and_threads():
    """Create discussion forums and threads"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get courses that don't have forums
        cursor.execute("""
            SELECT c.cid FROM Course c
            LEFT JOIN DiscussionForum df ON c.cid = df.cid
            WHERE df.dfid IS NULL
            LIMIT 50
        """)
        courses = [row['cid'] for row in cursor.fetchall()]
        
        # Get accounts for thread authors
        cursor.execute("SELECT aid FROM Account LIMIT 100")
        accounts = [row['aid'] for row in cursor.fetchall()]
        
        if not courses or not accounts:
            print("No courses without forums or no accounts found")
            return
            
        print(f"Creating forums for {len(courses)} courses...")
        
        for cid in courses:
            # Create 1-3 forums per course
            for _ in range(random.randint(1, 3)):
                forum_name = f"Forum: {fake.bs()}"
                
                cursor.execute(
                    "INSERT INTO DiscussionForum (dfname, cid) VALUES (%s, %s)",
                    (forum_name, cid)
                )
                
                forum_id = cursor.lastrowid
                
                # Create 3-7 threads per forum
                for _ in range(random.randint(3, 7)):
                    thread_title = fake.sentence()
                    thread_text = fake.paragraph()
                    author_id = random.choice(accounts)
                    
                    cursor.execute(
                        "INSERT INTO DiscussionThread (dtname, dttext, dfid, aid, parent_dtid) VALUES (%s, %s, %s, %s, NULL)",
                        (thread_title, thread_text, forum_id, author_id)
                    )
                    
                    # Create some replies
                    thread_id = cursor.lastrowid
                    
                    # 30% chance of adding student replies
                    if random.random() < 0.3:
                        # Get some students
                        cursor.execute("SELECT sid FROM Student LIMIT 20")
                        students = [row['sid'] for row in cursor.fetchall()]
                        
                        if students:
                            for _ in range(random.randint(1, 3)):
                                student_id = random.choice(students)
                                
                                cursor.execute(
                                    "INSERT INTO StudentReply (sid, dtid) VALUES (%s, %s)",
                                    (student_id, thread_id)
                                )
        
        conn.commit()
        print("Created forums and threads successfully")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    if check_dependencies():
        create_sections()
        create_section_items()
        create_forums_and_threads()
        print("Successfully populated missing tables!")