const API_URL = "/api/auth";

// Toggle between Login and Register forms
function toggleForms() {
    const loginSec = document.getElementById("login-section");
    const regSec = document.getElementById("register-section");
    loginSec.style.display = loginSec.style.display === "none" ? "block" : "none";
    regSec.style.display = regSec.style.display === "none" ? "block" : "none";
}

// Handle Registration
document.getElementById("register-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const data = {
        full_name: document.getElementById("reg-name").value,
        email: document.getElementById("reg-email").value,
        phone: document.getElementById("reg-phone").value,
        password: document.getElementById("reg-password").value,
        role: "client" // Default role for registration
    };

    const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        alert("Регистрация успешна! Теперь войдите.");
        toggleForms();
    } else {
        const err = await res.json();
        alert("Ошибка: " + err.detail);
    }
});

// Handle Login
document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    // FastAPI OAuth2 expects form-data for login, not JSON
    const formData = new URLSearchParams();
    formData.append("username", email); // OAuth2 uses 'username' field
    formData.append("password", password);

    const res = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: formData
    });

    if (res.ok) {
        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        
        // Decode JWT to get role (Base64 decoding)
        const payload = JSON.parse(atob(data.access_token.split('.')[1]));
        
        // Redirect based on role
        if (payload.role === "admin") window.location.href = "/ui/admin";
        else if (payload.role === "master") window.location.href = "/ui/master";
        else window.location.href = "/ui/client";
    } else {
        alert("Неверный логин или пароль");
    }
});