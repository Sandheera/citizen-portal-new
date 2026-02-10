let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;
let expandedCategories = new Set();

// load categories with subcategories tree
async function loadCategories(){
    const res = await fetch("/api/categories");
    categories = await res.json();
    const el = document.getElementById("category-list");
    el.innerHTML = "";
    
    categories.forEach(c=>{
        const catDiv = document.createElement("div");
        catDiv.className = "cat-tree-item";
        
        // Category header with expand/collapse toggle
        const header = document.createElement("div");
        header.className = "cat-header";
        
        const toggle = document.createElement("span");
        toggle.className = "cat-toggle";
        toggle.textContent = "▶";
        toggle.style.cursor = "pointer";
        toggle.style.marginRight = "8px";
        toggle.style.fontSize = "12px";
        toggle.onclick = (e) => {
            e.stopPropagation();
            toggleCategory(c.id, toggle);
        };
        
        const icon = document.createElement("span");
        icon.textContent = c.icon || "📁";
        icon.style.marginRight = "8px";
        
        const name = document.createElement("span");
        name.textContent = c.name?.[lang] || c.name?.en || c.id;
        name.style.fontWeight = "bold";
        name.style.cursor = "pointer";
        name.onclick = () => selectCategory(c);
        
        header.appendChild(toggle);
        header.appendChild(icon);
        header.appendChild(name);
        catDiv.appendChild(header);
        
        // Subcategories container
        if(c.subcategories && c.subcategories.length > 0){
            const subDiv = document.createElement("div");
            subDiv.className = "cat-subcategories";
            subDiv.id = `subcat-${c.id}`;
            subDiv.style.display = "none";
            subDiv.style.marginLeft = "20px";
            subDiv.style.borderLeft = "2px solid #ddd";
            subDiv.style.paddingLeft = "10px";
            
            c.subcategories.forEach(sub => {
                const subItem = document.createElement("div");
                subItem.className = "subcat-item";
                subItem.style.padding = "8px 0";
                subItem.style.cursor = "pointer";
                subItem.style.borderRadius = "4px";
                subItem.style.paddingLeft = "8px";
                
                const subName = document.createElement("div");
                subName.textContent = `└ ${sub.name?.[lang] || sub.name?.en}`;
                subName.style.fontWeight = "500";
                
                const subCount = document.createElement("div");
                subCount.textContent = `${sub.itemCount || 0} items`;
                subCount.style.fontSize = "12px";
                subCount.style.color = "#666";
                subCount.style.marginTop = "2px";
                
                subItem.appendChild(subName);
                subItem.appendChild(subCount);
                
                subItem.onclick = () => selectSubcategory(c, sub);
                subItem.onmouseover = () => subItem.style.backgroundColor = "#f0f0f0";
                subItem.onmouseout = () => subItem.style.backgroundColor = "transparent";
                
                subDiv.appendChild(subItem);
            });
            
            catDiv.appendChild(subDiv);
        }
        
        el.appendChild(catDiv);
    });
    
    // load ads
    loadAds();
}

function toggleCategory(catId, toggleEl){
    const subDiv = document.getElementById(`subcat-${catId}`);
    if(subDiv){
        if(expandedCategories.has(catId)){
            subDiv.style.display = "none";
            toggleEl.textContent = "▶";
            expandedCategories.delete(catId);
        } else {
            subDiv.style.display = "block";
            toggleEl.textContent = "▼";
            expandedCategories.add(catId);
        }
    }
}

function selectCategory(cat){
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("q-title").innerText = "Select a subcategory";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
}

function selectSubcategory(cat, sub){
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en;
    const subList = document.getElementById("sub-list");
    subList.innerHTML = "";
    
    const header = document.createElement("div");
    header.style.fontWeight = "bold";
    header.style.marginBottom = "10px";
    header.style.color = cat.color || "#333";
    header.textContent = sub.name?.[lang] || sub.name?.en;
    subList.appendChild(header);
    
    const desc = document.createElement("p");
    desc.textContent = sub.description || "";
    desc.style.fontSize = "14px";
    desc.style.color = "#666";
    desc.style.marginBottom = "15px";
    subList.appendChild(desc);
    
    const itemsText = document.createElement("p");
    itemsText.innerHTML = `<strong>Available items:</strong> ${sub.itemCount || 0}`;
    subList.appendChild(itemsText);
    
    if(sub.keywords && sub.keywords.length > 0){
        const keywordsDiv = document.createElement("div");
        keywordsDiv.style.marginTop = "10px";
        const kLabel = document.createElement("strong");
        kLabel.textContent = "Keywords: ";
        keywordsDiv.appendChild(kLabel);
        const kSpan = document.createElement("span");
        kSpan.textContent = sub.keywords.join(", ");
        kSpan.style.fontSize = "14px";
        kSpan.style.color = "#555";
        keywordsDiv.appendChild(kSpan);
        subList.appendChild(keywordsDiv);
    }
    
    document.getElementById("q-title").innerText = `${sub.name?.[lang] || sub.name?.en} - Details`;
}

async function loadMinistriesInCategory(cat){
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;
    
    if(cat.ministry_ids && cat.ministry_ids.length){
        for(let id of cat.ministry_ids){
            const r = await fetch(`/api/service/${id}`);
            const s = await r.json();
            if(s && s.subservices){
                s.subservices.forEach(sub=>{
                    let li = document.createElement("li");
                    li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                    li.onclick = ()=> loadQuestions(s, sub);
                    document.getElementById("sub-list").appendChild(li);
                });
            }
        }
    } else {
        const svcRes = await fetch("/api/services");
        const all = await svcRes.json();
        all.filter(s=>s.category===cat.id).forEach(s=>{
            s.subservices.forEach(sub=>{
                let li = document.createElement("li");
                li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                li.onclick = ()=> loadQuestions(s, sub);
                document.getElementById("sub-list").appendChild(li);
            });
        });
    }
}

async function loadQuestions(service, sub){
    currentServiceName = service.name?.[lang] || service.name?.en;
    currentSub = sub;
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";
    document.getElementById("q-title").innerText = sub.name?.[lang] || sub.name?.en || sub.id;
    (sub.questions || []).forEach(q=>{
        let li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en;
        li.onclick = ()=> showAnswer(service, sub, q);
        qList.appendChild(li);
    });
}

function showAnswer(service, sub, q){
    let html = `<h3>${q.q?.[lang] || q.q?.en}</h3>`;
    html += `<p>${q.answer?.[lang] || q.answer?.en}</p>`;
    if(q.downloads && q.downloads.length){
        html += `<p><b>Downloads:</b> ${q.downloads.map(d=>`<a href="${d}" target="_blank">${d.split("/").pop()}</a>`).join(", ")}</p>`;
    }
    if(q.location){
        html += `<p><b>Location:</b> <a href="${q.location}" target="_blank">View Map</a></p>`;
    }
    if(q.instructions){
        html += `<p><b>Instructions:</b> ${q.instructions}</p>`;
    }
    document.getElementById("answer-box").innerHTML = html;
    
    // log engagement
    fetch("/api/engagement", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
            user_id: profile_id,
            age: null,
            job: null,
            desires: [],
            question_clicked: q.q?.[lang] || q.q?.en,
            service: currentServiceName
        })
    });
}

// Chat UI
function openChat(){ document.getElementById("chat-panel").style.display = "block"; }
function closeChat(){ document.getElementById("chat-panel").style.display = "none"; }

async function sendChat(){
    const input = document.getElementById("chat-text");
    const text = input.value.trim();
    if(!text) return;
    
    appendChat("user", text);
    input.value = "";
    
    // call AI endpoint
    const res = await fetch("/api/ai/search", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({query: text, top_k: 5})
    });
    const data = await res.json();
    let reply = data.answer || "No answer found.";
    appendChat("bot", reply);
    
    // log engagement
    fetch("/api/engagement", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({user_id: profile_id, question_clicked: text, service: null})
    });
}

function appendChat(sender, text){
    const body = document.getElementById("chat-body");
    const div = document.createElement("div");
    div.className = "chat-msg " + (sender==="user"?"user-msg":"bot-msg");
    div.innerText = text;
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
}

// Autosuggest
let suggestTimer = null;
async function autosuggest(q){
    clearTimeout(suggestTimer);
    if(!q || q.length < 2){
        document.getElementById("suggestions").innerHTML = "";
        return;
    }
    suggestTimer = setTimeout(async ()=>{
        const res = await fetch(`/api/search/autosuggest?q=${encodeURIComponent(q)}`);
        const items = await res.json();
        const el = document.getElementById("suggestions");
        el.innerHTML = items.map(it=>`<div class="s-item" onclick='pickSuggestion(${JSON.stringify(JSON.stringify(it))})'>${it.name?.en || it.name}</div>`).join("");
    }, 250);
}

function pickSuggestion(serialized){
    const it = JSON.parse(serialized);
    if(it && it.subservices && it.subservices.length){
        loadQuestions(it, it.subservices[0]);
    }
    document.getElementById("suggestions").innerHTML = "";
}

// Language
function setLang(l){
    lang = l;
    loadCategories();
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
}

// Profile modal
function showProfileModal(){ document.getElementById("profile-modal").style.display = "block"; }
function profileNext(step){
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step+1}`).style.display = "block";
}
function profileBack(step){
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step-1}`).style.display = "block";
}

async function profileSubmit(){
    const data1 = {name: document.getElementById("p_name").value, age: document.getElementById("p_age").value};
    const data2 = {email: document.getElementById("p_email").value, phone: document.getElementById("p_phone").value};
    const data3 = {job: document.getElementById("p_job").value};
    
    let res = await fetch("/api/profile/step", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({email:data2.email, step:"basic", data:data1})
    });
    let j = await res.json();
    profile_id = j.profile_id || null;
    
    await fetch("/api/profile/step", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({profile_id: profile_id, step:"contact", data:data2})
    });
    
    await fetch("/api/profile/step", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({profile_id: profile_id, step:"employment", data:data3})
    });
    
    document.getElementById("profile-modal").style.display = "none";
}

// load ads
async function loadAds(){
    const res = await fetch("/api/ads");
    const ads = await res.json();
    const el = document.getElementById("ads-area");
    el.innerHTML = ads.map(a=>`<div class="ad-card"><a href="${a.link || '#'}"><h4>${a.title}</h4><p>${a.body || ''}</p></a></div>`).join("");
}

// initialize
window.onload = async ()=>{
    await loadCategories();
    const svcRes = await fetch("/api/services");
    services = await svcRes.json();
};
