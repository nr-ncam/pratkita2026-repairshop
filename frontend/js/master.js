const token = localStorage.getItem("token");
if (!token) window.location.href = "/";
const headers = { "Authorization": `Bearer ${token}`, "Content-Type": "application/json" };

// Загрузка склада
async function loadInventory() {
    const res = await fetch("/api/inventory/", { headers });
    if (!res.ok) return;
    const parts = await res.json();
    const list = document.getElementById("inventory-list");
    list.innerHTML = parts.map(p => `
        <li class="list-group-item d-flex justify-content-between">
            <span>${p.name}</span>
            <span class="badge bg-success">${p.quantity} шт.</span>
        </li>
    `).join("");
}

// Загрузка заявок мастера
async function loadRequests() {
    const res = await fetch("/api/master/my-requests", { headers });
    const requests = await res.json();
    const container = document.getElementById("my-requests");
    
    if (requests.length === 0) {
        container.innerHTML = "<p class='text-muted'>У вас нет назначенных заявок.</p>";
        return;
    }

    container.innerHTML = requests.map(r => `
        <div class="card mb-3 shadow-sm">
            <div class="card-body">
                <h5 class="card-title">Заявка #${r.id} - ${r.device_type}</h5>
                <p>${r.description}</p>
                <hr>
                <div class="row">
                    <div class="col-md-4">
                        <label class="form-label">Статус</label>
                        <select class="form-select" onchange="updateStatus(${r.id}, this.value)">
                            <option value="Принята" ${r.status === 'Принята' ? 'selected' : ''}>Принята</option>
                            <option value="В диагностике" ${r.status === 'В диагностике' ? 'selected' : ''}>В диагностике</option>
                            <option value="В ремонте" ${r.status === 'В ремонте' ? 'selected' : ''}>В ремонте</option>
                            <option value="Готова к выдаче" ${r.status === 'Готова к выдаче' ? 'selected' : ''}>Готова к выдаче</option>
                        </select>
                    </div>
                    <div class="col-md-8">
                        <label class="form-label">Добавить комментарий</label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="comment-${r.id}" placeholder="Что сделано/выявлено...">
                            <button class="btn btn-primary" onclick="addComment(${r.id})">Добавить</button>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <label class="form-label">Использовать запчасть</label>
                    <div class="input-group">
                        <input type="number" class="form-control" id="part-id-${r.id}" placeholder="ID детали">
                        <input type="number" class="form-control" id="part-qty-${r.id}" placeholder="Кол-во" value="1">
                        <button class="btn btn-warning" onclick="usePart(${r.id})">Списать</button>
                    </div>
                </div>
            </div>
        </div>
    `).join("");
}

// Обновление статуса
async function updateStatus(id, status) {
    await fetch(`/api/master/requests/${id}/status`, {
        method: "PATCH",
        headers,
        body: JSON.stringify({ status: status })
    });
    alert("Статус обновлен!");
}

// Добавление комментария
async function addComment(id) {
    const text = document.getElementById(`comment-${id}`).value;
    if (!text) return;
    await fetch(`/api/master/requests/${id}/comments`, {
        method: "POST",
        headers,
        body: JSON.stringify({ text: text })
    });
    alert("Комментарий добавлен!");
    document.getElementById(`comment-${id}`).value = "";
}

// Списание детали
async function usePart(requestId) {
    const partId = document.getElementById(`part-id-${requestId}`).value;
    const qty = document.getElementById(`part-qty-${requestId}`).value;
    if (!partId) return;
    
    const res = await fetch(`/api/master/requests/${requestId}/parts`, {
        method: "POST",
        headers,
        body: JSON.stringify({ part_id: parseInt(partId), quantity: parseInt(qty) })
    });
    
    if (res.ok) {
        alert("Деталь списана со склада!");
        loadInventory();
    } else {
        const err = await res.json();
        alert(err.detail);
    }
}

function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

loadInventory();
loadRequests();