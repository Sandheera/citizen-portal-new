let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentCategory = null;
let currentSub = null;
// Generate a unique user ID if not logged in
let profile_id = localStorage.getItem('user_id') || 'user_' + Math.random().toString(36).substr(2, 9);
// Save for future visits
localStorage.setItem('user_id', profile_id);
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

function selectSubcategory(cat, sub){
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
                <button onclick="loadSubcategoryItems('${sub.id}')" style="
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
                    margin-bottom: 10px;
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(11, 59, 140, 0.3)';"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(11, 59, 140, 0.2)';">
                    📋 View All Services (${sub.itemCount || 0})
                </button>
                
                <button onclick="askAboutCurrent()" style="
                    width: 100%;
                    padding: 12px 20px;
                    background: white;
                    color: ${cat.color || '#0b3b8c'};
                    border: 2px solid ${cat.color || '#0b3b8c'};
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                " onmouseover="this.style.background='${cat.color || '#0b3b8c'}'; this.style.color='white';"
                   onmouseout="this.style.background='white'; this.style.color='${cat.color || '#0b3b8c'}';">
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

// Load and display service items for a subcategory
async function loadSubcategoryItems(subcategoryId) {
    try {
        const response = await fetch(`/api/subcategory/${subcategoryId}/items`);
        const data = await response.json();
        
        const items = data.items || [];
        
        if(items.length === 0) {
            document.getElementById("question-list").innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <div style="font-size: 48px; margin-bottom: 10px;">📭</div>
                    <div style="font-size: 16px;">No services available yet</div>
                    <div style="font-size: 12px; margin-top: 5px;">Check back soon for updates</div>
                </div>
            `;
            return;
        }
        
        let itemsHtml = '<div style="display: grid; gap: 15px;">';
        
        items.forEach(item => {
            const processingTime = item.processingTime || "Varies";
            const fee = item.fee || "Free";
            const requirements = item.requirements || [];
            
            itemsHtml += `
                <div class="service-item-card" style="
                    background: white;
                    border: 1px solid #e2e8f0;
                    border-radius: 10px;
                    padding: 18px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                " onmouseover="this.style.boxShadow='0 4px 12px rgba(0,0,0,0.1)'; this.style.transform='translateY(-2px)';"
                   onmouseout="this.style.boxShadow='0 1px 3px rgba(0,0,0,0.05)'; this.style.transform='translateY(0)';"
                   onclick="viewServiceItem('${subcategoryId}', '${item.id}')">
                    
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                        <h3 style="margin: 0; color: #0f172a; font-size: 16px; flex: 1;">
                            ${item.title?.[lang] || item.title?.en || item.title}
                        </h3>
                        <span style="background: ${fee === 'Free' ? '#dcfce7' : '#fef3c7'}; 
                                     color: ${fee === 'Free' ? '#166534' : '#92400e'}; 
                                     padding: 4px 10px; 
                                     border-radius: 12px; 
                                     font-size: 11px; 
                                     font-weight: 600;
                                     white-space: nowrap;
                                     margin-left: 10px;">
                            ${fee}
                        </span>
                    </div>
                    
                    <p style="color: #64748b; font-size: 13px; line-height: 1.5; margin-bottom: 12px;">
                        ${item.description?.[lang] || item.description?.en || item.description || ""}
                    </p>
                    
                    <div style="display: flex; gap: 15px; flex-wrap: wrap; font-size: 12px; color: #64748b;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span>⏱️</span>
                            <span>${processingTime}</span>
                        </div>
                        ${requirements.length > 0 ? `
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <span>📋</span>
                            <span>${requirements.length} requirements</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
            `;
        });
        
        itemsHtml += '</div>';
        
        document.getElementById("question-list").innerHTML = itemsHtml;
        
    } catch(error) {
        console.error("Error loading items:", error);
        document.getElementById("question-list").innerHTML = `
            <div style="text-align: center; padding: 40px; color: #ef4444;">
                <div style="font-size: 48px; margin-bottom: 10px;">⚠️</div>
                <div style="font-size: 16px;">Error loading services</div>
                <div style="font-size: 12px; margin-top: 5px;">Please try again later</div>
            </div>
        `;
    }
}

// View detailed service item
async function viewServiceItem(subcategoryId, itemId) {
    try {
        const response = await fetch(`/api/subcategory/${subcategoryId}/items/${itemId}`);
        const data = await response.json();
        
        const item = data.item;
        const category = data.category;
        
        let detailHtml = `
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); 
                        border-radius: 12px; 
                        padding: 25px; 
                        border-left: 4px solid ${category.color || '#0b3b8c'};
                        box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
                
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                    <span style="font-size: 36px;">${category.icon || '📁'}</span>
                    <div>
                        <h2 style="margin: 0; color: ${category.color || '#333'}; font-size: 22px;">
                            ${item.title?.[lang] || item.title?.en || item.title}
                        </h2>
                        <small style="color: #64748b;">${data.subcategory.name?.[lang] || data.subcategory.name?.en}</small>
                    </div>
                </div>
                
                <p style="line-height: 1.7; color: #475569; margin-bottom: 20px;">
                    ${item.description?.[lang] || item.description?.en || item.description || ""}
                </p>
        `;
        
        // Requirements
        if(item.requirements && item.requirements.length > 0) {
            detailHtml += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #0f172a; margin-bottom: 10px; font-size: 15px;">📋 Requirements:</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${item.requirements.map(req => `
                            <li style="padding: 8px 12px; 
                                       background: #f8fafc; 
                                       margin-bottom: 6px; 
                                       border-radius: 6px; 
                                       border-left: 3px solid ${category.color || '#0b3b8c'};
                                       font-size: 13px;">
                                ✓ ${req}
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }
        
        // Details grid
        detailHtml += `
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                        gap: 15px; 
                        margin-bottom: 20px;">
                
                <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; border: 1px solid #bae6fd;">
                    <div style="font-size: 11px; color: #0369a1; font-weight: 600; margin-bottom: 4px;">FEE</div>
                    <div style="font-size: 16px; color: #0c4a6e; font-weight: 700;">${item.fee || 'Free'}</div>
                </div>
                
                <div style="background: #f0fdf4; padding: 12px; border-radius: 8px; border: 1px solid #bbf7d0;">
                    <div style="font-size: 11px; color: #166534; font-weight: 600; margin-bottom: 4px;">PROCESSING TIME</div>
                    <div style="font-size: 16px; color: #15803d; font-weight: 700;">${item.processingTime || 'Varies'}</div>
                </div>
        `;
        
        if(item.location) {
            detailHtml += `
                <div style="background: #fef3c7; padding: 12px; border-radius: 8px; border: 1px solid #fde68a;">
                    <div style="font-size: 11px; color: #92400e; font-weight: 600; margin-bottom: 4px;">LOCATION</div>
                    <div style="font-size: 13px; color: #78350f; font-weight: 600;">${item.location}</div>
                </div>
            `;
        }
        
        detailHtml += `</div>`;
        
        // Downloads
        if(item.downloads && item.downloads.length > 0) {
            detailHtml += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #0f172a; margin-bottom: 10px; font-size: 15px;">📥 Downloads:</h4>
                    <div style="display: flex; flex-wrap: wrap; gap: 10px;">
                        ${item.downloads.map(doc => `
                            <a href="${doc.url}" 
                               download="${doc.name}"
                               style="display: inline-flex; 
                                      align-items: center; 
                                      gap: 6px;
                                      padding: 8px 14px; 
                                      background: ${category.color || '#0b3b8c'}; 
                                      color: white; 
                                      border-radius: 6px; 
                                      text-decoration: none; 
                                      font-size: 13px;
                                      font-weight: 500;
                                      transition: all 0.2s;">
                                📄 ${doc.name}
                            </a>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        // Instructions
        if(item.instructions) {
            detailHtml += `
                <div style="margin-bottom: 20px;">
                    <h4 style="color: #0f172a; margin-bottom: 10px; font-size: 15px;">📝 How to Apply:</h4>
                    <div style="background: #f8fafc; 
                                padding: 15px; 
                                border-radius: 8px; 
                                border-left: 3px solid ${category.color || '#0b3b8c'};
                                line-height: 1.6;
                                color: #475569;
                                font-size: 13px;">
                        ${item.instructions}
                    </div>
                </div>
            `;
        }
        
        // Action buttons
        detailHtml += `
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button onclick="loadSubcategoryItems('${subcategoryId}')" 
                        style="flex: 1; 
                               padding: 12px; 
                               background: white; 
                               color: ${category.color || '#0b3b8c'}; 
                               border: 2px solid ${category.color || '#0b3b8c'}; 
                               border-radius: 8px; 
                               font-weight: 600; 
                               cursor: pointer;
                               transition: all 0.2s;">
                    ← Back to List
                </button>
                <button onclick="applyForService('${itemId}')" 
                        style="flex: 1; 
                               padding: 12px; 
                               background: ${category.color || '#0b3b8c'}; 
                               color: white; 
                               border: none; 
                               border-radius: 8px; 
                               font-weight: 600; 
                               cursor: pointer;
                               transition: all 0.2s;">
                    Apply Now →
                </button>
            </div>
        `;
        
        detailHtml += `</div>`;
        
        document.getElementById("answer-box").innerHTML = detailHtml;
        
    } catch(error) {
        console.error("Error viewing service item:", error);
    }
}

// Apply for service (placeholder)
function applyForService(itemId) {
    alert("Application feature coming soon! Service ID: " + itemId);
    // This would open an application form or redirect to application page
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

// Load and display service items for a subcategory
async function loadSubcategoryItems(subcategoryId) {
    try {
        const res = await fetch(`/api/subcategory/${subcategoryId}/items`);
        const items = await res.json();
        
        const qTitle = document.getElementById("q-title");
        const questionList = document.getElementById("question-list");
        const answerBox = document.getElementById("answer-box");
        
        qTitle.innerText = "Available Services";
        answerBox.innerHTML = "";
        
        if(items.length === 0) {
            questionList.innerHTML = `
                <div style="text-align: center; padding: 40px; color: #999;">
                    <p style="font-size: 16px;">📋 No services available in this category yet.</p>
                    <p style="font-size: 14px;">Please check back later or contact support.</p>
                </div>
            `;
            return;
        }
        
        questionList.innerHTML = items.map(item => `
            <li onclick="showItemDetails('${subcategoryId}', '${item.id}')" style="
                cursor: pointer;
                padding: 14px;
                margin: 10px 0;
                background: white;
                border-radius: 8px;
                border-left: 3px solid ${currentCategory?.color || '#0b3b8c'};
                transition: all 0.2s ease;
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0; color: #0f172a; font-size: 15px;">
                            ${item.title?.[lang] || item.title?.en}
                        </h4>
                        <p style="margin: 0; font-size: 13px; color: #64748b; line-height: 1.4;">
                            ${item.description || ''}
                        </p>
                        <div style="margin-top: 8px; display: flex; gap: 12px; font-size: 12px; color: #94a3b8;">
                            <span>💰 ${item.fee}</span>
                            <span>⏱️ ${item.processingTime}</span>
                        </div>
                    </div>
                    <div style="background: #f0f9ff; color: #0369a1; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                        Apply →
                    </div>
                </div>
            </li>
        `).join('');
        
    } catch(err) {
        console.error('Error loading items:', err);
    }
}

// Show detailed item information and application form
async function showItemDetails(subcategoryId, itemId) {
    try {
        const res = await fetch(`/api/subcategory/${subcategoryId}/items/${itemId}`);
        const item = await res.json();
        
        const answerBox = document.getElementById("answer-box");
        
        let requirementsHtml = '';
        if(item.requirements && item.requirements.length > 0) {
            requirementsHtml = `
                <div class="info-section">
                    <h4 style="color: #0f172a; margin: 0 0 10px 0;">📋 Requirements:</h4>
                    <ul style="margin: 0; padding-left: 20px; color: #475569;">
                        ${item.requirements.map(req => `<li style="margin: 5px 0;">${req}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let formHtml = '';
        if(item.formFields && item.formFields.length > 0) {
            formHtml = `
                <div class="info-section">
                    <h4 style="color: #0f172a; margin: 0 0 15px 0;">📝 Application Form:</h4>
                    <form id="application-form" onsubmit="submitApplication(event, '${subcategoryId}', '${itemId}')">
                        ${item.formFields.map(field => `
                            <div style="margin-bottom: 12px;">
                                <label style="display: block; margin-bottom: 5px; color: #334155; font-size: 13px; font-weight: 500;">
                                    ${field.name}${field.required ? ' *' : ''}
                                </label>
                                <input 
                                    type="${field.type || 'text'}" 
                                    name="${field.name}" 
                                    ${field.required ? 'required' : ''}
                                    style="
                                        width: 100%;
                                        padding: 10px 12px;
                                        border: 2px solid #e2e8f0;
                                        border-radius: 6px;
                                        font-size: 14px;
                                        transition: all 0.2s;
                                    "
                                    onfocus="this.style.borderColor='${currentCategory?.color || '#0b3b8c'}'"
                                    onblur="this.style.borderColor='#e2e8f0'"
                                />
                            </div>
                        `).join('')}
                        <button type="submit" style="
                            width: 100%;
                            padding: 12px 20px;
                            margin-top: 10px;
                            background: linear-gradient(135deg, ${currentCategory?.color || '#0b3b8c'} 0%, ${adjustColor(currentCategory?.color || '#0b3b8c', -20)} 100%);
                            color: white;
                            border: none;
                            border-radius: 8px;
                            font-size: 14px;
                            font-weight: 600;
                            cursor: pointer;
                            transition: all 0.3s;
                        ">
                            ✅ Submit Application
                        </button>
                    </form>
                </div>
            `;
        }
        
        answerBox.innerHTML = `
            <div class="info-card" style="border-left: 4px solid ${currentCategory?.color || '#0b3b8c'};">
                <h2 style="color: ${currentCategory?.color || '#333'}; margin: 0 0 10px 0;">
                    ${item.title?.[lang] || item.title?.en}
                </h2>
                
                <p style="color: #475569; line-height: 1.6; margin: 0 0 15px 0;">
                    ${item.description}
                </p>
                
                <div style="display: flex; gap: 20px; margin: 15px 0;">
                    <div style="flex: 1; background: #f0fdf4; padding: 12px; border-radius: 8px; border-left: 3px solid #22c55e;">
                        <div style="font-size: 11px; color: #15803d; font-weight: 600; margin-bottom: 4px;">FEE</div>
                        <div style="font-size: 18px; color: #166534; font-weight: 700;">${item.fee}</div>
                    </div>
                    <div style="flex: 1; background: #fef3c7; padding: 12px; border-radius: 8px; border-left: 3px solid #f59e0b;">
                        <div style="font-size: 11px; color: #b45309; font-weight: 600; margin-bottom: 4px;">PROCESSING TIME</div>
                        <div style="font-size: 18px; color: #92400e; font-weight: 700;">${item.processingTime}</div>
                    </div>
                </div>
                
                ${requirementsHtml}
                ${formHtml}
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
                    <button onclick="loadSubcategoryItems('${subcategoryId}')" style="
                        padding: 10px 16px;
                        background: #f1f5f9;
                        color: #475569;
                        border: none;
                        border-radius: 6px;
                        font-size: 13px;
                        cursor: pointer;
                    ">
                        ← Back to all services
                    </button>
                </div>
            </div>
        `;
        
    } catch(err) {
        console.error('Error loading item details:', err);
    }
}

// Submit application form
async function submitApplication(event, subcategoryId, itemId) {
    event.preventDefault();
    
    console.log('🔍 Submitting application...', {subcategoryId, itemId});
    
    const form = event.target;
    const formData = new FormData(form);
    const data = {};
    
    formData.forEach((value, key) => {
        data[key] = value;
    });
    
    console.log('📝 Form data:', data);
    console.log('👤 User ID:', profile_id);
    
    try {
        const url = `/api/subcategory/${subcategoryId}/items/${itemId}/apply`;
        console.log('🌐 Sending to:', url);
        
        const res = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                user_id: profile_id,
                data: data
            })
        });
        
        console.log('📨 Response status:', res.status);
        
        const result = await res.json();
        console.log('📦 Response data:', result);
        
        if(result.status === 'success') {
            // Show success message with application ID
            alert(`✅ Application submitted successfully!\n\nApplication ID: ${result.application_id}\n\nClick "My Applications" button to track your application.`);
            form.reset();
            
            // Ensure My Applications button is still visible
            if (!document.getElementById('myApplicationsBtn')) {
                addMyApplicationsButton();
            }
            
            // Update button with badge showing application count
            updateApplicationButtonBadge();
        } else {
            alert('❌ Failed to submit application. Please try again.');
        }
        
    } catch(err) {
        console.error('❌ Error submitting application:', err);
        alert('❌ An error occurred. Please try again.');
    }
}

window.onload=async()=>{
    await loadCategories();
    
    // Auto-select first category if available
    if(categories.length > 0) {
        selectCategory(categories[0]);
    }
    
    // Add "My Applications" button to the interface
    addMyApplicationsButton();
};

// ==================== MY APPLICATIONS FEATURE ====================

function addMyApplicationsButton() {
    // Check if button already exists to prevent duplicates
    if (document.getElementById('myApplicationsBtn')) {
        return;
    }
    
    // Add button to top right of the page
    const button = document.createElement('button');
    button.id = 'myApplicationsBtn'; // Add ID to track it
    button.innerHTML = '📋 My Applications';
    button.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        cursor: pointer;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        z-index: 1000;
        transition: all 0.3s;
    `;
    button.onmouseover = () => {
        button.style.transform = 'translateY(-2px)';
        button.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
    };
    button.onmouseout = () => {
        button.style.transform = 'translateY(0)';
        button.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
    };
    button.onclick = showMyApplications;
    document.body.appendChild(button);
    
    // Initial badge update
    updateApplicationButtonBadge();
}

// Update the button with application count badge
async function updateApplicationButtonBadge() {
    try {
        const statsRes = await fetch(`/api/application-stats/${profile_id}`);
        const stats = await statsRes.json();
        const button = document.getElementById('myApplicationsBtn');
        
        if (button && stats.total > 0) {
            button.innerHTML = `
                📋 My Applications 
                <span style="
                    background: white;
                    color: #667eea;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                    margin-left: 6px;
                ">${stats.total}</span>
            `;
        }
    } catch (err) {
        console.error('Error updating badge:', err);
    }
}

async function showMyApplications() {
    try {
        // Get applications for current user
        const statsRes = await fetch(`/api/application-stats/${profile_id}`);
        const stats = await statsRes.json();
        
        const appsRes = await fetch(`/api/my-applications/${profile_id}`);
        const applications = await appsRes.json();
        
        // Check if user is admin (simple check - can be improved)
        const isAdmin = window.location.pathname.includes('/admin') || sessionStorage.getItem('admin_logged_in') === 'true';
        
        // Create modal
        const modal = document.createElement('div');
        modal.id = 'applicationsModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.4);
            z-index: 2000;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.3s;
        `;
        
        // Close when clicking outside
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        };
        
        modal.innerHTML = `
            <div onclick="event.stopPropagation()" style="background: white; width: 95%; max-width: 1400px; max-height: 95vh; border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                <!-- Header -->
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 30px; display: flex; justify-content: space-between; align-items: center;">
                    <h2 style="margin: 0; font-size: 24px; font-weight: 700;">📋 My Applications</h2>
                    <div style="display: flex; gap: 12px; align-items: center;">
                        <button onclick="exportApplicationsReport()" style="padding: 10px 20px; background: white; color: #667eea; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.3s;">
                            📄 Export PDF
                        </button>
                        <button onclick="document.getElementById('applicationsModal').remove()" style="background: rgba(255,255,255,0.2); border: none; color: white; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; font-size: 24px; font-weight: bold; display: flex; align-items: center; justify-content: center; transition: all 0.3s;">
                            ×
                        </button>
                    </div>
                </div>
                
                <!-- Content -->
                <div style="padding: 30px; background: #f8f9fa;">
                    <!-- Stats Cards - Compact -->
                    <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin-bottom: 24px;">
                        <div style="background: white; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #e3f2fd; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <div style="font-size: 32px; font-weight: bold; color: #1976d2;">${stats.total || 0}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Total</div>
                        </div>
                        <div style="background: white; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #fff3e0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <div style="font-size: 32px; font-weight: bold; color: #f57c00;">${stats.pending || 0}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Pending</div>
                        </div>
                        <div style="background: white; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #e8f5e9; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <div style="font-size: 32px; font-weight: bold; color: #388e3c;">${stats.approved || 0}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Approved</div>
                        </div>
                        <div style="background: white; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #fce4ec; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <div style="font-size: 32px; font-weight: bold; color: #c2185b;">${stats.rejected || 0}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Rejected</div>
                        </div>
                        <div style="background: white; padding: 16px; border-radius: 10px; text-align: center; border: 2px solid #f3e5f5; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                            <div style="font-size: 32px; font-weight: bold; color: #7b1fa2;">${stats.processing || 0}</div>
                            <div style="font-size: 11px; color: #666; margin-top: 4px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Processing</div>
                        </div>
                    </div>
                    
                    <!-- Applications List - Tidier Layout -->
                    <div style="background: white; border-radius: 12px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); max-height: 500px; overflow-y: auto;">
                        ${applications.length === 0 ? `
                            <div style="text-align: center; padding: 80px 20px; color: #999;">
                                <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.5;">📭</div>
                                <div style="font-size: 20px; font-weight: 600; color: #666; margin-bottom: 8px;">No applications yet</div>
                                <div style="font-size: 14px; color: #999;">Submit an application to track it here</div>
                            </div>
                        ` : applications.map(app => `
                            <div style="background: linear-gradient(to right, ${
                                app.status === 'approved' ? '#e8f5e9' :
                                app.status === 'rejected' ? '#fce4ec' :
                                app.status === 'processing' ? '#f3e5f5' :
                                app.status === 'cancelled' ? '#f5f5f5' : '#fff3e0'
                            }, white); padding: 20px; border-radius: 10px; margin-bottom: 12px; border-left: 5px solid ${
                                app.status === 'approved' ? '#388e3c' :
                                app.status === 'rejected' ? '#c2185b' :
                                app.status === 'processing' ? '#7b1fa2' :
                                app.status === 'cancelled' ? '#757575' : '#f57c00'
                            }; box-shadow: 0 2px 6px rgba(0,0,0,0.06); transition: all 0.3s;">
                                <!-- Header Row -->
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                                    <div style="display: flex; align-items: center; gap: 12px;">
                                        <div style="font-weight: 700; font-size: 18px; color: #333;">
                                            #${app._id.substring(app._id.length - 6).toUpperCase()}
                                        </div>
                                        <div style="font-size: 13px; color: #666; background: white; padding: 4px 10px; border-radius: 6px;">
                                            📅 ${new Date(app.submitted_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                                        </div>
                                    </div>
                                    <span style="background: ${
                                        app.status === 'approved' ? '#388e3c' :
                                        app.status === 'rejected' ? '#c2185b' :
                                        app.status === 'processing' ? '#7b1fa2' :
                                        app.status === 'cancelled' ? '#757575' : '#f57c00'
                                    }; color: white; padding: 6px 14px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">
                                        ${app.status}
                                    </span>
                                </div>
                                
                                <!-- Info Row -->
                                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; padding: 12px; background: rgba(255,255,255,0.7); border-radius: 8px;">
                                    <div style="font-size: 13px;">
                                        <span style="color: #999; font-weight: 600;">Subcategory:</span>
                                        <span style="color: #333; font-weight: 500; margin-left: 6px;">${app.subcategory_id}</span>
                                    </div>
                                    <div style="font-size: 13px;">
                                        <span style="color: #999; font-weight: 600;">Item:</span>
                                        <span style="color: #333; font-weight: 500; margin-left: 6px;">${app.item_id}</span>
                                    </div>
                                </div>
                                
                                ${app.admin_notes ? `
                                    <div style="background: #fff3cd; padding: 12px; border-radius: 8px; margin-bottom: 16px; border-left: 4px solid #ffc107;">
                                        <div style="font-weight: 700; font-size: 12px; color: #856404; margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.5px;">📝 Admin Notes</div>
                                        <div style="font-size: 13px; color: #856404; line-height: 1.5;">${app.admin_notes}</div>
                                    </div>
                                ` : ''}
                                
                                <!-- Action Buttons - Clean Layout -->
                                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                                    ${app.status === 'pending' ? `
                                        <button onclick="updateApplicationStatus('${app._id}', 'processing')" style="padding: 10px 18px; background: #7b1fa2; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1; min-width: 120px;">
                                            🔄 Processing
                                        </button>
                                        <button onclick="updateApplicationStatus('${app._id}', 'approved')" style="padding: 10px 18px; background: #388e3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1; min-width: 120px;">
                                            ✅ Approve
                                        </button>
                                        <button onclick="updateApplicationStatus('${app._id}', 'rejected')" style="padding: 10px 18px; background: #c2185b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1; min-width: 120px;">
                                            ❌ Reject
                                        </button>
                                        <button onclick="cancelApplication('${app._id}')" style="padding: 10px 18px; background: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1; min-width: 120px;">
                                            🗑️ Cancel
                                        </button>
                                    ` : app.status === 'processing' ? `
                                        <button onclick="updateApplicationStatus('${app._id}', 'approved')" style="padding: 10px 18px; background: #388e3c; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1;">
                                            ✅ Approve
                                        </button>
                                        <button onclick="updateApplicationStatus('${app._id}', 'rejected')" style="padding: 10px 18px; background: #c2185b; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s; flex: 1;">
                                            ❌ Reject
                                        </button>
                                    ` : ''}
                                    
                                    <button onclick="viewApplicationDetails('${app._id}')" style="padding: 10px 18px; background: white; color: #2196F3; border: 2px solid #2196F3; border-radius: 8px; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.3s;">
                                        👁️ Details
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
    } catch (err) {
        console.error('Error loading applications:', err);
        alert('Error loading applications. Please try again.');
    }
}

async function cancelApplication(applicationId) {
    if (!confirm('Are you sure you want to cancel this application?')) return;
    
    try {
        const res = await fetch(`/api/my-applications/${profile_id}/${applicationId}`, {
            method: 'DELETE'
        });
        
        if (res.ok) {
            alert('Application cancelled successfully!');
            document.querySelector('[style*="position: fixed"]').remove();
            showMyApplications();
        } else {
            alert('Cannot cancel this application');
        }
    } catch (err) {
        console.error('Error cancelling application:', err);
        alert('Error cancelling application. Please try again.');
    }
}

// Update application status (uses public endpoint)
async function updateApplicationStatus(applicationId, newStatus) {
    const statusMessages = {
        'processing': 'mark this application as Processing',
        'approved': 'approve this application',
        'rejected': 'reject this application'
    };
    
    if (!confirm(`Are you sure you want to ${statusMessages[newStatus]}?`)) return;
    
    let notes = '';
    if (newStatus === 'rejected') {
        notes = prompt('Please provide a reason for rejection:');
        if (!notes) return;
    }
    
    try {
        const res = await fetch(`/api/my-applications/${profile_id}/${applicationId}/update-status`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                status: newStatus,
                notes: notes
            })
        });
        
        if (res.ok) {
            alert('✅ Application status updated successfully!');
            document.querySelector('[style*="position: fixed"]').remove();
            showMyApplications();
        } else {
            const error = await res.json();
            alert('❌ Error: ' + (error.error || 'Could not update application'));
        }
    } catch (err) {
        console.error('Error updating status:', err);
        alert('❌ Error updating application. Please try again.');
    }
}

// View application details
async function viewApplicationDetails(applicationId) {
    try {
        const res = await fetch(`/api/my-applications/${profile_id}`);
        const applications = await res.json();
        const app = applications.find(a => a._id === applicationId);
        
        if (!app) {
            alert('Application not found');
            return;
        }
        
        const detailsModal = document.createElement('div');
        detailsModal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 3000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        detailsModal.innerHTML = `
            <div style="background: white; width: 90%; max-width: 600px; border-radius: 12px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.5);">
                <div style="background: #2196F3; color: white; padding: 20px; display: flex; justify-content: space-between; align-items: center;">
                    <h3 style="margin: 0;">Application Details</h3>
                    <button onclick="this.closest('div').parentElement.remove()" style="background: none; border: none; color: white; font-size: 28px; cursor: pointer;">×</button>
                </div>
                <div style="padding: 24px; max-height: 70vh; overflow-y: auto;">
                    <div style="margin-bottom: 20px;">
                        <div style="font-size: 24px; font-weight: bold; color: #333; margin-bottom: 8px;">
                            #${app._id.substring(app._id.length - 6).toUpperCase()}
                        </div>
                        <div style="display: inline-block; background: ${
                            app.status === 'approved' ? '#e8f5e9' :
                            app.status === 'rejected' ? '#fce4ec' :
                            app.status === 'processing' ? '#f3e5f5' : '#fff3e0'
                        }; color: ${
                            app.status === 'approved' ? '#388e3c' :
                            app.status === 'rejected' ? '#c2185b' :
                            app.status === 'processing' ? '#7b1fa2' : '#f57c00'
                        }; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; text-transform: uppercase;">
                            ${app.status}
                        </div>
                    </div>
                    
                    <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                        <div style="font-weight: 600; margin-bottom: 12px; color: #666;">Application Information</div>
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 14px;">
                            <div>
                                <div style="color: #999; font-size: 12px;">Subcategory ID</div>
                                <div style="font-weight: 600; color: #333;">${app.subcategory_id}</div>
                            </div>
                            <div>
                                <div style="color: #999; font-size: 12px;">Item ID</div>
                                <div style="font-weight: 600; color: #333;">${app.item_id}</div>
                            </div>
                            <div>
                                <div style="color: #999; font-size: 12px;">Submitted</div>
                                <div style="font-weight: 600; color: #333;">${new Date(app.submitted_at).toLocaleString()}</div>
                            </div>
                            <div>
                                <div style="color: #999; font-size: 12px;">Last Updated</div>
                                <div style="font-weight: 600; color: #333;">${new Date(app.updated_at).toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                    
                    ${app.application_data ? `
                        <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; margin-bottom: 16px;">
                            <div style="font-weight: 600; margin-bottom: 12px; color: #666;">Submitted Data</div>
                            ${Object.entries(app.application_data).map(([key, value]) => `
                                <div style="margin-bottom: 8px;">
                                    <div style="color: #999; font-size: 12px; text-transform: capitalize;">${key.replace(/([A-Z])/g, ' $1').trim()}</div>
                                    <div style="font-weight: 500; color: #333;">${value}</div>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                    
                    ${app.admin_notes ? `
                        <div style="background: #fff3e0; padding: 16px; border-radius: 8px; border-left: 4px solid #f57c00;">
                            <div style="font-weight: 600; margin-bottom: 8px; color: #f57c00;">Admin Notes</div>
                            <div style="color: #333;">${app.admin_notes}</div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.body.appendChild(detailsModal);
        
    } catch (err) {
        console.error('Error loading details:', err);
        alert('Error loading application details');
    }
}

// Export applications as PDF
async function exportApplicationsReport() {
    try {
        const statsRes = await fetch(`/api/application-stats/${profile_id}`);
        const stats = await statsRes.json();
        
        const appsRes = await fetch(`/api/my-applications/${profile_id}`);
        const applications = await appsRes.json();
        
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
            <head>
                <title>My Applications Report</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    h1 { color: #667eea; border-bottom: 3px solid #667eea; padding-bottom: 10px; }
                    .stats { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }
                    .stat-card { background: #f5f5f5; padding: 15px; border-radius: 8px; text-align: center; }
                    .stat-value { font-size: 28px; font-weight: bold; color: #667eea; }
                    .stat-label { font-size: 12px; color: #666; margin-top: 4px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 12px; text-align: left; font-size: 13px; }
                    th { background: #667eea; color: white; }
                    tr:nth-child(even) { background: #f9f9f9; }
                    .status { padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; }
                    .status-pending { background: #fff3e0; color: #f57c00; }
                    .status-approved { background: #e8f5e9; color: #388e3c; }
                    .status-rejected { background: #fce4ec; color: #c2185b; }
                    .status-processing { background: #f3e5f5; color: #7b1fa2; }
                    .footer { margin-top: 30px; text-align: center; font-size: 11px; color: #999; }
                </style>
            </head>
            <body>
                <h1>📋 My Applications Report</h1>
                <p><strong>Generated:</strong> ${new Date().toLocaleString()}</p>
                <p><strong>User ID:</strong> ${profile_id}</p>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-value">${stats.total || 0}</div>
                        <div class="stat-label">Total</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.pending || 0}</div>
                        <div class="stat-label">Pending</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.approved || 0}</div>
                        <div class="stat-label">Approved</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.rejected || 0}</div>
                        <div class="stat-label">Rejected</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.processing || 0}</div>
                        <div class="stat-label">Processing</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Application ID</th>
                            <th>Status</th>
                            <th>Subcategory</th>
                            <th>Item</th>
                            <th>Submitted</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${applications.map(app => `
                            <tr>
                                <td>${app._id.substring(app._id.length - 8).toUpperCase()}</td>
                                <td><span class="status status-${app.status}">${app.status.toUpperCase()}</span></td>
                                <td>${app.subcategory_id}</td>
                                <td>${app.item_id}</td>
                                <td>${new Date(app.submitted_at).toLocaleDateString()}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                
                <div class="footer">
                    <p>Citizen Services Portal - Application Report</p>
                    <p>This report is confidential</p>
                </div>
            </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
        
    } catch (err) {
        console.error('Error generating report:', err);
        alert('Error generating PDF report');
    }
}