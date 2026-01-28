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
                <td style="padding:8px; border:1px solid #e0e0e0; font-size:11px;">${it.timestamp || '-'}</td>
            </tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    } catch (err) {
        console.error(err);
    }
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
