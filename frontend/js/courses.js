// Global variables
let currentCourseId = null;

document.addEventListener('DOMContentLoaded', () => {
    // Check if we're in course management mode
    const urlParams = new URLSearchParams(window.location.search);
    const manageMode = urlParams.get('manage') === 'true';
    const specificCourseId = urlParams.get('course_id');
    
    if (manageMode) {
        document.getElementById('page-title').textContent = 'Manage Courses';
        document.getElementById('courses-subtitle').textContent = 'Create and manage course content';
    }
    
    // Load courses or specific course
    if (specificCourseId) {
        loadCourseDetails(specificCourseId);
    } else {
        loadCourses();
    }
    
    // Enroll form handler
    const enrollForm = document.getElementById('enroll-form');
    if (enrollForm) {
        enrollForm.addEventListener('submit', handleEnroll);
    }
    
    // Back to courses button
    const backButton = document.getElementById('back-to-courses');
    if (backButton) {
        backButton.addEventListener('click', () => {
            document.getElementById('course-details').classList.add('hidden');
            document.querySelector('.card').classList.remove('hidden');
        });
    }
    
    // Content type dropdown handler
    const contentTypeSelect = document.getElementById('content-type');
    if (contentTypeSelect) {
        contentTypeSelect.addEventListener('change', () => {
            const filePath = document.querySelector('.content-file-path');
            const link = document.querySelector('.content-link');
            
            if (contentTypeSelect.value === 'link') {
                filePath.classList.add('hidden');
                link.classList.remove('hidden');
            } else {
                filePath.classList.remove('hidden');
                link.classList.add('hidden');
            }
        });
    }
    
    // Add content form handler
    const addContentForm = document.getElementById('add-content-form');
    if (addContentForm) {
        addContentForm.addEventListener('submit', handleAddContent);
    }
    
    // Add event form handler
    const addEventForm = document.getElementById('add-event-form');
    if (addEventForm) {
        addEventForm.addEventListener('submit', handleAddEvent);
    }
    
    // Create assignment form handler
    const createAssignmentForm = document.getElementById('create-assignment-form');
    if (createAssignmentForm) {
        createAssignmentForm.addEventListener('submit', handleCreateAssignment);
    }
    
    // Create forum form handler
    const createForumForm = document.getElementById('create-forum-form');
    if (createForumForm) {
        createForumForm.addEventListener('submit', handleCreateForum);
    }
    
    // Create thread form handler
    const createThreadForm = document.getElementById('create-thread-form');
    if (createThreadForm) {
        createThreadForm.addEventListener('submit', handleCreateThread);
    }
    
    // Reply to thread form handler
    const replyThreadForm = document.getElementById('reply-thread-form');
    if (replyThreadForm) {
        replyThreadForm.addEventListener('submit', handleReplyThread);
    }
    
    // Submit assignment form handler
    const submitAssignmentForm = document.getElementById('submit-assignment-form');
    if (submitAssignmentForm) {
        submitAssignmentForm.addEventListener('submit', handleSubmitAssignment);
    }
});

// Load all courses
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
            courses.forEach(course => {
                const courseCard = `
                    <div class="col-md-4 mb-4">
                        <div class="card course-card h-100">
                            <div class="card-body d-flex flex-column">
                                <h5 class="card-title">${course.cname}</h5>
                                <p class="card-text">Course ID: ${course.cid}</p>
                                <button class="btn btn-primary mt-auto" onclick="loadCourseDetails(${course.cid})">View Course</button>
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

// Load specific course details
function loadCourseDetails(courseId) {
    currentCourseId = courseId;
    
    document.querySelector('.card').classList.add('hidden');
    const courseDetails = document.getElementById('course-details');
    courseDetails.classList.remove('hidden');
    
    // Update course name placeholder
    document.getElementById('course-detail-name').textContent = 'Loading course details...';
    
    // Load course content
    loadCourseContent(courseId);
    
    // Load assignments
    loadAssignments(courseId);
    
    // Load forums
    loadForums(courseId);
    
    // Load members
    loadCourseMembers(courseId);
}

// Load course content
async function loadCourseContent(courseId) {
    const contentContainer = document.getElementById('content-container');
    const loadingElement = document.getElementById('content-loading');
    
    if (!contentContainer) return;
    
    try {
        loadingElement.classList.remove('hidden');
        contentContainer.innerHTML = '';
        
        const response = await fetch(`${API_URL}/content?course_id=${courseId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load course content');
        }
        
        const content = await response.json();
        
        // Update course name if available
        if (content.length > 0 && content[0].course_name) {
            document.getElementById('course-detail-name').textContent = content[0].course_name;
        } else {
            document.getElementById('course-detail-name').textContent = `Course #${courseId}`;
        }
        
        if (content.length === 0) {
            contentContainer.innerHTML = '<p class="text-muted">No content available for this course.</p>';
        } else {
            let contentHTML = '<div class="list-group">';
            
            content.forEach(item => {
                let linkInfo = '';
                
                if (item.type === 'document' && item.document_path) {
                    linkInfo = `<small class="text-muted">Document: ${item.document_path}</small>`;
                } else if (item.type === 'lecture_slide' && item.slide_path) {
                    linkInfo = `<small class="text-muted">Slide: ${item.slide_path}</small>`;
                } else if (item.type === 'link' && item.link) {
                    linkInfo = `<a href="${item.link}" target="_blank" class="text-primary">External Link</a>`;
                }
                
                contentHTML += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${item.itemname}</h5>
                            <small class="text-muted">Item ID: ${item.itemid}</small>
                        </div>
                        <p class="mb-1">Type: ${item.type}</p>
                        ${linkInfo}
                    </div>
                `;
            });
            
            contentHTML += '</div>';
            contentContainer.innerHTML = contentHTML;
        }
    } catch (error) {
        console.error('Error loading course content:', error);
        contentContainer.innerHTML = '<p class="text-danger">Failed to load course content. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Load course assignments
async function loadAssignments(courseId) {
    const assignmentsContainer = document.getElementById('assignments-container');
    const loadingElement = document.getElementById('assignments-loading');
    
    if (!assignmentsContainer) return;
    
    try {
        loadingElement.classList.remove('hidden');
        assignmentsContainer.innerHTML = '';
        
        const response = await fetch(`${API_URL}/assignments?course_id=${courseId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load assignments');
        }
        
        const assignments = await response.json();
        
        if (assignments.length === 0) {
            assignmentsContainer.innerHTML = '<p class="text-muted">No assignments available for this course.</p>';
        } else {
            let assignmentsHTML = '<div class="list-group assignment-list">';
            
            assignments.forEach(assignment => {
                const dueDate = new Date(assignment.due_date);
                const formattedDate = dueDate.toLocaleString();
                
                assignmentsHTML += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${assignment.itemname}</h5>
                            <span class="badge bg-primary">Max: ${assignment.max_score} pts</span>
                        </div>
                        <p class="mb-1">Due: ${formattedDate}</p>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="submitAssignment(${assignment.asid})">
                                Submit Assignment
                            </button>
                        </div>
                    </div>
                `;
            });
            
            assignmentsHTML += '</div>';
            assignmentsContainer.innerHTML = assignmentsHTML;
        }
    } catch (error) {
        console.error('Error loading assignments:', error);
        assignmentsContainer.innerHTML = '<p class="text-danger">Failed to load assignments. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Load forums for a course
async function loadForums(courseId) {
    const forumsContainer = document.getElementById('forums-container');
    const loadingElement = document.getElementById('forums-loading');
    
    if (!forumsContainer) return;
    
    try {
        loadingElement.classList.remove('hidden');
        forumsContainer.innerHTML = '';
        
        const response = await fetch(`${API_URL}/forums?course_id=${courseId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load forums');
        }
        
        const forums = await response.json();
        
        if (forums.length === 0) {
            forumsContainer.innerHTML = '<p class="text-muted">No discussion forums available for this course.</p>';
        } else {
            let forumsHTML = '<div class="list-group">';
            
            forums.forEach(forum => {
                forumsHTML += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${forum.dfname}</h5>
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="loadThreads(${forum.dfid})">
                                View Discussions
                            </button>
                        </div>
                    </div>
                `;
            });
            
            forumsHTML += '</div>';
            forumsContainer.innerHTML = forumsHTML;
        }
    } catch (error) {
        console.error('Error loading forums:', error);
        forumsContainer.innerHTML = '<p class="text-danger">Failed to load forums. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Load threads for a forum
async function loadThreads(forumId) {
    const threadsContainer = document.getElementById('threads-container');
    const threadsSection = document.getElementById('threads-section');
    const forumsSection = document.getElementById('forums-section');
    const loadingElement = document.getElementById('threads-loading');
    
    if (!threadsContainer || !threadsSection || !forumsSection) return;
    
    try {
        // Show threads section, hide forums section
        forumsSection.classList.add('hidden');
        threadsSection.classList.remove('hidden');
        loadingElement.classList.remove('hidden');
        threadsContainer.innerHTML = '';
        
        // Store current forum ID for new thread creation
        threadsSection.dataset.forumId = forumId;
        
        const response = await fetch(`${API_URL}/threads?dfid=${forumId}`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load threads');
        }
        
        const threads = await response.json();
        
        if (threads.length === 0) {
            threadsContainer.innerHTML = '<p class="text-muted">No discussion threads found. Be the first to start a discussion!</p>';
        } else {
            // Group threads by parent/child relationship
            const parentThreads = threads.filter(thread => !thread.parent_dtid);
            let threadsHTML = '<div class="list-group">';
            
            parentThreads.forEach(thread => {
                const replies = threads.filter(reply => reply.parent_dtid === thread.dtid);
                const createdDate = new Date(thread.created_at).toLocaleString();
                
                threadsHTML += `
                    <div class="list-group-item">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${thread.dtname}</h5>
                            <small class="text-muted">${createdDate}</small>
                        </div>
                        <p class="mb-1">${thread.dttext}</p>
                        <div class="mt-2">
                            <button class="btn btn-sm btn-outline-primary" onclick="showReplyForm(${thread.dtid})">
                                Reply
                            </button>
                        </div>
                        
                        <!-- Replies Section -->
                        ${replies.length > 0 ? '<div class="replies-section mt-3 ms-4">' : ''}
                        ${replies.map(reply => {
                            const replyDate = new Date(reply.created_at).toLocaleString();
                            return `
                                <div class="reply-item mb-2 p-2 border-start border-3">
                                    <div class="d-flex justify-content-between">
                                        <small class="fw-bold">RE: #${reply.parent_dtid}</small>
                                        <small class="text-muted">${replyDate}</small>
                                    </div>
                                    <p class="mb-1">${reply.dttext}</p>
                                </div>
                            `;
                        }).join('')}
                        ${replies.length > 0 ? '</div>' : ''}
                    </div>
                `;
            });
            
            threadsHTML += '</div>';
            threadsContainer.innerHTML = threadsHTML;
        }
    } catch (error) {
        console.error('Error loading threads:', error);
        threadsContainer.innerHTML = '<p class="text-danger">Failed to load discussion threads. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Back to forums button handler
function backToForums() {
    const threadsSection = document.getElementById('threads-section');
    const forumsSection = document.getElementById('forums-section');
    
    if (threadsSection && forumsSection) {
        threadsSection.classList.add('hidden');
        forumsSection.classList.remove('hidden');
    }
}

// Load course members
async function loadCourseMembers(courseId) {
    const membersContainer = document.getElementById('members-container');
    const loadingElement = document.getElementById('members-loading');
    
    if (!membersContainer) return;
    
    try {
        loadingElement.classList.remove('hidden');
        membersContainer.innerHTML = '';
        
        const response = await fetch(`${API_URL}/course/${courseId}/members`, {
            headers: window.auth.getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Failed to load course members');
        }
        
        const members = await response.json();
        
        if (members.length === 0) {
            membersContainer.innerHTML = '<p class="text-muted">No members found for this course.</p>';
        } else {
            const students = members.filter(member => member.role === 'student');
            const lecturers = members.filter(member => member.role === 'lecturer');
            
            let membersHTML = '<div class="members-list">';
            
            // Lecturers section
            if (lecturers.length > 0) {
                membersHTML += '<h5 class="mt-3">Lecturers</h5><ul class="list-group">';
                lecturers.forEach(lecturer => {
                    membersHTML += `
                        <li class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <span>${lecturer.fname} ${lecturer.lname}</span>
                                <span class="badge bg-success">Lecturer</span>
                            </div>
                        </li>
                    `;
                });
                membersHTML += '</ul>';
            }
            
            // Students section
            if (students.length > 0) {
                membersHTML += '<h5 class="mt-3">Students</h5><ul class="list-group">';
                students.forEach(student => {
                    membersHTML += `
                        <li class="list-group-item">
                            <div class="d-flex w-100 justify-content-between">
                                <span>${student.fname} ${student.lname}</span>
                                <span class="badge bg-primary">Student</span>
                            </div>
                        </li>
                    `;
                });
                membersHTML += '</ul>';
            }
            
            membersHTML += '</div>';
            membersContainer.innerHTML = membersHTML;
        }
    } catch (error) {
        console.error('Error loading course members:', error);
        membersContainer.innerHTML = '<p class="text-danger">Failed to load course members. Please try again later.</p>';
    } finally {
        loadingElement.classList.add('hidden');
    }
}

// Submit assignment form
function submitAssignment(assignmentId) {
    const modal = document.getElementById('submit-assignment-modal');
    const form = document.getElementById('submit-assignment-form');
    
    if (modal && form) {
        form.reset();
        form.elements.asid.value = assignmentId;
        
        // Show the modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
}

// Show reply form for a thread
function showReplyForm(threadId) {
    const modal = document.getElementById('reply-thread-modal');
    const form = document.getElementById('reply-thread-form');
    
    if (modal && form) {
        form.reset();
        form.elements.dtid.value = threadId;
        
        // Show the modal
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }
}

// Handle enrollment form submission
async function handleEnroll(event) {
    event.preventDefault();
    
    const form = event.target;
    const courseId = form.elements.cid.value;
    const studentId = window.auth.currentUser.id;
    
    if (!courseId || !studentId) {
        window.auth.showAlert('Missing course ID or student ID', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/enroll`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                sid: studentId,
                cid: courseId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Successfully enrolled in course', 'success');
            loadCourses(); // Reload courses to show the new enrollment
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('enroll-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to enroll in course', 'danger');
        }
    } catch (error) {
        console.error('Error enrolling in course:', error);
        window.auth.showAlert('Failed to enroll in course. Please try again later.', 'danger');
    }
}

// Handle adding course content
async function handleAddContent(event) {
    event.preventDefault();
    
    const form = event.target;
    const itemname = form.elements.itemname.value;
    const contentType = form.elements.contentType.value;
    const filePath = form.elements.filePath?.value || '';
    const hyplink = form.elements.hyplink?.value || '';
    const sectionId = form.elements.secid.value || 1; // Default to section 1 if not specified
    
    try {
        const response = await fetch(`${API_URL}/content`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                itemname: itemname,
                secid: sectionId,
                type: contentType,
                file_path: filePath,
                hyplink: hyplink
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Content added successfully', 'success');
            loadCourseContent(currentCourseId);
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-content-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to add content', 'danger');
        }
    } catch (error) {
        console.error('Error adding content:', error);
        window.auth.showAlert('Failed to add content. Please try again later.', 'danger');
    }
}

// Handle adding calendar event
async function handleAddEvent(event) {
    event.preventDefault();
    
    const form = event.target;
    const calname = form.elements.calname.value;
    const description = form.elements.description.value;
    const eventDate = form.elements.eventDate.value;
    
    try {
        const response = await fetch(`${API_URL}/calendar_events`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                calname: calname,
                data: description,
                event_date: eventDate,
                cid: currentCourseId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Event added successfully', 'success');
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('add-event-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to add event', 'danger');
        }
    } catch (error) {
        console.error('Error adding event:', error);
        window.auth.showAlert('Failed to add event. Please try again later.', 'danger');
    }
}

// Handle creating an assignment
async function handleCreateAssignment(event) {
    event.preventDefault();
    
    const form = event.target;
    const itemId = form.elements.itemid.value;
    const submitbox = form.elements.submitbox?.checked || false;
    const maxScore = form.elements.maxScore.value || 100;
    const dueDate = form.elements.dueDate.value;
    
    try {
        const response = await fetch(`${API_URL}/assignments`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                itemid: itemId,
                submitbox: submitbox,
                max_score: maxScore,
                due_date: dueDate
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Assignment created successfully', 'success');
            loadAssignments(currentCourseId);
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('create-assignment-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to create assignment', 'danger');
        }
    } catch (error) {
        console.error('Error creating assignment:', error);
        window.auth.showAlert('Failed to create assignment. Please try again later.', 'danger');
    }
}

// Handle creating a forum
async function handleCreateForum(event) {
    event.preventDefault();
    
    const form = event.target;
    const forumName = form.elements.dfname.value;
    
    try {
        const response = await fetch(`${API_URL}/forums`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                dfname: forumName,
                cid: currentCourseId,
                user_type: window.auth.currentUser.type
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Forum created successfully', 'success');
            loadForums(currentCourseId);
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('create-forum-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to create forum', 'danger');
        }
    } catch (error) {
        console.error('Error creating forum:', error);
        window.auth.showAlert('Failed to create forum. Please try again later.', 'danger');
    }
}

// Handle creating a thread
async function handleCreateThread(event) {
    event.preventDefault();
    
    const form = event.target;
    const threadName = form.elements.dtname.value;
    const threadText = form.elements.dttext.value;
    const forumId = document.getElementById('threads-section').dataset.forumId;
    
    try {
        const response = await fetch(`${API_URL}/threads`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                dtname: threadName,
                dttext: threadText,
                dfid: forumId,
                aid: window.auth.currentUser.id
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Thread created successfully', 'success');
            loadThreads(forumId);
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('create-thread-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to create thread', 'danger');
        }
    } catch (error) {
        console.error('Error creating thread:', error);
        window.auth.showAlert('Failed to create thread. Please try again later.', 'danger');
    }
}

// Handle replying to a thread
async function handleReplyThread(event) {
    event.preventDefault();
    
    const form = event.target;
    const threadId = form.elements.dtid.value;
    const replyText = form.elements.dttext.value;
    
    try {
        const response = await fetch(`${API_URL}/threads/reply`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                dtid: threadId,
                dttext: replyText,
                aid: window.auth.currentUser.id
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Reply added successfully', 'success');
            const forumId = document.getElementById('threads-section').dataset.forumId;
            loadThreads(forumId);
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('reply-thread-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to add reply', 'danger');
        }
    } catch (error) {
        console.error('Error adding reply:', error);
        window.auth.showAlert('Failed to add reply. Please try again later.', 'danger');
    }
}

// Handle submitting an assignment
async function handleSubmitAssignment(event) {
    event.preventDefault();
    
    const form = event.target;
    const assignmentId = form.elements.asid.value;
    const filePath = form.elements.filePath.value;
    
    try {
        const response = await fetch(`${API_URL}/submit_assignment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...window.auth.getAuthHeaders()
            },
            body: JSON.stringify({
                asid: assignmentId,
                sid: window.auth.currentUser.id,
                file_path: filePath
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            window.auth.showAlert('Assignment submitted successfully', 'success');
            
            // Close the modal if it exists
            const modal = bootstrap.Modal.getInstance(document.getElementById('submit-assignment-modal'));
            if (modal) {
                modal.hide();
            }
        } else {
            window.auth.showAlert(data.error || 'Failed to submit assignment', 'danger');
        }
    } catch (error) {
        console.error('Error submitting assignment:', error);
        window.auth.showAlert('Failed to submit assignment. Please try again later.', 'danger');
    }
}