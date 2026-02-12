let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentCategory = null;
let currentSub = null;
let profile_id = null;
let expandedCategories = new Set();

/* LOAD CATEGORY TREE */
async function loadCategories(){
    const res = await fetch("/api/categories");
    categories = await res.json();
    const el = document.getElementById("category-list");
    el.innerHTML = "";

    categories.forEach(c=>{
        const catDiv = document.createElement("div");
        catDiv.className = "cat-tree-item";

        const header = document.createElement("div");
        header.className = "cat-header";

        const toggle = document.createElement("span");
        toggle.className = "cat-toggle";
        toggle.textContent = "▶";
        toggle.onclick = (e)=>{
            e.stopPropagation();
            toggleCategory(c.id, toggle);
        };

        const icon = document.createElement("span");
        icon.textContent = c.icon || "📁";
        icon.style.marginRight = "8px";

        const name = document.createElement("span");
        name.textContent = c.name?.[lang] || c.name?.en || c.id;
        name.style.cursor = "pointer";
        name.onclick = ()=> selectCategory(c);

        header.append(toggle, icon, name);
        catDiv.appendChild(header);

        if(c.subcategories?.length){
            const subDiv = document.createElement("div");
            subDiv.id = `subcat-${c.id}`;
            subDiv.className = "cat-subcategories";
            subDiv.style.display="none";

            c.subcategories.forEach(sub=>{
                const item=document.createElement("div");
                item.className="subcat-item";
                item.innerHTML=`
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span>▫ ${sub.name?.[lang]||sub.name?.en}</span>
                        <div class="subcount">${sub.itemCount||0}</div>
                    </div>
                `;
                item.onclick=()=>selectSubcategory(c,sub);
                subDiv.appendChild(item);
            });

            catDiv.appendChild(subDiv);
        }

        el.appendChild(catDiv);
    });

    loadAds();
}

function toggleCategory(id,toggle){
    const box=document.getElementById(`subcat-${id}`);
    if(!box) return;

    if(expandedCategories.has(id)){
        box.style.display="none";
        toggle.textContent="▶";
        expandedCategories.delete(id);
    }else{
        box.style.display="block";
        toggle.textContent="▼";
        expandedCategories.add(id);
    }
}

function selectCategory(cat){
    currentCategory = cat;
    currentSub = null;
    
    document.getElementById("sub-title").innerText=cat.name?.[lang]||cat.name?.en;
    document.getElementById("question-list").innerHTML="";
    document.getElementById("answer-box").innerHTML="";

    const list=document.getElementById("sub-list");
    list.innerHTML="";

    if(cat.subcategories?.length){
        cat.subcategories.forEach(sub=>{
            const li=document.createElement("li");
            li.innerHTML=`
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <b style="color: ${cat.color || '#0b3b8c'};">${sub.name?.[lang]||sub.name?.en}</b><br>
                        <small style="color: #666;">${sub.description||""}</small>
                    </div>
                    <span style="background: #e3f2fd; padding: 3px 8px; border-radius: 12px; font-size: 11px; color: #1976d2; font-weight: 500;">
                        ${sub.itemCount || 0} items
                    </span>
                </div>
            `;
            li.onclick=()=>selectSubcategory(cat,sub);
            list.appendChild(li);
        });
        document.getElementById("q-title").innerText="Select a subcategory";
    } else {
        list.innerHTML = "<li style='color: #999; text-align: center; padding: 20px;'>No subcategories available</li>";
        document.getElementById("q-title").innerText="No subcategories";
    }
    
    // Log engagement
    fetch("/api/engagement",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            user_id:profile_id,
            category_id:cat.id,
            service:cat.name?.en,
            source:"category_click"
        })
    });
}

function selectSubcategory(cat,sub){
    currentServiceName=cat.name?.en;
    currentCategory = cat;
    currentSub=sub;

    document.getElementById("q-title").innerText=sub.name?.[lang]||sub.name?.en;
    document.getElementById("question-list").innerHTML="";

    let html=`
        <div class="info-card" style="border-left: 4px solid ${cat.color || '#0b3b8c'};">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 15px;">
                <span style="font-size: 32px;">${cat.icon || '📁'}</span>
                <div>
                    <h2 style="color:${cat.color||"#333"}; margin: 0;">${sub.name?.[lang]||sub.name?.en}</h2>
                    <small style="color: #666;">${cat.name?.[lang] || cat.name?.en}</small>
                </div>
            </div>
            
            <p style="line-height: 1.6; color: #444; margin: 15px 0;">${sub.description||""}</p>

            <div class="info-section">
                <div style="display: inline-block; background: #f0f9ff; padding: 8px 16px; border-radius: 8px; border: 1px solid #bfdbfe;">
                    <b style="color: #0369a1;">Available Items:</b> 
                    <span style="color: #0c4a6e; font-weight: 600;">${sub.itemCount||0}</span>
                </div>
            </div>
    `;

    if(sub.keywords?.length){
        html+=`
            <div class="info-section">
                <b style="color: #475569;">Keywords:</b> 
                <div style="margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px;">
                    ${sub.keywords.map(k => 
                        `<span style="background: #e0e7ff; color: #4338ca; padding: 4px 10px; border-radius: 12px; font-size: 12px;">${k}</span>`
                    ).join('')}
                </div>
            </div>
        `;
    }

    html+=`
            <div class="info-section" style="margin-top: 20px;">
                <button onclick="askAboutCurrent()" style="
                    width: 100%;
                    padding: 12px 20px;
                    background: linear-gradient(135deg, ${cat.color || '#0b3b8c'} 0%, ${adjustColor(cat.color || '#0b3b8c', -20)} 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 8px rgba(11, 59, 140, 0.2);
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(11, 59, 140, 0.3)';"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(11, 59, 140, 0.2)';">
                    💬 Ask AI about this service
                </button>
            </div>
        </div>
    `;

    document.getElementById("answer-box").innerHTML=html;

    // Log engagement
    fetch("/api/engagement",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            user_id:profile_id,
            service:currentServiceName,
            category_id:cat.id,
            subcategory_id:sub.id,
            question_clicked:sub.name?.en,
            source:"subcategory"
        })
    });
}

// Helper function to adjust color brightness
function adjustColor(color, amount) {
    const clamp = (val) => Math.min(255, Math.max(0, val));
    const num = parseInt(color.replace("#", ""), 16);
    const r = clamp((num >> 16) + amount);
    const g = clamp(((num >> 8) & 0x00FF) + amount);
    const b = clamp((num & 0x0000FF) + amount);
    return "#" + ((r << 16) | (g << 8) | b).toString(16).padStart(6, '0');
}

async function askAboutCurrent(){
    if(!currentSub) return;
    openChat();
    const questionText = `Tell me about ${currentSub.name?.en} in ${currentCategory?.name?.en}`;
    document.getElementById("chat-text").value = questionText;
    sendChat();
}

/* CHAT */
function openChat(){
    document.getElementById("chat-panel").style.display="flex";
}

function closeChat(){
    document.getElementById("chat-panel").style.display="none";
}

async function sendChat(){
    const input=document.getElementById("chat-text");
    const text=input.value.trim();
    if(!text) return;

    appendChat("user",text);
    input.value="";

    // Show typing indicator
    const typingDiv = document.createElement("div");
    typingDiv.className = "chat-msg bot-msg typing-indicator";
    typingDiv.innerHTML = "<span>●</span><span>●</span><span>●</span>";
    typingDiv.id = "typing-indicator";
    document.getElementById("chat-body").appendChild(typingDiv);

    try {
        const res = await fetch("/api/ai/search",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({query:text, top_k:5})
        });
        const data = await res.json();
        
        // Remove typing indicator
        document.getElementById("typing-indicator")?.remove();
        
        appendChat("bot", data.answer || "No answer found.");
        
        // If results include subcategories, show quick action buttons
        if(data.results && data.results.length > 0) {
            const quickActions = document.createElement("div");
            quickActions.className = "chat-quick-actions";
            data.results.slice(0, 3).forEach(result => {
                const btn = document.createElement("button");
                btn.className = "quick-action-btn";
                btn.textContent = result.metadata?.subcategory_name || "View";
                btn.onclick = () => {
                    // Find and select this subcategory
                    const cat = categories.find(c => c.id === result.category_id);
                    const sub = cat?.subcategories?.find(s => s.id === result.subcategory_id);
                    if(cat && sub) {
                        selectSubcategory(cat, sub);
                        closeChat();
                    }
                };
                quickActions.appendChild(btn);
            });
            document.getElementById("chat-body").appendChild(quickActions);
        }
    } catch(err) {
        document.getElementById("typing-indicator")?.remove();
        appendChat("bot", "Sorry, I encountered an error. Please try again.");
        console.error(err);
    }
}

function appendChat(sender,text){
    const body=document.getElementById("chat-body");
    const div=document.createElement("div");
    div.className="chat-msg "+(sender==="user"?"user-msg":"bot-msg");
    
    // Format markdown-like text
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>');
    
    div.innerHTML = formattedText;
    body.appendChild(div);
    body.scrollTop=body.scrollHeight;
}

async function loadAds(){
    const res=await fetch("/api/ads");
    const ads=await res.json();
    const adsArea = document.getElementById("ads-area");
    
    if(ads.length === 0) {
        adsArea.innerHTML = "<div style='text-align: center; color: rgba(255,255,255,0.6); font-size: 12px; padding: 10px;'>No announcements</div>";
        return;
    }
    
    adsArea.innerHTML = ads.map(a=>`
        <div class="ad-card">
            <a href="${a.link||'#'}" target="_blank">
                <h4 style="margin: 0 0 6px 0; font-size: 13px;">${a.title}</h4>
                <p style="margin: 0; font-size: 11px; opacity: 0.9;">${a.body||''}</p>
            </a>
        </div>
    `).join("");
}

// Search functionality
async function performSearch() {
    const query = document.getElementById("search-input").value.trim();
    if(!query) return;
    
    openChat();
    document.getElementById("chat-text").value = query;
    sendChat();
}

// Allow Enter key to send chat
document.addEventListener('DOMContentLoaded', () => {
    const chatInput = document.getElementById("chat-text");
    if(chatInput) {
        chatInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChat();
            }
        });
    }
    
    const searchInput = document.getElementById("search-input");
    if(searchInput) {
        searchInput.addEventListener('keypress', (e) => {
            if(e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }
});

function setLang(l){
    lang=l;
    loadCategories();
    
    // Update all visible text
    if(currentCategory) selectCategory(currentCategory);
    if(currentSub && currentCategory) selectSubcategory(currentCategory, currentSub);
}

// Auto-suggest for search (optional enhancement)
let suggestTimeout;
async function autosuggest(value) {
    clearTimeout(suggestTimeout);
    
    if(!value || value.length < 2) {
        document.getElementById("suggestions").innerHTML = "";
        return;
    }
    
    suggestTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`/api/search/autosuggest?q=${encodeURIComponent(value)}`);
            const results = await res.json();
            
            const suggestDiv = document.getElementById("suggestions");
            if(results.length === 0) {
                suggestDiv.innerHTML = "";
                return;
            }
            
            suggestDiv.innerHTML = results.slice(0, 5).map(r => {
                const icon = r.type === "category" ? r.icon : r.parentIcon || "▫";
                const label = r.name?.en || r.name;
                const parent = r.type === "subcategory" ? ` (${r.parentCategory?.en || ""})` : "";
                
                return `<div class="s-item" onclick="handleSuggestionClick('${r.type}', '${r.id}')">
                    ${icon} ${label}${parent}
                </div>`;
            }).join("");
        } catch(err) {
            console.error("Autosuggest error:", err);
        }
    }, 300);
}

function handleSuggestionClick(type, id) {
    if(type === "category") {
        const cat = categories.find(c => c.id === id);
        if(cat) {
            selectCategory(cat);
            // Expand the category in sidebar
            if(!expandedCategories.has(id)) {
                const toggle = document.querySelector(`#subcat-${id}`).previousElementSibling?.querySelector('.cat-toggle');
                if(toggle) toggleCategory(id, toggle);
            }
        }
    } else if(type === "subcategory") {
        // Find parent category
        for(const cat of categories) {
            const sub = cat.subcategories?.find(s => s.id === id);
            if(sub) {
                selectSubcategory(cat, sub);
                // Expand the category in sidebar
                if(!expandedCategories.has(cat.id)) {
                    const toggle = document.querySelector(`#subcat-${cat.id}`).previousElementSibling?.querySelector('.cat-toggle');
                    if(toggle) toggleCategory(cat.id, toggle);
                }
                break;
            }
        }
    }
    
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("chat-text").value = "";
}

window.onload=async()=>{
    await loadCategories();
    
    // Auto-select first category if available
    if(categories.length > 0) {
        selectCategory(categories[0]);
    }
};