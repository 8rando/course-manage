// Global API URL
// const API_URL = 'http://127.0.0.1:5000/backend/app';
const API_URL = '/api';

// User session data
let currentUser = null;

// Check if user is already logged in
document.addEventListener('DOMContentLoaded', () => {
    checkAuthentication();
    
    // Setup event listeners
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// Check if user is authenticated
function checkAuthentication() {
    const userData = localStorage.getItem('user');
    if (userData) {
        try {
            currentUser = JSON.parse(userData);
            updateUIForLoggedInUser();
            
            // If on login page, redirect to dashboard
            if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
                window.location.href = 'dashboard.html';
            }
        } catch (error) {
            console.error('Error parsing user data:', error);
            localStorage.removeItem('user');
        }
    } else if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
        // Redirect to login if not authenticated and not on login page
        window.location.href = 'index.html';
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const fname = document.getElementById('login-fname').value;
    const lname = document.getElementById('login-lname').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_URL}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fname, lname, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Store user info in localStorage
            const userData = {
                id: data.user_id,
                fname: fname,
                lname: lname,
                type: data.type
            };
            localStorage.setItem('user', JSON.stringify(userData));
            
            // Redirect to dashboard
            window.location.href = 'dashboard.html';
        } else {
            showAlert(data.error || 'Login failed. Please try again.', 'danger');
        }
    } catch (error) {
        console.error('Login error:', error);
        showAlert('An error occurred during login. Please try again.', 'danger');
    }
}

// Handle registration form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const fname = document.getElementById('register-fname').value;
    const lname = document.getElementById('register-lname').value;
    const password = document.getElementById('register-password').value;
    const user_type = document.getElementById('register-user-type').value;
    
    try {
        const response = await fetch(`${API_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fname, lname, password, user_type })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Registration successful. Please log in.', 'success');
            // Switch to login tab
            document.getElementById('login-tab').click();
            // Pre-fill login form
            document.getElementById('login-fname').value = fname;
            document.getElementById('login-lname').value = lname;
        } else {
            showAlert(data.error || 'Registration failed. Please try again.', 'danger');
        }
    } catch (error) {
        console.error('Registration error:', error);
        showAlert('An error occurred during registration. Please try again.', 'danger');
    }
}

// Handle logout
function handleLogout() {
    localStorage.removeItem('user');
    window.location.href = 'index.html';
}

// Update UI based on user role
function updateUIForLoggedInUser() {
    if (!currentUser) return;
    
    // Update welcome message
    const userInfoElement = document.getElementById('user-info');
    if (userInfoElement) {
        userInfoElement.textContent = `Welcome, ${currentUser.fname} ${currentUser.lname}`;
    }
    
    // Show/hide elements based on user role
    const adminOnlyElements = document.querySelectorAll('.admin-only');
    const lecturerOnlyElements = document.querySelectorAll('.lecturer-only');
    const studentOnlyElements = document.querySelectorAll('.student-only');
    
    adminOnlyElements.forEach(el => {
        el.style.display = currentUser.type === 'admin' ? '' : 'none';
    });
    
    lecturerOnlyElements.forEach(el => {
        el.style.display = currentUser.type === 'lecturer' ? '' : 'none';
    });
    
    studentOnlyElements.forEach(el => {
        el.style.display = currentUser.type === 'student' ? '' : 'none';
    });
    
    // Update role display if present
    const roleDisplay = document.getElementById('user-role-display');
    if (roleDisplay) {
        roleDisplay.textContent = `You are logged in as: ${currentUser.type.charAt(0).toUpperCase() + currentUser.type.slice(1)}`;
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertId = `alert-${Date.now()}`;
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            alertElement.classList.remove('show');
            setTimeout(() => alertElement.remove(), 150);
        }
    }, 5000);
}

// Function to get auth headers for API requests
function getAuthHeaders() {
    return {
        'Content-Type': 'application/json'
    };
}

// Export functions for use in other modules
window.auth = {
    currentUser,
    showAlert,
    getAuthHeaders
};