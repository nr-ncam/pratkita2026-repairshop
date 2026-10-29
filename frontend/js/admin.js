const token = localStorage.getItem("token");
if (!token) window.location.href = "/";
const headers = { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" };

let mastersList = [];

// Загрузка статистики
async function loadStats() {
    const res = await fetch("/api/stats/dashboard", { headers });
    const data = await res.json();
    
    document.getElementById("stats-container").innerHTML = `
        <div class="col-md-4">
            <div class="card text-white bg-primary mb-3">
                <div class="card-body">
                    <h5 class="card-title">Выручка</h5>
                    <h2>${data.revenue} руб.</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-white bg-info mb-3">
                <div class="card-body">
                    <h5 class="card-title">Заявок в работе</h5>
                    <h2>${data.requests_by_status['В ремонте'] || 0}</h2>
                </div>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card text-white bg-secondary mb-3">
                <div class="card-body">
                    <h5 class="card-title">Готовы к выдаче</h5>
                    <h2>${data.requests_by_status['Готова к выдаче'] || 0}</h2>
                </div>
            </div>
        </div>
    `;
}

// Загрузка мастеров
async function loadMasters() {
    const res = await fetch("/api/admin/masters", { headers });
    mastersList = await res.json();
}

// Загрузка всех заявок
async function loadRequests() {
    const res = await fetch("/api/admin/requests", { headers });
    const requests = await res.json();
    
    const container = document.getElementById("all-requests");
    container.innerHTML = requests.map(r => {
        // Генерируем опции для выбора мастера
        const masterOptions = mastersList.map(m => 
            `<option value="${m.id}" ${r.master_id === m.id ? 'selected' : ''}>${m.full_name}</option>`
        ).join("");

        return `
            <div class="card mb-2 shadow-sm">
                <div class="card-body d-flex justify-content-between align-items-center">
                    <div>
                        <strong>#${r.id} - ${r.device_type}</strong>
                        <br><small class="text-muted">Статус: ${r.status}</small>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                        <select class="form-select form-select-sm" onchange="assignMaster(${r.id}, this.value)">
                            <option value="">Назначить мастера...</option>
                            ${masterOptions}
                        </select>
                    </div>
                </div>
            </div>
        `;
    }).join("");
}

// Назначение мастера
async function assignMaster(requestId, masterId) {
    if (!masterId) return;
    const res = await fetch(`/api/admin/requests/${requestId}/assign/${masterId}`, {
        method: "PUT",
        headers
    });
    if (res.ok) {
        alert("Мастер назначен!");
        loadRequests();
    }
}

// Формы
document.getElementById("service-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetch("/api/services/", {
        method: "POST",
        headers,
        body: JSON.stringify({
            name: document.getElementById("s-name").value,
            price: parseFloat(document.getElementById("s-price").value)
        })
    });
    alert("Услуга добавлена!");
    e.target.reset();
});

document.getElementById("inventory-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    await fetch("/api/inventory/", {
        method: "POST",
        headers,
        body: JSON.stringify({
            name: document.getElementById("i-name").value,
            quantity: parseInt(document.getElementById("i-qty").value),
            price: parseFloat(document.getElementById("i-price").value)
        })
    });
    alert("Запчасть добавлена на склад!");
    e.target.reset();
});

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

async function loadUsers() {
    const res = await fetch("/api/admin/users", { headers });
    const users = await res.json();
    
    const container = document.getElementById("users-list");
    container.innerHTML = `
        <table class="table table-sm table-hover">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>ФИО</th>
                    <th>Email</th>
                    <th>Роль</th>
                </tr>
            </thead>
            <tbody>
                ${users.map(u => `
                    <tr>
                        <td>${u.id}</td>
                        <td>${u.full_name}</td>
                        <td>${u.email}</td>
                        <td>
                            <select class="form-select form-select-sm" onchange="changeRole(${u.id}, this.value)">
                                <option value="client" ${u.role === 'client' ? 'selected' : ''}>Клиент</option>
                                <option value="master" ${u.role === 'master' ? 'selected' : ''}>Мастер</option>
                                <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Админ</option>
                            </select>
                        </td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

// --- Функция для смены роли ---
async function changeRole(userId, newRole) {
    const res = await fetch(`/api/admin/users/${userId}/role?new_role=${newRole}`, {
        method: "PATCH",
        headers
    });
    if (res.ok) {
        alert("Роль обновлена!");
    } else {
        const err = await res.json();
        alert("Ошибка: " + err.detail);
        loadUsers(); // Откатываем визуально назад
    }
}

// Инициализация
async function init() {
    await loadMasters();
    await loadStats();
    await loadRequests();
    await loadUsers(); 
}
init();