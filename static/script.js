let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
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

        const name = document.createElement("span");
        name.textContent = c.name?.[lang] || c.name?.en || c.id;
        name.onclick = ()=> selectCategory(c);

        header.append(toggle, icon, name);
        catDiv.appendChild(header);

        if(c.subcategories?.length){
            const subDiv = document.createElement("div");
            subDiv.id = `subcat-${c.id}`;
            subDiv.style.display="none";
            subDiv.style.marginLeft="20px";

            c.subcategories.forEach(sub=>{
                const item=document.createElement("div");
                item.className="subcat-item";
                item.innerHTML=`└ ${sub.name?.[lang]||sub.name?.en}
                                <div class="subcount">${sub.itemCount||0} items</div>`;
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
    document.getElementById("sub-title").innerText=cat.name?.[lang]||cat.name?.en;
    document.getElementById("question-list").innerHTML="";
    document.getElementById("answer-box").innerHTML="";

    const list=document.getElementById("sub-list");
    list.innerHTML="";

    if(cat.subcategories?.length){
        cat.subcategories.forEach(sub=>{
            const li=document.createElement("li");
            li.innerHTML=`<b>${sub.name?.[lang]||sub.name?.en}</b><br>
                          <small>${sub.description||""}</small>`;
            li.onclick=()=>selectSubcategory(cat,sub);
            list.appendChild(li);
        });
        document.getElementById("q-title").innerText="Service Details";
    }
}

function selectSubcategory(cat,sub){
    currentServiceName=cat.name?.en;
    currentSub=sub;

    document.getElementById("q-title").innerText=sub.name?.[lang]||sub.name?.en;
    document.getElementById("question-list").innerHTML="";

    let html=`
        <div class="info-card">
            <h2 style="color:${cat.color||"#333"}">${sub.name?.[lang]||sub.name?.en}</h2>
            <p>${sub.description||""}</p>

            <div class="info-section"><b>Available Items:</b> ${sub.itemCount||0}</div>
    `;

    if(sub.keywords?.length){
        html+=`<div class="info-section"><b>Keywords:</b> ${sub.keywords.join(", ")}</div>`;
    }

    html+=`<div class="info-section">
            <button onclick="askAboutCurrent()">Ask AI about this</button>
           </div></div>`;

    document.getElementById("answer-box").innerHTML=html;

    fetch("/api/engagement",{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({user_id:profile_id,service:currentServiceName,question_clicked:sub.name?.en,source:"subcategory"})});
}

async function askAboutCurrent(){
    if(!currentSub) return;
    openChat();
    document.getElementById("chat-text").value=currentSub.name?.en;
    sendChat();
}

/* CHAT */
function openChat(){document.getElementById("chat-panel").style.display="block";}
function closeChat(){document.getElementById("chat-panel").style.display="none";}

async function sendChat(){
    const input=document.getElementById("chat-text");
    const text=input.value.trim();
    if(!text)return;

    appendChat("user",text);
    input.value="";

    const res=await fetch("/api/ai/search",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query:text,top_k:5})});
    const data=await res.json();
    appendChat("bot",data.answer||"No answer found.");
}

function appendChat(sender,text){
    const body=document.getElementById("chat-body");
    const div=document.createElement("div");
    div.className="chat-msg "+(sender==="user"?"user-msg":"bot-msg");
    div.innerText=text;
    body.appendChild(div);
    body.scrollTop=body.scrollHeight;
}

async function loadAds(){
    const res=await fetch("/api/ads");
    const ads=await res.json();
    document.getElementById("ads-area").innerHTML=
        ads.map(a=>`<div class="ad-card"><a href="${a.link||'#'}" target="_blank"><h4>${a.title}</h4><p>${a.body||''}</p></a></div>`).join("");
}

function setLang(l){
    lang=l;
    loadCategories();
}

window.onload=async()=>{
    await loadCategories();
};
