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