// Global variables
let userId = null;
let userType = null;
let currentCourseId = null;

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
    
    // Show/hide instructor controls based on user type
    if (userType === 'admin' || userType === 'lecturer') {
        document.querySelectorAll('.instructor-only').forEach(elem => {
            elem.style.display = 'block';
        });
    } else {
        document.querySelectorAll('.instructor-only').forEach(elem => {
            elem.style.display = 'none';
        });
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
        currentCourseId = courseId;
        
        if (courseId) {
            loadAssignments(courseId);
            if (userType === 'admin' || userType === 'lecturer') {
                loadSections(courseId);
            }
        } else {
            document.getElementById('assignments-container').innerHTML = '<p>Please select a course to view assignments.</p>';
        }
    });
    
    // Create assignment form
    document.getElementById('create-assignment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        createAssignment();
    });
    
    // Submit assignment form
    document.getElementById('submit-assignment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        submitAssignment();
    });
    
    // Grade assignment form
    document.getElementById('grade-assignment-form').addEventListener('submit', function(e) {
        e.preventDefault();
        gradeAssignment();
    });
}

// Load user's courses
function loadCourses() {
    const courseSelect = document.getElementById('course-select');
    
    showLoading('assignments-loading');
    
    fetch(`/api/courses?user_type=${userType}&user_id=${userId}`)
        .then(response => response.json())
        .then(courses => {
            hideLoading('assignments-loading');
            
            // Clear existing options
            while (courseSelect.options.length > 1) {
                courseSelect.remove(1);
            }
            
            // Add new options
            courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.cid;
                option.textContent = course.cname;
                courseSelect.appendChild(option);
            });
        })
        .catch(error => {
            hideLoading('assignments-loading');
            showAlert('Error loading courses: ' + error.message, 'danger');
        });
}

// Load sections for creating assignments
function loadSections(courseId) {
    const sectionSelect = document.getElementById('sectionSelect');
    
    fetch(`/api/sections?course_id=${courseId}`)
        .then(response => response.json())
        .then(sections => {
            // Clear existing options
            while (sectionSelect.options.length > 1) {
                sectionSelect.remove(1);
            }
            
            // Add new options
            sections.forEach(section => {
                const option = document.createElement('option');
                option.value = section.secid;
                option.textContent = section.secname;
                sectionSelect.appendChild(option);
            });
        })
        .catch(error => {
            showAlert('Error loading sections: ' + error.message, 'danger');
        });
}

// Load assignments for a course
function loadAssignments(courseId) {
    const assignmentsContainer = document.getElementById('assignments-container');
    
    showLoading('assignments-loading');
    
    fetch(`/api/assignments?course_id=${courseId}`)
        .then(response => response.json())
        .then(assignments => {
            hideLoading('assignments-loading');
            
            if (assignments.length === 0) {
                assignmentsContainer.innerHTML = '<div class="alert alert-info">No assignments found for this course.</div>';
                return;
            }
            
            // Display assignments
            let html = '<div class="table-responsive"><table class="table table-striped">';
            html += `
                <thead>
                    <tr>
                        <th>Assignment</th>
                        <th>Max Score</th>
                        <th>Due Date</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            assignments.forEach(assignment => {
                const dueDate = new Date(assignment.due_date);
                const formattedDate = dueDate.toLocaleString();
                
                html += `
                    <tr>
                        <td>${assignment.itemname}</td>
                        <td>${assignment.max_score}</td>
                        <td>${formattedDate}</td>
                        <td>
                `;
                
                if (userType === 'student') {
                    html += `
                        <button class="btn btn-sm btn-primary submit-btn" 
                            data-assignment-id="${assignment.asid}" 
                            data-assignment-name="${assignment.itemname}"
                            data-bs-toggle="modal" 
                            data-bs-target="#submit-assignment-modal">
                            Submit
                        </button>
                    `;
                } else if (userType === 'admin' || userType === 'lecturer') {
                    html += `
                        <button class="btn btn-sm btn-info view-submissions-btn" 
                            data-assignment-id="${assignment.asid}">
                            View Submissions
                        </button>
                    `;
                }
                
                html += `</td></tr>`;
            });
            
            html += '</tbody></table></div>';
            assignmentsContainer.innerHTML = html;
            
            // Add event listeners to buttons
            if (userType === 'student') {
                document.querySelectorAll('.submit-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const assignmentId = this.getAttribute('data-assignment-id');
                        const assignmentName = this.getAttribute('data-assignment-name');
                        
                        // Set assignment details in the modal
                        document.getElementById('asid').value = assignmentId;
                        document.getElementById('submission-details').innerHTML = `
                            <p><strong>Assignment:</strong> ${assignmentName}</p>
                        `;
                        
                        // Load assignment details
                        fetch(`/api/assignment_details?asid=${assignmentId}`)
                            .then(response => response.json())
                            .then(details => {
                                if (details.submitbox) {
                                    document.getElementById('submission-details').innerHTML += `
                                        <p><strong>Instructions:</strong> ${details.submitbox}</p>
                                        <p><strong>Due Date:</strong> ${new Date(details.due_date).toLocaleString()}</p>
                                    `;
                                }
                            })
                            .catch(error => {
                                console.error('Error loading assignment details:', error);
                            });
                    });
                });
            } else if (userType === 'admin' || userType === 'lecturer') {
                // Add event listeners to view submissions buttons
                document.querySelectorAll('.view-submissions-btn').forEach(button => {
                    button.addEventListener('click', function() {
                        const assignmentId = this.getAttribute('data-assignment-id');
                        loadSubmissions(assignmentId);
                    });
                });
            }
        })
        .catch(error => {
            hideLoading('assignments-loading');
            showAlert('Error loading assignments: ' + error.message, 'danger');
        });
}

// Load submissions for an assignment
function loadSubmissions(assignmentId) {
    const submissionsContainer = document.getElementById('submissions-container');
    document.getElementById('submissions-section').classList.remove('hidden');
    
    showLoading('submissions-loading');
    
    fetch(`/api/submissions?asid=${assignmentId}`)
        .then(response => response.json())
        .then(submissions => {
            hideLoading('submissions-loading');
            
            if (submissions.length === 0) {
                submissionsContainer.innerHTML = '<div class="alert alert-info">No submissions found for this assignment.</div>';
                return;
            }
            
            // Display submissions
            let html = '<div class="table-responsive"><table class="table table-striped">';
            html += `
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Submission</th>
                        <th>Submitted On</th>
                        <th>Grade</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
            `;
            
            submissions.forEach(submission => {
                const submittedDate = new Date(submission.submitted_at);
                const formattedDate = submittedDate.toLocaleString();
                
                html += `
                    <tr>
                        <td>${submission.fname} ${submission.lname}</td>
                        <td>${submission.file_path}</td>
                        <td>${formattedDate}</td>
                        <td>${submission.grade !== null ? submission.grade : 'Not graded'}</td>
                        <td>
                            <button class="btn btn-sm btn-primary grade-btn" 
                                data-submission-id="${submission.submission_id}"
                                data-student-name="${submission.fname} ${submission.lname}"
                                data-submission-path="${submission.file_path}"
                                data-max-score="${submission.max_score}"
                                data-bs-toggle="modal" 
                                data-bs-target="#grade-assignment-modal">
                                Grade
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += '</tbody></table></div>';
            submissionsContainer.innerHTML = html;
            
            // Add event listeners to grade buttons
            document.querySelectorAll('.grade-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const submissionId = this.getAttribute('data-submission-id');
                    const studentName = this.getAttribute('data-student-name');
                    const submissionPath = this.getAttribute('data-submission-path');
                    const maxScore = this.getAttribute('data-max-score');
                    
                    // Set submission details in the modal
                    document.getElementById('submission_id').value = submissionId;
                    document.getElementById('submission-info').innerHTML = `
                        <p><strong>Student:</strong> ${studentName}</p>
                        <p><strong>Submission:</strong> ${submissionPath}</p>
                        <p><strong>Maximum Score:</strong> ${maxScore}</p>
                    `;
                    
                    // Set max attribute on grade input
                    document.getElementById('grade').setAttribute('max', maxScore);
                });
            });
        })
        .catch(error => {
            hideLoading('submissions-loading');
            showAlert('Error loading submissions: ' + error.message, 'danger');
        });
}

// Create a new assignment
function createAssignment() {
    // First, create a section item
    const sectionItemData = {
        itemname: document.getElementById('itemname').value,
        secid: document.getElementById('sectionSelect').value,
        type: 'assignment' // This is a content type
    };
    
    fetch('/api/content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(sectionItemData)
    })
    .then(response => response.json())
    .then(data => {
        // Now create the assignment using the returned itemid
        const assignmentData = {
            itemid: data.itemid || data.item_id, // Depending on your API response format
            submitbox: document.getElementById('submitbox').value,
            max_score: document.getElementById('max_score').value,
            due_date: document.getElementById('due_date').value
        };
        
        return fetch('/api/assignments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(assignmentData)
        });
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('create-assignment-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('create-assignment-form').reset();
        
        // Show success message
        showAlert('Assignment created successfully', 'success');
        
        // Reload assignments
        loadAssignments(currentCourseId);
    })
    .catch(error => {
        showAlert('Error creating assignment: ' + error.message, 'danger');
    });
}

// Submit an assignment
function submitAssignment() {
    const formData = {
        asid: document.getElementById('asid').value,
        sid: userId,
        file_path: document.getElementById('file_path').value
    };
    
    fetch('/api/submit_assignment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('submit-assignment-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('submit-assignment-form').reset();
        
        // Show success message
        showAlert('Assignment submitted successfully', 'success');
        
        // Reload assignments
        loadAssignments(currentCourseId);
    })
    .catch(error => {
        showAlert('Error submitting assignment: ' + error.message, 'danger');
    });
}

// Grade an assignment
function gradeAssignment() {
    const formData = {
        submission_id: document.getElementById('submission_id').value,
        grade: document.getElementById('grade').value
    };
    
    fetch('/api/grade_assignment', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('grade-assignment-modal'));
        modal.hide();
        
        // Reset form
        document.getElementById('grade-assignment-form').reset();
        
        // Show success message
        showAlert('Assignment graded successfully', 'success');
        
        // Refresh the submissions list
        const assignmentId = document.querySelector('.view-submissions-btn[aria-expanded="true"]')?.getAttribute('data-assignment-id');
        if (assignmentId) {
            loadSubmissions(assignmentId);
        }
    })
    .catch(error => {
        showAlert('Error grading assignment: ' + error.message, 'danger');
    });
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