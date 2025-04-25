// Global variables
let userId = null;
let userType = null;
let currentForumId = null;

// Initialize when document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthentication();
    
    // Set up event listeners
    setupEventListeners();
    
    // Load user's courses
    loadCourses();
});

// Check if user is authenticated
function checkAuthentication() {
    userId = localStorage.getItem('user_id');
    userType = localStorage.getItem('user_type');
    const userName = localStorage.getItem('user_name');
    
    if (!userId || !userType) {
        window.location.href = 'index.html';
        return;
    }
    
    // Update UI with user information
    document.getElementById('user-name').textContent = `Welcome, ${userName}`;
    
    // Show/hide controls based on user type
    if (userType !== 'admin' && userType !== 'lecturer') {
        document.getElementById('create-forum-button').style.display = 'none';
    }
}

// Set up event listeners
function setupEventListeners() {
    // Logout button
    document.getElementById('logout-button').addEventListener('click', function(e) {
        e.preventDefault();
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_type');
        localStorage.removeItem('user_name');
        window.location.href = 'index.html';
    });
    
    // Course selection change
    document.getElementById('course-select').addEventListener('change', function() {
        const courseId = this.value;
        if (courseId) {
            loadForums(courseId);
        } else {
            document.getElementById('forums-container').innerHTML = '<p>Please select a course to view forums.</p>';
        }
    });
    
    // Create forum form
    document.getElementById('create-forum-form').addEventListener('submit', function(e) {
        e.preventDefault();
        createForum();
    });
    
    // Create thread form
    document.getElementById('create-thread-form').addEventListener('submit', function(e) {
        e.preventDefault();
        createThread();
    });
    
    // Reply thread form
    document.getElementById('reply-thread-form').addEventListener('submit', function(e) {
        e.preventDefault();
        replyToThread();
    });
}

// Load user's courses
function loadCourses() {
    const courseSelect = document.getElementById('course-select');
    const forumCourseSelect = document.getElementById('forum-course-id');
    
    showLoading('forums-loading');
    
    fetch(`/api/courses?user_type=${userType}&user_id=${userId}`)
        .then(response => response.json())
        .then(courses => {
            hideLoading('forums-loading');
            
            // Clear existing options
            while (courseSelect.options.length > 1) {
                courseSelect.remove(1);
            }
            
            while (forumCourseSelect.options.length > 1) {
                forumCourseSelect.remove(1);
            }
            
            // Add new options
            courses.forEach(course => {
                const option1 = document.createElement('option');
                option1.value = course.cid;
                option1.textContent = course.cname;
                courseSelect.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = course.cid;
                option2.textContent = course.cname;
                forumCourseSelect.appendChild(option2);
            });
        })
        .catch(error => {
            hideLoading('forums-loading');
            showAlert('Error loading courses: ' + error.message, 'danger');
        });
}

// Load forums for a course
function loadForums(courseId) {
    const forumsContainer = document.getElementById('forums-container');
    
    showLoading('forums-loading');
    
    fetch(`/api/forums?course_id=${courseId}`)
        .then(response => response.json())
        .then(forums => {
            hideLoading('forums-loading');
            
            if (forums.length === 0) {
                forumsContainer.innerHTML = '<div class="alert alert-info">No forums found for this course.</div>';
                return;
            }
            
            // Display forums
            let html = '<div class="list-group">';
            forums.forEach(forum => {
                html += `
                    <a href="#" class="list-group-item list-group-item-action forum-item" data-forum-id="${forum.dfid}">
                        <div class="d-flex w-100 justify-content-between">
                            <h5 class="mb-1">${forum.dfname}</h5>
                        </div>
                        <button class="btn btn-sm btn-primary view-threads-btn" data-forum-id="${forum.dfid}">View Threads</button>
                    </a>
                `;
            });
            html += '</div>';
            
            forumsContainer.innerHTML = html;
            
            // Add event listeners to view threads buttons
            document.querySelectorAll('.view-threads-btn').forEach(button => {
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    const forumId = this.getAttribute('data-forum-id');
                    viewThreads(forumId);
                });
            });
            
            // Add event listeners to forum items
            document.querySelectorAll('.forum-item').forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    const forumId = this.getAttribute('data-forum-id');
                    viewThreads(forumId);
                });
            });
        })
        .catch(error => {
            hideLoading('forums-loading');
            showAlert('Error loading forums: ' + error.message, 'danger');
        });
}

// View threads for a forum
function viewThreads(forumId) {
    currentForumId = forumId;
    
    // Hide forums section and show threads section
    document.getElementById('forums-section').classList.add('hidden');
    document.getElementById('threads-section').classList.remove('hidden');
    
    const threadsContainer = document.getElementById('threads-container');
    
    showLoading('threads-loading');
    
    fetch(`/api/threads?dfid=${forumId}`)
        .then(response => response.json())
        .then(threads => {
            hideLoading('threads-loading');
            
            if (threads.length === 0) {
                threadsContainer.innerHTML = '<div class="alert alert-info">No threads found in this forum.</div>';
                return;
            }
            
            // Group threads by parent
            const threadMap = new Map();
            const rootThreads = [];
            
            threads.forEach(thread => {
                threadMap.set(thread.dtid, {
                    ...thread,
                    replies: []
                });
            });
            
            threads.forEach(thread => {
                if (thread.parent_dtid) {
                    const parent = threadMap.get(thread.parent_dtid);
                    if (parent) {
                        parent.replies.push(threadMap.get(thread.dtid));
                    }
                } else {
                    rootThreads.push(threadMap.get(thread.dtid));
                }
            });
            
            // Display threads
            let html = '';
            rootThreads.forEach(thread => {
                html += renderThread(thread);
            });
            
            threadsContainer.innerHTML = html;
            
            // Add event listeners to reply buttons
            document.querySelectorAll('.reply-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const threadId = this.getAttribute('data-thread-id');
                    document.getElementById('dtid').value = threadId;
                });
            });
        })
        .catch(error => {
            hideLoading('threads-loading');
            showAlert('Error loading threads: ' + error.message, 'danger');
        });
}

// Render a thread and its replies
function renderThread(thread, depth = 0) {
    const date = new Date(thread.created_at);
    const formattedDate = date.toLocaleString();
    
    let html = `
        <div class="card mb-3 thread-card" style="margin-left: ${depth * 20}px">
            <div class="card-header">
                <h5 class="mb-0">${thread.dtname}</h5>
                <small class="text-muted">Posted on ${formattedDate}</small>
            </div>
            <div class="card-body">
                <p class="card-text">${thread.dttext}</p>
                <button class="btn btn-sm btn-outline-primary reply-btn" data-thread-id="${thread.dtid}" data-bs-toggle="modal" data-bs-target="#reply-thread-modal">
                    Reply
                </button>
            </div>
        </div>
    `;
    
    // Render replies
    if (thread.replies && thread.replies.length > 0) {
        thread.replies.forEach(reply => {
            html += renderThread(reply, depth + 1);
        });
    }
    
    return html;
}

// Create a new forum
function createForum() {
    const formData = {
        dfname: document.getElementById('dfname').value,
        cid: document.getElementById('forum-course-id').value,
        user_type: userType
    };
    
    fetch('/api/forums', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('create-forum-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('create-forum-form').reset();
        
        // Show success message
        showAlert('Forum created successfully', 'success');
        
        // Reload forums
        loadForums(formData.cid);
        
        // Update course select
        document.getElementById('course-select').value = formData.cid;
    })
    .catch(error => {
        showAlert('Error creating forum: ' + error.message, 'danger');
    });
}

// Create a new thread
function createThread() {
    const formData = {
        dtname: document.getElementById('dtname').value,
        dttext: document.getElementById('dttext').value,
        dfid: currentForumId,
        aid: userId
    };
    
    fetch('/api/threads', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('create-thread-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('create-thread-form').reset();
        
        // Show success message
        showAlert('Thread created successfully', 'success');
        
        // Reload threads
        viewThreads(currentForumId);
    })
    .catch(error => {
        showAlert('Error creating thread: ' + error.message, 'danger');
    });
}

// Reply to a thread
function replyToThread() {
    const formData = {
        dtid: document.getElementById('dtid').value,
        dttext: document.getElementById('reply-dttext').value,
        aid: userId
    };
    
    fetch('/api/threads/reply', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('reply-thread-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('reply-thread-form').reset();
        
        // Show success message
        showAlert('Reply added successfully', 'success');
        
        // Reload threads
        viewThreads(currentForumId);
    })
    .catch(error => {
        showAlert('Error replying to thread: ' + error.message, 'danger');
    });
}

// Go back to forums
function backToForums() {
    document.getElementById('forums-section').classList.remove('hidden');
    document.getElementById('threads-section').classList.add('hidden');
}

// Show loading spinner
function showLoading(id) {
    document.getElementById(id).classList.remove('hidden');
}

// Hide loading spinner
function hideLoading(id) {
    document.getElementById(id).classList.add('hidden');
}

// Show alert message
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alertContainer.removeChild(alert);
        }, 150);
    }, 5000);
}