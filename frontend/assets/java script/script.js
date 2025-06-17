// Configuration API
const API_BASE_URL = 'http://localhost:8000/api';

// Fonction pour les requêtes authentifiées
async function apiRequest(endpoint, options = {}) {
    const token = localStorage.getItem('authToken');
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Token ${token}` }),
            ...options.headers,
        },
        ...options,
    };
    const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
    return response.json();
}

// Inscription
async function registerUser(userData) {
    return await apiRequest('/users/register/', {
        method: 'POST',
        body: JSON.stringify(userData),
    });
}

// Connexion
async function loginUser(credentials) {
    const response = await apiRequest('/users/login/', {
        method: 'POST',
        body: JSON.stringify(credentials),
    });
    if (response.token) {
        localStorage.setItem('authToken', response.token);
        localStorage.setItem('user', JSON.stringify(response.user));
    }
    return response;
}

// Recherche de trajets
async function searchRides(searchData) {
    return await apiRequest('/rides/search/', {
        method: 'POST',
        body: JSON.stringify(searchData),
    });
}

// Créer un trajet
async function createRide(rideData) {
    return await apiRequest('/rides/', {
        method: 'POST',
        body: JSON.stringify(rideData),
    });
}

let currentUser = null;
let conversations = [
    {
        id: 1,
        name: "Marie Dupont",
        topic: "Trajet Cotonou → IFRI",
        messages: [
            { id: 1, text: "Salut ! Je peux te prendre demain matin pour aller à IFRI ?", sent: false, time: "10:30" },
            { id: 2, text: "Parfait ! À quelle heure passes-tu ?", sent: true, time: "10:32" },
            { id: 3, text: "Je passe vers 7h30. Ça te va ?", sent: false, time: "10:35" }
        ]
    },
    {
        id: 2,
        name: "Jean Martin",
        topic: "Covoiturage vendredi",
        messages: [
            { id: 1, text: "Salut ! Tu as encore de la place vendredi ?", sent: false, time: "09:15" },
            { id: 2, text: "Oui bien sûr ! Rendez-vous à 7h25 ?", sent: true, time: "09:18" }
        ]
    }
];
let currentConversation = conversations[0];

// Navigation functions
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
}

function showLogin() {
    showPage('loginPage');
}

function showRegister() {
    showPage('registerPage');
}

function showForgotPassword() {
    showPage('forgotPasswordPage');
}

function showDashboard() {
    showPage('dashboardPage');
    updateNavForLoggedInUser();
}

function showHome() {
    showPage('homePage');
    updateNavForLoggedOutUser();
}

function updateNavForLoggedInUser() {
    const navButtons = document.getElementById('navButtons');
    navButtons.innerHTML = `
        <span style="color: #667eea; font-weight: 500;">
            <i class="fas fa-user"></i>
            ${currentUser ? currentUser.firstName + ' ' + currentUser.lastName : 'Utilisateur'}
        </span>
        <a href="#" class="btn btn-outline" onclick="logout()">
            <i class="fas fa-sign-out-alt"></i>
            Déconnexion
        </a>
    `;
}

function updateNavForLoggedOutUser() {
    const navButtons = document.getElementById('navButtons');
    navButtons.innerHTML = `
        <a href="#" class="btn btn-outline" onclick="showLogin()">
            <i class="fas fa-sign-in-alt"></i>
            Connexion
        </a>
        <a href="#" class="btn btn-primary" onclick="showRegister()">
            <i class="fas fa-user-plus"></i>
            S'inscrire
        </a>
    `;
}

function logout() {
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    showHome();
}

// Dashboard navigation
function showDashboardSection(sectionId) {
    // Update sidebar navigation
    document.querySelectorAll('.dashboard-nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');

    // Show corresponding section
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    document.getElementById(sectionId).classList.add('active');
    document.getElementById(sectionId).style.display = 'block';
}

// Dashboard navigation event listeners
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.dashboard-nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            if (section) {
                showDashboardSection(section);
            }
        });
    });
});

// Form validation functions
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[0-9\s\-\(\)]{8,}$/;
    return re.test(phone);
}

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + 'Error');
    field.classList.add('error');
    if (errorDiv) {
        errorDiv.textContent = message;
    }
}

function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorDiv = document.getElementById(fieldId + 'Error');
    field.classList.remove('error');
    if (errorDiv) {
        errorDiv.textContent = '';
    }
}

function showSuccess(fieldId, message) {
    const errorDiv = document.getElementById(fieldId + 'Error');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.className = 'success-message';
    }
}

// Registration form handler
document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Clear previous errors
    ['firstName', 'lastName', 'email', 'phone', 'password', 'confirmPassword', 'role'].forEach(clearError);

    let isValid = true;

    // Get form values
    const firstName = document.getElementById('firstName').value.trim();
    const lastName = document.getElementById('lastName').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const role = document.getElementById('role').value;

    // Validate fields
    if (!firstName) {
        showError('firstName', 'Le prénom est requis');
        isValid = false;
    }

    if (!lastName) {
        showError('lastName', 'Le nom est requis');
        isValid = false;
    }

    if (!email) {
        showError('email', 'L\'e-mail est requis');
        isValid = false;
    } else if (!validateEmail(email)) {
        showError('email', 'Format d\'e-mail invalide');
        isValid = false;
    }

    if (!phone) {
        showError('phone', 'Le numéro de téléphone est requis');
        isValid = false;
    } else if (!validatePhone(phone)) {
        showError('phone', 'Format de téléphone invalide');
        isValid = false;
    }

    if (!password) {
        showError('password', 'Le mot de passe est requis');
        isValid = false;
    } else if (password.length < 6) {
        showError('password', 'Le mot de passe doit contenir au moins 6 caractères');
        isValid = false;
    }

    if (password !== confirmPassword) {
        showError('confirmPassword', 'Les mots de passe ne correspondent pas');
        isValid = false;
    }

    if (!role) {
        showError('role', 'Veuillez choisir un rôle');
        isValid = false;
    }

    if (isValid) {
        try {
            const response = await registerUser({
                first_name: firstName,
                last_name: lastName,
                email: email,
                phone: phone,
                password: password,
                role: role
            });
            if (response && !response.error) {
                alert('Inscription réussie ! Bienvenue sur IFRI Covoiturage.');
                showLogin();
            } else {
                alert(response.error || "Erreur lors de l'inscription.");
            }
        } catch (err) {
            alert("Erreur réseau lors de l'inscription.");
        }
    }
});

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    clearError('loginEmail');
    clearError('loginPassword');

    const emailOrPhone = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;

    let isValid = true;

    if (!emailOrPhone) {
        showError('loginEmail', 'L\'e-mail ou téléphone est requis');
        isValid = false;
    }

    if (!password) {
        showError('loginPassword', 'Le mot de passe est requis');
        isValid = false;
    }

    if (isValid) {
        try {
            const response = await loginUser({ email: emailOrPhone, password });
            if (response.token) {
                // Récupère l'utilisateur connecté depuis la réponse ou le localStorage
                currentUser = response.user || JSON.parse(localStorage.getItem('user'));
                document.getElementById('userName').textContent = currentUser.firstName;
                showDashboard();
                alert('Connexion réussie !');
            } else {
                alert(response.error || "Identifiants invalides.");
            }
        } catch (err) {
            alert("Erreur réseau lors de la connexion.");
        }
    }
});

// Forgot password form handler
document.getElementById('forgotPasswordForm').addEventListener('submit', function(e) {
    e.preventDefault();

    clearError('resetEmail');

    const email = document.getElementById('resetEmail').value.trim();

    if (!email) {
        showError('resetEmail', 'L\'adresse e-mail est requise');
        return;
    }

    if (!validateEmail(email)) {
        showError('resetEmail', 'Format d\'e-mail invalide');
        return;
    }

    // Simulate sending reset email
    showSuccess('resetEmail', 'Un lien de réinitialisation a été envoyé à votre adresse e-mail');

    setTimeout(() => {
        alert('Vérifiez votre boîte e-mail pour le lien de réinitialisation.');
        showLogin();
    }, 2000);
});

// Profile form handler
document.getElementById('profileForm').addEventListener('submit', function(e) {
    e.preventDefault();
    alert('Profil mis à jour avec succès !');
});

// Search form handler
document.getElementById('searchForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const departure = document.getElementById('departure').value;
    const destination = document.getElementById('destination').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;

    // Simulate search results
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = `
        <h4 style="margin-bottom: 20px;">Résultats de recherche</h4>
        <div class="ride-card">
            <div class="ride-info">
                <div class="ride-route">${departure || 'Cotonou'} → ${destination || 'IFRI'}</div>
                <div class="ride-details">
                    <strong>Marie Dupont</strong> • ${date || 'Demain'}, ${time || '07:30'} • 2 places disponibles
                </div>
                <div style="margin-top: 8px; color: #666; font-size: 14px;">
                    <i class="fas fa-star" style="color: #ffc107;"></i> 4.8 • Toyota Corolla
                </div>
            </div>
            <div class="ride-actions">
                <button class="btn btn-outline btn-sm">Détails</button>
                <button class="btn btn-primary btn-sm" onclick="requestRide()">Demander</button>
            </div>
        </div>
        <div class="ride-card">
            <div class="ride-info">
                <div class="ride-route">${departure || 'Cotonou'} → ${destination || 'IFRI'}</div>
                <div class="ride-details">
                    <strong>Jean Martin</strong> • ${date || 'Demain'}, ${time || '08:00'} • 1 place disponible
                </div>
                <div style="margin-top: 8px; color: #666; font-size: 14px;">
                    <i class="fas fa-star" style="color: #ffc107;"></i> 4.5 • Peugeot 208
                </div>
            </div>
            <div class="ride-actions">
                <button class="btn btn-outline btn-sm">Détails</button>
                <button class="btn btn-primary btn-sm" onclick="requestRide()">Demander</button>
            </div>
        </div>
    `;
});

// Chat functions
function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message) {
        // Add message to current conversation
        const newMessage = {
            id: Date.now(),
            text: message,
            sent: true,
            time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
        };

        currentConversation.messages.push(newMessage);

        // Update chat display
        updateChatMessages();

        // Clear input
        messageInput.value = '';

        // Simulate response after a delay
        setTimeout(() => {
            const response = {
                id: Date.now(),
                text: "Message reçu ! Je vous réponds bientôt.",
                sent: false,
                time: new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
            };
            currentConversation.messages.push(response);
            updateChatMessages();
        }, 1000);
    }
}

function updateChatMessages() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = currentConversation.messages.map(msg => `
        <div class="message ${msg.sent ? 'sent' : 'received'}">
            ${msg.text}
            <div style="font-size: 12px; opacity: 0.7; margin-top: 5px;">
                ${msg.time}
            </div>
        </div>
    `).join('');

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Allow sending message with Enter key
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Utility functions
function requestRide() {
    alert('Demande de covoiturage envoyée ! Le conducteur recevra une notification.');
}

function showCreateRideForm() {
    alert('Fonctionnalité de création de trajet en cours de développement.');
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;

    // Set default time
    document.getElementById('time').value = '07:30';

    // Initialize chat
        });