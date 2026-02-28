let currentType = null;
let currentItem = null;
let expandedCategories = new Set();
let selectedCategory = null;

// Load and build category tree
async function loadCategoryTree() {
    const res = await fetch('/api/admin/categories');
    const categories = await res.json();
    const treeEl = document.getElementById('categoriesTree');
    
    if (!categories.length) {
        treeEl.innerHTML = '<p style="color:#999; font-size:12px;">No categories found</p>';
        return;
    }
    
    let treeHTML = '<ul class="category-tree">';
    
    for (const cat of categories) {
        const isExpanded = expandedCategories.has(cat.id);
        const isSelected = selectedCategory === cat.id;
        
        treeHTML += `
            <li class="tree-item">
                <button class="tree-toggle ${isSelected ? 'active' : ''}" 
                    onclick="toggleCategory('${cat.id}'); selectCategory('${cat.id}')">
                    ${cat.subcategories && cat.subcategories.length ? `
                        <span style="font-size:10px; margin-right:6px;">${isExpanded ? '▼' : '▶'}</span>
                    ` : '<span style="width:16px; display:inline-block;"></span>'}
                    <span class="tree-icon">${cat.icon || '📁'}</span>
                    <strong>${cat.name?.en || cat.id}</strong>
                </button>
                
                ${cat.subcategories && cat.subcategories.length ? `
                    <div class="tree-children ${isExpanded ? 'expanded' : ''}">
                        ${cat.subcategories.map(sub => `
                            <div class="tree-child-item" onclick="selectSubcategory('${cat.id}', '${sub.id}')">
                                <span class="tree-icon">└</span>
                                <strong>${sub.name?.en || sub.id}</strong>
                                ${sub.itemCount ? `<span style="float:right; color:#999; font-size:11px;">${sub.itemCount}</span>` : ''}
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </li>
        `;
    }
    
    treeHTML += '</ul>';
    treeEl.innerHTML = treeHTML;
}

function toggleCategory(catId) {
    if (expandedCategories.has(catId)) {
        expandedCategories.delete(catId);
    } else {
        expandedCategories.add(catId);
    }
    loadCategoryTree();
}

function selectCategory(catId) {
    selectedCategory = catId;
    loadCategoryTree();
}

function selectSubcategory(catId, subId) {
    selectedCategory = catId;
}

// Load Services
async function loadServices() {
    const res = await fetch('/api/admin/services');
    const services = await res.json();
    const el = document.getElementById('servicesList');
    el.innerHTML = services.length ? services.map(s => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; border-left:4px solid #0b3b8c;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <div>
                    <strong style="font-size:14px;">${s.name?.en || s.id}</strong>
                    <p style="margin:4px 0; font-size:12px; color:#666;">ID: ${s.id}</p>
                    ${s.category ? `<p style="margin:4px 0; font-size:11px; color:#0b3b8c;">Category: ${s.category}</p>` : ''}
                    ${s.description ? `<p style="margin:4px 0; font-size:12px; color:#555;">${s.description}</p>` : ''}
                </div>
                <button onclick="deleteService('${s.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
            </div>
            ${s.subservices && s.subservices.length ? `
                <div style="margin-top:12px; padding:8px; background:#ffffff; border-radius:4px; border-left:2px solid #0b3b8c;">
                    <strong style="font-size:12px; color:#0b3b8c;">Subservices:</strong>
                    ${s.subservices.map((sub, idx) => `
                        <div style="margin-top:8px; padding:8px; background:#f0f4f8; border-radius:4px;">
                            <p style="margin:0; font-size:12px;"><strong>${sub.name?.en || sub.id}</strong></p>
                            <p style="margin:2px 0; font-size:11px; color:#666;">ID: ${sub.id}</p>
                            ${sub.description ? `<p style="margin:4px 0; font-size:11px; color:#555;">${sub.description}</p>` : ''}
                            ${sub.questions && sub.questions.length ? `
                                <div style="margin-top:6px; font-size:10px; color:#0b3b8c;">
                                    📋 ${sub.questions.length} questions
                                </div>
                            ` : ''}
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('') : '<p>No services found.</p>';
}

// Load Officers
async function loadOfficers() {
    const res = await fetch('/api/admin/officers');
    const officers = await res.json();
    const el = document.getElementById('officersList');
    el.innerHTML = officers.length ? officers.map(o => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; border-left:4px solid #FF9800;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <strong style="font-size:14px; color:#FF9800;">${o.name}</strong>
                    <p style="margin:4px 0; font-size:12px; color:#FF9800;"><strong>${o.role}</strong></p>
                    <p style="margin:4px 0; font-size:11px; color:#666;">ID: ${o.id}</p>
                    ${o.email ? `<p style="margin:4px 0; font-size:11px;">📧 ${o.email}</p>` : ''}
                    ${o.phone ? `<p style="margin:4px 0; font-size:11px;">📱 ${o.phone}</p>` : ''}
                    ${o.department ? `<p style="margin:4px 0; font-size:11px;">🏢 Department: ${o.department}</p>` : ''}
                    ${o.bio ? `<p style="margin:4px 0; font-size:11px; color:#555;">${o.bio}</p>` : ''}
                    ${o.specialization ? `<p style="margin:4px 0; font-size:10px; color:#FF9800;">⭐ Specialization: ${o.specialization}</p>` : ''}
                </div>
                <button onclick="deleteOfficer('${o.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
            </div>
        </div>
    `).join('') : '<p>No officers found.</p>';
}

// Load Ads
async function loadAds() {
    const res = await fetch('/api/admin/ads');
    const ads = await res.json();
    const el = document.getElementById('adsList');
    el.innerHTML = ads.length ? ads.map(a => `
        <div style="padding:12px; background:#f8fafc; border-radius:6px; margin-bottom:8px; border-left:4px solid #4CAF50;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div style="flex:1;">
                    <strong style="font-size:14px;">${a.title}</strong>
                    <p style="margin:4px 0; font-size:12px; color:#666;">ID: ${a.id}</p>
                    ${a.body ? `<p style="margin:4px 0; font-size:12px; color:#555;">${a.body}</p>` : '<p style="margin:4px 0; font-size:12px; color:#999;">No description</p>'}
                    ${a.type ? `<p style="margin:4px 0; font-size:11px; color:#4CAF50;"><strong>Type:</strong> ${a.type}</p>` : ''}
                    ${a.targetAudience ? `<p style="margin:4px 0; font-size:11px; color:#4CAF50;"><strong>Target:</strong> ${Array.isArray(a.targetAudience) ? a.targetAudience.join(', ') : a.targetAudience}</p>` : ''}
                    ${a.link ? `<p style="margin:4px 0; font-size:11px;">🔗 <a href="${a.link}" target="_blank" style="color:#4CAF50;">Link</a></p>` : ''}
                    ${a.startDate ? `<p style="margin:4px 0; font-size:11px;">📅 Start: ${a.startDate}</p>` : ''}
                    ${a.endDate ? `<p style="margin:4px 0; font-size:11px;">📅 End: ${a.endDate}</p>` : ''}
                    ${a.priority ? `<p style="margin:4px 0; font-size:11px;">⚡ Priority: ${a.priority}</p>` : ''}
                </div>
                <button onclick="deleteAd('${a.id}')" style="padding:6px 12px; background:#d32f2f; color:white; border:none; border-radius:4px; cursor:pointer; font-size:12px;">Delete</button>
            </div>
        </div>
    `).join('') : '<p>No ads found.</p>';
}

// Form Functions
function showServiceForm() {
    currentType = 'service';
    currentItem = null;
    document.getElementById('formTitle').textContent = 'Add Service';
    document.getElementById('formFields').innerHTML = `
        <input type="text" id="id" placeholder="Service ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="name_en" placeholder="Service Name (English)" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="category" placeholder="Category" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="description" placeholder="Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:80px;"></textarea>
        <input type="text" id="contactEmail" placeholder="Contact Email" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="hotline" placeholder="Hotline" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="website" placeholder="Website URL" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="requirements" placeholder="Requirements (comma-separated)" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:60px;"></textarea>
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
        <textarea id="description" placeholder="Category Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:60px;"></textarea>
        <input type="text" id="icon" placeholder="Icon (emoji or icon code)" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="color" placeholder="Color (hex code, e.g. #2196F3)" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
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
        <input type="text" id="role" placeholder="Role/Position" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="department" placeholder="Department" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="email" id="email" placeholder="Email" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="tel" id="phone" placeholder="Phone Number" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="specialization" placeholder="Specialization/Expertise" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="bio" placeholder="Bio/Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:70px;"></textarea>
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
        <textarea id="body" placeholder="Description/Content" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:80px;"></textarea>
        <select id="type" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <option value="">Select Type</option>
            <option value="promotion">Promotion</option>
            <option value="training">Training Program</option>
            <option value="announcement">Announcement</option>
            <option value="event">Event</option>
            <option value="important">Important Notice</option>
        </select>
        <input type="url" id="link" placeholder="Link/URL" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="targetAudience" placeholder="Target Audience (comma-separated)" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="date" id="startDate" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="date" id="endDate" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <select id="priority" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;">
            <option value="">Select Priority</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
        </select>
    `;
    document.getElementById('formModal').style.display = 'flex';
}

function showSubcategoryForm(catId) {
    currentType = 'subcategory';
    currentItem = catId;
    document.getElementById('formTitle').textContent = 'Add Subcategory';
    document.getElementById('formFields').innerHTML = `
        <input type="hidden" id="parentId" value="${catId}" />
        <input type="text" id="id" placeholder="Subcategory ID" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="text" id="name_en" placeholder="Subcategory Name (English)" required style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <textarea id="description" placeholder="Description" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px; height:60px;"></textarea>
        <input type="text" id="keywords" placeholder="Keywords (comma-separated)" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
        <input type="number" id="itemCount" placeholder="Number of Items" min="0" style="width:100%; padding:8px; margin-bottom:10px; border:1px solid #cbd5e1; border-radius:6px;" />
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
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(inp => {
        if (inp.id !== 'parentId') {
            payload[inp.id] = inp.value;
        }
    });
    
    if (currentType === 'service') {
        payload.name = { en: payload.name_en };
        delete payload.name_en;
        if (payload.requirements) {
            payload.requirements = payload.requirements.split(',').map(r => r.trim()).filter(r => r);
        }
    } else if (currentType === 'category') {
        payload.name = { en: payload.name_en };
        delete payload.name_en;
        payload.subcategories = [];
    } else if (currentType === 'subcategory') {
        const parentId = document.getElementById('parentId').value;
        payload.name = { en: payload.name_en };
        delete payload.name_en;
        if (payload.keywords) {
            payload.keywords = payload.keywords.split(',').map(k => k.trim()).filter(k => k);
        }
        if (payload.itemCount) {
            payload.itemCount = parseInt(payload.itemCount);
        }
        
        const addRes = await fetch(`/api/admin/categories/add-subcategory`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parentId, subcategory: payload })
        });
        
        if (addRes.ok) {
            alert('Subcategory added successfully!');
            closeForm();
            loadCategoryTree();
        } else {
            alert('Error adding subcategory!');
        }
        return;
    } else if (currentType === 'ad') {
        if (payload.targetAudience) {
            payload.targetAudience = payload.targetAudience.split(',').map(a => a.trim()).filter(a => a);
        }
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
        loadCategoryTree();
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
    loadCategoryTree();
    loadServices();
    loadOfficers();
    loadAds();
};
