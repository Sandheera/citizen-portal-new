let currentType = null;
let currentItem = null;

async function loadServices() {
    const res = await fetch('/api/admin/services');
    const services = await res.json();
    const el = document.getElementById('servicesList');
    el.innerHTML = services.length ? services.map(s => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${s.name?.en || s.id}</strong>
                <p style="margin:4px 0; font-size:12px; color:#666;">${s.id}</p>
            </div>
            <button onclick="deleteService('${s.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
        </div>
    `).join('') : '<p>No services found.</p>';
}

async function loadCategories() {
    const res = await fetch('/api/admin/categories');
    const categories = await res.json();
    const el = document.getElementById('categoriesList');
    el.innerHTML = categories.length ? categories.map(c => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${c.name?.en || c.id}</strong>
                <p style="margin:4px 0; font-size:12px; color:#666;">${c.id}</p>
            </div>
            <button onclick="deleteCategory('${c.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
        </div>
    `).join('') : '<p>No categories found.</p>';
}

async function loadOfficers() {
    const res = await fetch('/api/admin/officers');
    const officers = await res.json();
    const el = document.getElementById('officersList');
    el.innerHTML = officers.length ? officers.map(o => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${o.name}</strong>
                <p style="margin:4px 0; font-size:12px; color:#666;">${o.role}</p>
            </div>
            <button onclick="deleteOfficer('${o.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
        </div>
    `).join('') : '<p>No officers found.</p>';
}

async function loadAds() {
    const res = await fetch('/api/admin/ads');
    const ads = await res.json();
    const el = document.getElementById('adsList');
    el.innerHTML = ads.length ? ads.map(a => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${a.title}</strong>
                <p style="margin:4px 0; font-size:12px; color:#666;">${a.body || 'No description'}</p>
            </div>
            <button onclick="deleteAd('${a.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
        </div>
    `).join('') : '<p>No ads found.</p>';
}

function showServiceForm() {
    currentType = 'service';
    currentItem = null;
    document.getElementById('formTitle').textContent = 'Add Service';
    document.getElementById('formFields').innerHTML = `
        <input type="text" id="id" placeholder="Service ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="name_en" placeholder="Service Name (English)" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="description" placeholder="Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:80px;"></textarea>
    `;
    document.getElementById('formModal').style.display = 'flex';
}

function showCategoryForm() {
    currentType = 'category';
    currentItem = null;
    document.getElementById('formTitle').textContent = 'Add Category';
    document.getElementById('formFields').innerHTML = `
        <input type="text" id="id" placeholder="Category ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="name_en" placeholder="Category Name (English)" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
    `;
    document.getElementById('formModal').style.display = 'flex';
}

function showOfficerForm() {
    currentType = 'officer';
    currentItem = null;
    document.getElementById('formTitle').textContent = 'Add Officer';
    document.getElementById('formFields').innerHTML = `
        <input type="text" id="id" placeholder="Officer ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="name" placeholder="Officer Name" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="role" placeholder="Role" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="email" id="email" placeholder="Email" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
    `;
    document.getElementById('formModal').style.display = 'flex';
}

function showAdForm() {
    currentType = 'ad';
    currentItem = null;
    document.getElementById('formTitle').textContent = 'Add Advertisement';
    document.getElementById('formFields').innerHTML = `
        <input type="text" id="id" placeholder="Ad ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="title" placeholder="Title" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="body" placeholder="Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:80px;"></textarea>
        <input type="url" id="link" placeholder="Link" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
    `;
    document.getElementById('formModal').style.display = 'flex';
}

function closeForm() {
    document.getElementById('formModal').style.display = 'none';
}

async function submitForm(e) {
    e.preventDefault();
    
    let payload = {};
    const form = document.getElementById('dataForm');
    const inputs = form.querySelectorAll('input, textarea');
    inputs.forEach(inp => {
        payload[inp.id] = inp.value;
    });
    
    if (currentType === 'service') {
        payload.name = { en: payload.name_en };
        delete payload.name_en;
    } else if (currentType === 'category') {
        payload.name = { en: payload.name_en };
        delete payload.name_en;
    }
    
    const endpoint = `/api/admin/${currentType}s`;
    const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    });
    
    if (res.ok) {
        alert('Saved successfully!');
        closeForm();
        location.reload();
    } else {
        alert('Error saving!');
    }
}

async function deleteService(id) {
    if (confirm('Delete this service?')) {
        await fetch(`/api/admin/services/${id}`, { method: 'DELETE' });
        loadServices();
    }
}

async function deleteCategory(id) {
    if (confirm('Delete this category?')) {
        await fetch(`/api/admin/categories?id=${id}`, { method: 'DELETE' });
        loadCategories();
    }
}

async function deleteOfficer(id) {
    if (confirm('Delete this officer?')) {
        await fetch(`/api/admin/officers?id=${id}`, { method: 'DELETE' });
        loadOfficers();
    }
}

async function deleteAd(id) {
    if (confirm('Delete this ad?')) {
        await fetch(`/api/admin/ads?id=${id}`, { method: 'DELETE' });
        loadAds();
    }
}

window.onload = () => {
    loadServices();
    loadCategories();
    loadOfficers();
    loadAds();
};
