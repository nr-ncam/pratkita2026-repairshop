const token = localStorage.getItem("token");
if (!token) window.location.href = "/"; // Redirect if not logged in

const headers = {
    "Authorization": `Bearer ${token}`
};

// --- 1. Fetch Services for Dropdown and Catalog ---
async function loadServices() {
    const res = await fetch("/api/services/");
    const services = await res.json();
    
    const select = document.getElementById("service-select");
    const catalog = document.getElementById("catalog-list");
    
    select.innerHTML = '<option value="">Выберите услугу...</option>';
    catalog.innerHTML = "";

    services.forEach(s => {
        // Add to dropdown
        select.innerHTML += `<option value="${s.id}">${s.name} - ${s.price} руб.</option>`;
        // Add to catalog list
        catalog.innerHTML += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <strong>${s.name}</strong><br>
                    <small class="text-muted">${s.description || ""}</small>
                </div>
                <span class="badge bg-primary rounded-pill">${s.price} руб.</span>
            </li>
        `;
    });
}

// --- 2. Create a Request (Form Submit) ---
document.getElementById("request-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    
    // We must use FormData because we are uploading a file
    const formData = new FormData();
    formData.append("device_type", document.getElementById("device-type").value);
    formData.append("description", document.getElementById("description").value);
    formData.append("service_id", document.getElementById("service-select").value);
    
    const photoFile = document.getElementById("photo").files[0];
    if (photoFile) formData.append("photo", photoFile);

    const res = await fetch("/api/requests/", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` }, // Don't set Content-Type, browser does it for FormData
        body: formData
    });

    if (res.ok) {
        alert("Заявка успешно создана!");
        document.getElementById("request-form").reset();
        loadMyRequests(); // Refresh history
    } else {
        alert("Ошибка при создании заявки");
    }
});

// --- 3. Load User's Request History ---
async function loadMyRequests() {
    const res = await fetch("/api/requests/my", { headers });
    const requests = await res.json();
    
    const container = document.getElementById("requests-list");
    container.innerHTML = "";

    if (requests.length === 0) {
        container.innerHTML = "<p class='text-muted'>У вас пока нет заявок.</p>";
        return;
    }

    // Helper for colored status badges
    const getBadgeClass = (status) => {
        if (status === "Принята") return "bg-secondary";
        if (status === "В диагностике") return "bg-warning text-dark";
        if (status === "В ремонте") return "bg-info text-dark";
        if (status === "Готова к выдаче") return "bg-primary";
        if (status === "Выдана") return "bg-success";
        return "bg-dark";
    };

    requests.forEach(r => {
        container.innerHTML += `
            <div class="card mb-3">
                <div class="card-body">
                    <div class="d-flex justify-content-between">
                        <h5 class="card-title">Заявка #${r.id} - ${r.device_type}</h5>
                        <span class="badge ${getBadgeClass(r.status)} fs-6">${r.status}</span>
                    </div>
                    <h6 class="card-subtitle mb-2 text-muted">${r.service_name}</h6>
                    <p class="card-text">${r.description}</p>
                    ${r.photo_path ? `<a href="${r.photo_path}" target="_blank" class="btn btn-sm btn-outline-secondary">Посмотреть фото</a>` : ""}
                    <hr>
                    <small class="text-muted">Создана: ${new Date(r.created_at).toLocaleString()}</small>
                </div>
            </div>
        `;
    });
}

// --- 4. Logout ---
function logout() {
    localStorage.removeItem("token");
    window.location.href = "/";
}

// Initialize page
loadServices();
loadMyRequests();