document.addEventListener('DOMContentLoaded', () => {
    // Load courses
    loadCourses();
    
    // Load student-specific data
    if (window.auth && window.auth.currentUser && window.auth.currentUser.type === 'student') {
        loadTodayEvents();
        loadUpcomingAssignments();
    }
    
    // Setup admin form listeners
    const createCourseForm = document.getElementById('create-course-form');
    if (createCourseForm) {
        createCourseForm.addEventListener('submit', handleCreateCourse);
    }
    
    const assignLecturerForm = document.getElementById('assign-lecturer-form');
    if (assignLecturerForm) {
        assignLecturerForm.addEventListener('submit', handleAssignLecturer);
    }
});

// Load user's courses
async function loadCourses() {
    const coursesContainer = document.getElementById('courses-container');
    const loadingElement = document.getElementById('courses-loading');
    
    if (!coursesContainer || !window.auth || !window.auth.currentUser) return;
    
    try {
        loadingElement.classList.remove('hidden');
        coursesContainer.innerHTML = '';
        
        const userType = window.auth.currentUser.type;
        const userId = window.auth.currentUser.id;
        
        const response = await fetch(`${API_URL}/courses?user_type=${userType}&user_id=${userId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load courses');
        }
        
        const courses = await response.json();
        
        if (courses.length === 0) {
            coursesContainer.innerHTML = '<div class="col-12"><p class="text-muted">No courses found. Enroll in a course or contact an administrator.</p></div>';
        } else {
            // Display up to 3 courses on dashboard
            const displayCourses = courses.slice(0, 3);
            
            displayCourses.forEach(course => {
                const courseCard = `
                    <div class="col-md-4 mb-3">
                        <div class="card course-card">
                            <div class="card-body">
                                <h5 class="card-title">${course.cname}</h5>
                                <p class="card-text">Course ID: ${course.cid}</p>
                                <a href="courses.html?course_id=${course.cid}" class="btn btn-primary">View Course</a>
                            </div>
                        </div>
                    </div>
                `;
                coursesContainer.insertAdjacentHTML('beforeend', courseCard);
            });
        }
    } catch (error) {
        console.error('Error loading courses:', error);
        window.auth.showAlert('Failed to load courses. Please try again later.', 'danger');
        coursesContainer.innerHTML = '<div class="col-12"><p class="text-danger">Failed to load courses. Please try again later.</p></div>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Load today's events for students
async function loadTodayEvents() {
    const eventsContainer = document.getElementById('events-container');
    const loadingElement = document.getElementById('events-loading');
    
    if (!eventsContainer || !window.auth || !window.auth.currentUser) return;
    
    try {
        loadingElement.classList.remove('hidden');
        eventsContainer.innerHTML = '';
        
        const today = new Date().toISOString().split('T')[0]; // YYYY-MM-DD format
        const studentId = window.auth.currentUser.id;
        
        const response = await fetch(`${API_URL}/calendar_events?date=${today}&student_id=${studentId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load events');
        }
        
        const events = await response.json();
        
        if (events.length === 0) {
            eventsContainer.innerHTML = '<p class="text-muted">No events scheduled for today.</p>';
        } else {
            events.forEach(event => {
                const eventCard = `
                    <div class="calendar-event">
                        <h5>${event.calname}</h5>
                        <p>${event.data || 'No description provided'}</p>
                        <small class="text-muted">Course ID: ${event.cid}</small>
                    </div>
                `;
                eventsContainer.insertAdjacentHTML('beforeend', eventCard);
            });
        }
    } catch (error) {
        console.error('Error loading events:', error);
        eventsContainer.innerHTML = '<p class="text-danger">Failed to load events. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Load upcoming assignments for students
async function loadUpcomingAssignments() {
    const assignmentsContainer = document.getElementById('assignments-container');
    const loadingElement = document.getElementById('assignments-loading');
    
    if (!assignmentsContainer || !window.auth || !window.auth.currentUser) return;
    
    try {
        loadingElement.classList.remove('hidden');
        assignmentsContainer.innerHTML = '';
        
        // This is a placeholder - we would need to extend the API to get assignments across all courses
        // For now, we'll just show a message
        assignmentsContainer.innerHTML = '<p class="text-muted">Visit your individual courses to view assignments.</p>';
        
    } catch (error) {
        console.error('Error loading assignments:', error);
        assignmentsContainer.innerHTML = '<p class="text-danger">Failed to load assignments. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Handle course creation (admin only)
async function handleCreateCourse(event) {
    event.preventDefault();
    
    if (!window.auth || !window.auth.currentUser || window.auth.currentUser.type !== 'admin') {
        window.auth.showAlert('Only admins can create courses.', 'danger');
        return;
    }
    
    const courseName = document.getElementById('course-name').value;
    
    try {
        const response = await fetch(`${API_URL}/courses`, {
            method: 'POST',
            headers: window.auth.getAuthHeaders(),
            body: JSON.stringify({
                cname: courseName,
                user_type: 'admin'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Course created successfully!', 'success');
            document.getElementById('course-name').value = '';
            // Reload courses
            loadCourses();
        } else {
            window.auth.showAlert(data.error || 'Failed to create course.', 'danger');
        }
    } catch (error) {
        console.error('Error creating course:', error);
        window.auth.showAlert('An error occurred while creating the course.', 'danger');
    }
}

// Handle lecturer assignment (admin only)
async function handleAssignLecturer(event) {
    event.preventDefault();
    
    if (!window.auth || !window.auth.currentUser || window.auth.currentUser.type !== 'admin') {
        window.auth.showAlert('Only admins can assign lecturers.', 'danger');
        return;
    }
    
    const lecturerId = document.getElementById('lecturer-id').value;
    const courseId = document.getElementById('course-id').value;
    
    try {
        const response = await fetch(`${API_URL}/assign_lecturer`, {
            method: 'POST',
            headers: window.auth.getAuthHeaders(),
            body: JSON.stringify({
                lid: lecturerId,
                cid: courseId,
                user_type: 'admin'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Lecturer assigned successfully!', 'success');
            document.getElementById('lecturer-id').value = '';
            document.getElementById('course-id').value = '';
        } else {
            window.auth.showAlert(data.error || 'Failed to assign lecturer.', 'danger');
        }
    } catch (error) {
        console.error('Error assigning lecturer:', error);
        window.auth.showAlert('An error occurred while assigning the lecturer.', 'danger');
    }
}