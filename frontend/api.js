// api.js - Fonctions pour communiquer avec le backend Django

const API_BASE = "http://localhost:8000/api";

// Authentification (login)
async function login(username, password) {
    const response = await fetch(`${API_BASE}/users/login/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    });
    return response.json();
}

// Inscription
async function register(userData) {
    const response = await fetch(`${API_BASE}/users/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData)
    });
    return response.json();
}

// Récupérer les trajets
async function getRides(token) {
    const response = await fetch(`${API_BASE}/rides/`, {
        headers: { "Authorization": `Token ${token}` }
    });
    return response.json();
}

// Créer un trajet
async function createRide(token, rideData) {
    const response = await fetch(`${API_BASE}/rides/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Token ${token}`
        },
        body: JSON.stringify(rideData)
    });
    return response.json();
}

// WebSocket pour le chat
function connectChat(conversationId, onMessage) {
    const ws = new WebSocket(`ws://localhost:8000/ws/chat/${conversationId}/`);
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        onMessage(data);
    };
    return ws;
}

// Export des fonctions
window.api = { login, register, getRides, createRide, connectChat };
