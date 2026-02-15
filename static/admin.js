document.getElementById("login-form").onsubmit = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const res = await fetch('/admin/login', { method: 'POST', body: form });
    if (res.redirected) {
        window.location = res.url;
    } else {
        loadDashboard();
    }
};

let currentTab = 'overview';

function showTab(tabName) {
    currentTab = tabName;
    
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.style.borderBottomColor = 'transparent';
        btn.style.color = '#666';
        btn.style.fontWeight = '500';
    });
    
    // Show selected tab
    document.getElementById(`tab-content-${tabName}`).style.display = 'block';
    
    // Activate button
    const activeBtn = document.getElementById(`tab-${tabName}`);
    activeBtn.style.borderBottomColor = '#0b3b8c';
    activeBtn.style.color = '#0b3b8c';
    activeBtn.style.fontWeight = '600';
    
    // Load tab-specific data
    if (tabName === 'subcategories') {
        loadSubcategoryReport();
    } else if (tabName === 'crud') {
        loadCategoriesForCRUD();
        loadServicesList();
    }
}

// ==================== CRUD FUNCTIONS ====================

let allCategories = [];
let allServices = [];

async function loadCategoriesForCRUD() {
    try {
        const res = await fetch('/api/categories');
        allCategories = await res.json();
        
        // Populate category filter
        const filterCat = document.getElementById('filter-category');
        const serviceCat = document.getElementById('service-category');
        
        filterCat.innerHTML = '<option value="">All Categories</option>';
        serviceCat.innerHTML = '<option value="">Select Category</option>';
        
        allCategories.forEach(cat => {
            filterCat.innerHTML += `<option value="${cat.id}">${cat.name.en}</option>`;
            serviceCat.innerHTML += `<option value="${cat.id}">${cat.name.en}</option>`;
        });
    } catch (err) {
        console.error('Error loading categories:', err);
    }
}

function loadSubcategoriesForForm() {
    const catId = document.getElementById('service-category').value;
    const subSelect = document.getElementById('service-subcategory');
    
    subSelect.innerHTML = '<option value="">Select Subcategory</option>';
    
    if (!catId) return;
    
    const category = allCategories.find(c => c.id === catId);
    if (category && category.subcategories) {
        category.subcategories.forEach(sub => {
            subSelect.innerHTML += `<option value="${sub.id}">${sub.name.en}</option>`;
        });
    }
}

async function loadServicesList() {
    try {
        const res = await fetch('/api/admin/items');
        allServices = await res.json();
        
        // Apply filters
        const filterCat = document.getElementById('filter-category').value;
        const filterSub = document.getElementById('filter-subcategory').value;
        const filterSearch = document.getElementById('filter-search').value.toLowerCase();
        
        let filtered = allServices.filter(service => {
            if (filterCat && service.category_id !== filterCat) return false;
            if (filterSub && service.subcategory_id !== filterSub) return false;
            if (filterSearch && !service.title.en.toLowerCase().includes(filterSearch) && 
                !service.description.toLowerCase().includes(filterSearch)) return false;
            return true;
        });
        
        const tbody = document.getElementById('servicesTableBody');
        tbody.innerHTML = '';
        
        if (filtered.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#999;">No services found</td></tr>';
            return;
        }
        
        filtered.forEach(service => {
            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid #e0e0e0';
            row.innerHTML = `
                <td style="padding:12px; font-size:11px; color:#666;">${service.id}</td>
                <td style="padding:12px;">
                    <div style="font-weight:600; color:#333;">${service.title.en}</div>
                    <div style="font-size:11px; color:#999; margin-top:2px;">${service.description.substring(0, 60)}...</div>
                </td>
                <td style="padding:12px; font-size:12px;">${service.category_name}</td>
                <td style="padding:12px; font-size:12px;">${service.subcategory_name}</td>
                <td style="padding:12px; text-align:center;">
                    <span style="background:#e3f2fd; color:#1976d2; padding:4px 8px; border-radius:8px; font-size:11px; font-weight:600;">
                        ${service.fee}
                    </span>
                </td>
                <td style="padding:12px; text-align:center; font-size:12px;">${service.processingTime}</td>
                <td style="padding:12px; text-align:center;">
                    <span style="background:${service.status === 'active' ? '#e8f5e9' : '#ffebee'}; color:${service.status === 'active' ? '#2e7d32' : '#c62828'}; padding:4px 10px; border-radius:12px; font-size:11px; font-weight:600;">
                        ${service.status}
                    </span>
                </td>
                <td style="padding:12px; text-align:center;">
                    <button onclick='editService("${service.subcategory_id}", "${service.id}")' style="padding:6px 12px; background:#2196F3; color:white; border:none; border-radius:4px; cursor:pointer; margin-right:5px; font-size:11px;">✏️ Edit</button>
                    <button onclick='deleteService("${service.subcategory_id}", "${service.id}", "${service.title.en}")' style="padding:6px 12px; background:#f44336; color:white; border:none; border-radius:4px; cursor:pointer; font-size:11px;">🗑️ Delete</button>
                </td>
            `;
            tbody.appendChild(row);
        });
        
        // Update subcategory filter based on selected category
        if (filterCat) {
            const category = allCategories.find(c => c.id === filterCat);
            const filterSub = document.getElementById('filter-subcategory');
            filterSub.innerHTML = '<option value="">All Subcategories</option>';
            if (category && category.subcategories) {
                category.subcategories.forEach(sub => {
                    filterSub.innerHTML += `<option value="${sub.id}">${sub.name.en}</option>`;
                });
            }
        }
        
    } catch (err) {
        console.error('Error loading services:', err);
        document.getElementById('servicesTableBody').innerHTML = 
            '<tr><td colspan="8" style="text-align:center; padding:20px; color:#d32f2f;">Error loading services</td></tr>';
    }
}

function showAddServiceModal() {
    document.getElementById('modalTitle').textContent = 'Add New Service';
    document.getElementById('serviceForm').reset();
    document.getElementById('service-id').value = '';
    document.getElementById('service-status').value = 'active';
    document.getElementById('serviceModal').style.display = 'block';
}

function closeServiceModal() {
    document.getElementById('serviceModal').style.display = 'none';
}

async function editService(subcategoryId, serviceId) {
    const service = allServices.find(s => s.id === serviceId && s.subcategory_id === subcategoryId);
    if (!service) return;
    
    document.getElementById('modalTitle').textContent = 'Edit Service';
    document.getElementById('service-id').value = service.id;
    document.getElementById('service-subcategory-id').value = service.subcategory_id;
    document.getElementById('service-category').value = service.category_id;
    
    loadSubcategoriesForForm();
    
    setTimeout(() => {
        document.getElementById('service-subcategory').value = service.subcategory_id;
    }, 100);
    
    document.getElementById('service-title-en').value = service.title.en || '';
    document.getElementById('service-title-si').value = service.title.si || '';
    document.getElementById('service-title-ta').value = service.title.ta || '';
    document.getElementById('service-description').value = service.description || '';
    document.getElementById('service-fee').value = service.fee || '';
    document.getElementById('service-time').value = service.processingTime || '';
    document.getElementById('service-requirements').value = (service.requirements || []).join('\n');
    document.getElementById('service-status').value = service.status || 'active';
    
    document.getElementById('serviceModal').style.display = 'block';
}

async function saveService(event) {
    event.preventDefault();
    
    const serviceId = document.getElementById('service-id').value;
    const subcategoryId = document.getElementById('service-subcategory-id').value || document.getElementById('service-subcategory').value;
    
    const requirements = document.getElementById('service-requirements').value
        .split('\n')
        .filter(r => r.trim())
        .map(r => r.trim());
    
    const serviceData = {
        id: serviceId || `service_${Date.now()}`,
        title: {
            en: document.getElementById('service-title-en').value,
            si: document.getElementById('service-title-si').value || document.getElementById('service-title-en').value,
            ta: document.getElementById('service-title-ta').value || document.getElementById('service-title-en').value
        },
        description: document.getElementById('service-description').value,
        fee: document.getElementById('service-fee').value,
        processingTime: document.getElementById('service-time').value,
        requirements: requirements,
        status: document.getElementById('service-status').value,
        formFields: [
            {name: "fullName", type: "text", required: true},
            {name: "nic", type: "text", required: true},
            {name: "contactNumber", type: "tel", required: true},
            {name: "email", type: "email", required: true}
        ]
    };
    
    try {
        let res;
        if (serviceId) {
            // Update existing
            res = await fetch(`/api/admin/subcategory/${subcategoryId}/items/${serviceId}`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(serviceData)
            });
        } else {
            // Create new
            res = await fetch(`/api/admin/subcategory/${subcategoryId}/items`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(serviceData)
            });
        }
        
        const result = await res.json();
        
        if (res.ok) {
            alert(serviceId ? 'Service updated successfully!' : 'Service added successfully!');
            closeServiceModal();
            loadServicesList();
        } else {
            alert('Error: ' + (result.error || 'Failed to save service'));
        }
    } catch (err) {
        console.error('Error saving service:', err);
        alert('Error saving service. Please try again.');
    }
}

async function deleteService(subcategoryId, serviceId, serviceName) {
    if (!confirm(`Are you sure you want to delete "${serviceName}"?`)) return;
    
    try {
        const res = await fetch(`/api/admin/subcategory/${subcategoryId}/items/${serviceId}`, {
            method: 'DELETE'
        });
        
        if (res.ok) {
            alert('Service deleted successfully!');
            loadServicesList();
        } else {
            alert('Error deleting service');
        }
    } catch (err) {
        console.error('Error deleting service:', err);
        alert('Error deleting service. Please try again.');
    }
}

// ==================== PDF EXPORT ====================

async function exportSubcategoryReportPDF() {
    try {
        const res = await fetch('/api/admin/subcategory-report');
        const report = await res.json();
        
        // Open print dialog with formatted content
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
            <head>
                <title>Subcategory Report</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { color: #0b3b8c; border-bottom: 3px solid #0b3b8c; padding-bottom: 10px; }
                    .summary { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 20px 0; }
                    .summary-card { background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; }
                    .summary-card .label { font-size: 12px; color: #666; }
                    .summary-card .value { font-size: 24px; font-weight: bold; color: #0b3b8c; margin-top: 5px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; font-size: 12px; }
                    th { background: #0b3b8c; color: white; }
                    tr:nth-child(even) { background: #f9f9f9; }
                    .footer { margin-top: 30px; text-align: center; font-size: 11px; color: #999; }
                </style>
            </head>
            <body>
                <h1>📊 Subcategory Analytics Report</h1>
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                
                <div class="summary">
                    <div class="summary-card">
                        <div class="label">Total Subcategories</div>
                        <div class="value">${report.length}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Total Views</div>
                        <div class="value">${report.reduce((sum, r) => sum + r.total_views, 0).toLocaleString()}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Unique Users</div>
                        <div class="value">${report.reduce((sum, r) => sum + r.unique_users, 0).toLocaleString()}</div>
                    </div>
                    <div class="summary-card">
                        <div class="label">Total Items</div>
                        <div class="value">${report.reduce((sum, r) => sum + r.item_count, 0)}</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Category</th>
                            <th>Subcategory</th>
                            <th>Views</th>
                            <th>Users</th>
                            <th>Items</th>
                            <th>Top Age Group</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${report.map((item, index) => {
                            const topAge = Object.entries(item.age_groups).reduce((a, b) => a[1] > b[1] ? a : b)[0];
                            return `
                                <tr>
                                    <td>#${index + 1}</td>
                                    <td>${item.category_icon} ${item.category_name}</td>
                                    <td>${item.subcategory_name}</td>
                                    <td>${item.total_views}</td>
                                    <td>${item.unique_users}</td>
                                    <td>${item.item_count}</td>
                                    <td>${topAge}</td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>Citizen Services Portal - Administrative Report</p>
                    <p>This report is confidential and for internal use only</p>
                </div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    } catch (err) {
        console.error('Error generating PDF:', err);
        alert('Error generating PDF report');
    }
}

async function loadDashboard() {
    const dashEl = document.getElementById("dashboard");
    try {
        const r = await fetch('/api/admin/insights');
        if (r.status === 401) {
            document.getElementById("login-box").style.display = "block";
            dashEl.style.display = "none";
            return;
        }
        const data = await r.json();
        document.getElementById("login-box").style.display = "none";
        dashEl.style.display = "block";

        // Age Chart
        new Chart(document.getElementById("ageChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.age_groups),
                datasets: [{
                    label: 'Users by Age Group',
                    data: Object.values(data.age_groups),
                    backgroundColor: '#0b3b8c'
                }]
            },
            options: { responsive: true, plugins: { legend: { display: true } } }
        });

        // Job Chart
        new Chart(document.getElementById("jobChart"), {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.jobs).slice(0, 8),
                datasets: [{
                    label: 'Jobs',
                    data: Object.values(data.jobs).slice(0, 8),
                    backgroundColor: ['#0b3b8c', '#1e40af', '#2563eb', '#60a5fa', '#93c5fd', '#cbd5e1', '#e0e7ff', '#c7d2e0']
                }]
            },
            options: { responsive: true, plugins: { legend: { display: true } } }
        });

        // Service Chart
        new Chart(document.getElementById("serviceChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.services).slice(0, 10),
                datasets: [{
                    label: 'Services Accessed',
                    data: Object.values(data.services).slice(0, 10),
                    backgroundColor: '#1e40af'
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                plugins: { legend: { display: false } }
            }
        });

        // Desire Chart
        new Chart(document.getElementById("desireChart"), {
            type: 'pie',
            data: {
                labels: Object.keys(data.desires).slice(0, 8),
                datasets: [{
                    label: 'User Desires',
                    data: Object.values(data.desires).slice(0, 8),
                    backgroundColor: ['#2563eb', '#7c3aed', '#db2777', '#059669', '#d97706', '#0891b2', '#6366f1', '#8b5cf6']
                }]
            },
            options: { responsive: true, plugins: { legend: { display: true } } }
        });

        // Premium List
        const pl = document.getElementById("premiumList");
        if (data.premium_suggestions && data.premium_suggestions.length) {
            pl.innerHTML = data.premium_suggestions.map(p =>
                `<div style="padding:10px; background:#f0f9ff; border-left:3px solid #0b3b8c; margin:8px 0; border-radius:4px;">
                    <strong>User:</strong> ${p.user || 'Anonymous'} | 
                    <strong>Question:</strong> ${p.question || 'N/A'} | 
                    <strong>Count:</strong> ${p.count}
                </div>`
            ).join("");
        } else {
            pl.innerHTML = "<div style='padding:10px; color:#666;'>No repeated engagements yet.</div>";
        }

        // Engagements Table
        const res2 = await fetch('/api/admin/engagements');
        const items = await res2.json();
        const tbody = document.querySelector("#engTable tbody");
        tbody.innerHTML = "";
        items.slice(0, 50).forEach(it => {
            const row = `<tr>
                <td style="padding:8px; border:1px solid #e0e0e0;">${it.age || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0;">${it.job || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0;">${(it.desires || []).join(", ") || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0; font-size:11px;">${it.question_clicked || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0;">${it.service || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0; font-size:11px;">${it.category_id || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0; font-size:11px;">${it.subcategory_id || '-'}</td>
                <td style="padding:8px; border:1px solid #e0e0e0; font-size:11px;">${it.timestamp || '-'}</td>
            </tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadSubcategoryReport() {
    try {
        const res = await fetch('/api/admin/subcategory-report');
        const report = await res.json();
        
        // Update summary cards
        const totalSubcategories = report.length;
        const totalViews = report.reduce((sum, r) => sum + r.total_views, 0);
        const totalUsers = report.reduce((sum, r) => sum + r.unique_users, 0);
        const avgViews = totalSubcategories > 0 ? Math.round(totalViews / totalSubcategories) : 0;
        
        document.getElementById('total-subcategories').textContent = totalSubcategories;
        document.getElementById('total-views').textContent = totalViews.toLocaleString();
        document.getElementById('total-users').textContent = totalUsers.toLocaleString();
        document.getElementById('avg-views').textContent = avgViews;
        
        // Build table
        const tbody = document.getElementById('subcategoryTableBody');
        tbody.innerHTML = '';
        
        if (report.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; padding:20px; color:#999;">No data available</td></tr>';
            return;
        }
        
        report.forEach((item, index) => {
            // Find top age group
            const ageGroups = item.age_groups;
            const topAgeGroup = Object.entries(ageGroups).reduce((a, b) => a[1] > b[1] ? a : b)[0];
            
            // Get top job
            const topJob = item.top_jobs.length > 0 ? item.top_jobs[0][0] : '-';
            
            const row = document.createElement('tr');
            row.style.borderBottom = '1px solid #e0e0e0';
            row.innerHTML = `
                <td style="padding:12px; font-weight:600; color:#0b3b8c;">#${index + 1}</td>
                <td style="padding:12px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:20px;">${item.category_icon}</span>
                        <span style="font-size:11px; color:#666;">${item.category_name}</span>
                    </div>
                </td>
                <td style="padding:12px;">
                    <div style="font-weight:600; color:#333;">${item.subcategory_name}</div>
                    <div style="font-size:11px; color:#999; margin-top:2px;">
                        ${item.keywords.slice(0, 3).join(', ')}
                    </div>
                </td>
                <td style="padding:12px; text-align:center;">
                    <span style="background:#e3f2fd; color:#1976d2; padding:4px 10px; border-radius:12px; font-weight:600; font-size:13px;">
                        ${item.total_views}
                    </span>
                </td>
                <td style="padding:12px; text-align:center;">
                    <span style="background:#f3e5f5; color:#7b1fa2; padding:4px 10px; border-radius:12px; font-weight:600; font-size:13px;">
                        ${item.unique_users}
                    </span>
                </td>
                <td style="padding:12px; text-align:center; color:#666;">${item.item_count}</td>
                <td style="padding:12px; font-size:12px;">
                    <span style="background:#fff3e0; color:#e65100; padding:3px 8px; border-radius:8px;">
                        ${topAgeGroup}
                    </span>
                </td>
                <td style="padding:12px; font-size:11px; color:#666;">${topJob.length > 20 ? topJob.substring(0, 20) + '...' : topJob}</td>
            `;
            tbody.appendChild(row);
        });
        
    } catch (err) {
        console.error('Error loading subcategory report:', err);
        document.getElementById('subcategoryTableBody').innerHTML = 
            '<tr><td colspan="8" style="text-align:center; padding:20px; color:#d32f2f;">Error loading report</td></tr>';
    }
}

function exportSubcategoryReport() {
    window.location = '/api/admin/export_subcategory_report';
}

document.getElementById("logoutBtn")?.addEventListener('click', async () => {
    await fetch('/api/admin/logout', { method: 'POST' });
    window.location = "/admin";
});

document.getElementById("exportCsv")?.addEventListener('click', () => {
    window.location = '/api/admin/export_csv';
});

// Rebuild AI Index
async function rebuildIndex() {
    const res = await fetch('/api/admin/build_index', { method: 'POST' });
    const data = await res.json();
    alert("AI Index Rebuilt Successfully!\n\nDocuments indexed: " + data.count + "\nFAISS Available: " + data.faiss);
    location.reload();
}

window.onload = loadDashboard;