import os

html = """<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quran Shorts | Premium Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-gradient: linear-gradient(-45deg, #0f172a, #1e1b4b, #064e3b, #0f172a);
            --glass-bg: rgba(255, 255, 255, 0.03);
            --glass-border: rgba(255, 255, 255, 0.08);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.4);
            --danger: #ef4444;
            --gold: #fbbf24;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }

        body {
            background: var(--bg-gradient);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
            color: var(--text-main);
            min-height: 100vh;
            padding: 20px;
            overflow-x: hidden;
        }

        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container { max-width: 1000px; margin: auto; animation: fadeIn 0.8s ease-out; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

        /* Header */
        .header {
            display: flex; justify-content: space-between; align-items: center;
            padding: 20px; margin-bottom: 30px;
            background: var(--glass-bg); backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border); border-radius: 20px;
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
        }
        .header h1 { font-size: 24px; font-weight: 700; background: linear-gradient(to right, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        .btn {
            background: var(--accent); color: white; border: none; padding: 12px 24px;
            border-radius: 12px; cursor: pointer; font-weight: 700; font-size: 15px;
            transition: all 0.3s ease; box-shadow: 0 4px 15px var(--accent-glow);
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 8px 25px var(--accent-glow); }
        .btn:active { transform: translateY(1px); }
        .btn-danger { background: var(--danger); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
        .btn-danger:hover { box-shadow: 0 8px 25px rgba(239, 68, 68, 0.5); }
        .btn-sm { padding: 6px 12px; font-size: 12px; border-radius: 8px; }

        /* Stats Grid */
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card {
            background: var(--glass-bg); backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border); border-radius: 20px;
            padding: 25px; position: relative; overflow: hidden;
            transition: transform 0.3s ease;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card::before {
            content: ''; position: absolute; top: 0; right: 0; width: 100%; height: 4px;
            background: linear-gradient(to right, transparent, var(--accent), transparent);
        }
        .stat-card.blue::before { background: linear-gradient(to right, transparent, #3b82f6, transparent); }
        .stat-card.gold::before { background: linear-gradient(to right, transparent, var(--gold), transparent); }
        
        .stat-title { font-size: 14px; color: var(--text-muted); margin-bottom: 10px; font-weight: 600; }
        .stat-val { font-size: 28px; font-weight: 900; color: var(--text-main); }
        .stat-sub { font-size: 13px; color: var(--accent); margin-top: 8px; font-weight: 600; }

        /* Panels */
        .panel {
            background: var(--glass-bg); backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border); border-radius: 20px;
            padding: 25px; margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0,0,0,0.3);
            animation: slideUp 0.5s ease-out;
        }
        @keyframes slideUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        
        .panel h3 { margin-bottom: 20px; font-size: 18px; display: flex; align-items: center; gap: 10px; }
        
        /* Lists */
        .list-container { display: flex; flex-direction: column; gap: 12px; }
        .list-item {
            display: flex; justify-content: space-between; align-items: center;
            background: rgba(0,0,0,0.2); padding: 15px; border-radius: 12px;
            border: 1px solid rgba(255,255,255,0.05); transition: background 0.3s;
        }
        .list-item:hover { background: rgba(0,0,0,0.4); }
        .item-info { display: flex; flex-direction: column; }
        .item-name { font-weight: 700; font-size: 16px; }
        .item-key { font-size: 11px; color: var(--text-muted); direction: ltr; text-align: right; margin-top: 4px; }

        /* Inputs */
        .add-row { display: flex; flex-direction: column; gap: 12px; margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--glass-border); }
        @media(min-width: 600px) { .add-row { flex-direction: row; align-items: center; } }
        
        input[type="text"], input[type="number"] {
            width: 100%; padding: 14px; border-radius: 12px;
            background: rgba(0,0,0,0.3); border: 1px solid var(--glass-border);
            color: white; font-family: 'Cairo', sans-serif; font-size: 14px;
            transition: border 0.3s ease, box-shadow 0.3s ease;
        }
        input:focus { outline: none; border-color: var(--accent); box-shadow: 0 0 15px rgba(16,185,129,0.2); }

        .hidden { display: none !important; }
    </style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🕌 Quran Shorts</h1>
        <button id="loginBtn" class="btn" onclick="login()">دخول الأدمن</button>
    </div>

    <div class="stats-grid" id="stats">
        <div class="stat-card">
            <div class="stat-title">التقدم الحالي</div>
            <div class="stat-val" id="progress">...</div>
        </div>
        <div class="stat-card blue">
            <div class="stat-title">آخر فيديو تم نشره</div>
            <div class="stat-val" id="lastPostTime">...</div>
            <div class="stat-sub" id="lastPostReciter"></div>
        </div>
        <div class="stat-card gold">
            <div class="stat-title">النشر القادم</div>
            <div class="stat-val" id="nextPostTime">...</div>
            <div class="stat-sub" id="nextPostReciter"></div>
        </div>
    </div>

    <div id="adminPanel" class="hidden">
        <div class="panel" style="text-align: center;">
            <h3>⚡ إجراءات سريعة</h3>
            <button class="btn" onclick="triggerWorkflow()" style="width: 100%; max-width: 300px; margin: auto;">تشغيل البوت الآن (Run Workflow)</button>
            <div id="workflowStatus" style="margin-top: 15px; color: var(--gold); font-weight: 600;"></div>
        </div>

        <div class="panel">
            <h3>🎙️ إدارة القراء</h3>
            <div class="list-container" id="recitersList"></div>
            
            <div class="add-row">
                <input type="text" id="newReciterName" placeholder="اسم القارئ (بالعربي)">
                <input type="text" id="newReciterKey" placeholder="المفتاح (إنجليزي)">
                <button class="btn" onclick="addReciter()">إضافة</button>
            </div>
        </div>

        <div class="panel">
            <h3>⏰ إدارة المواعيد (بالدقائق)</h3>
            <div class="list-container" id="slotsList"></div>
        </div>
    </div>
</div>

<script>
    const REPO = "zahrarj587-tech/quran-shorts";
    let PAT = localStorage.getItem("gh_pat") || "";
    let recitersData = {};
    let slotsData = {};
    
    async function loadData() {
        try {
            const [progRes, statsRes, recitersRes, slotsRes] = await Promise.all([
                fetch(`https://raw.githubusercontent.com/${REPO}/main/progress.json`),
                fetch(`https://raw.githubusercontent.com/${REPO}/main/stats.json`),
                fetch(`https://raw.githubusercontent.com/${REPO}/main/reciters.json`),
                fetch(`https://raw.githubusercontent.com/${REPO}/main/slots.json`)
            ]);
            const prog = await progRes.json();
            const stats = await statsRes.json();
            recitersData = await recitersRes.json();
            slotsData = await slotsRes.json();

            document.getElementById("progress").innerText = `سورة ${prog.surah} - آية ${prog.ayah}`;
            
            const reciterKeys = Object.keys(recitersData);
            const nextReciterKey = reciterKeys[prog.n % reciterKeys.length];
            const nextReciterName = recitersData[nextReciterKey] || nextReciterKey;
            document.getElementById("nextPostReciter").innerText = `بصوت: ${nextReciterName}`;

            if (stats.log && stats.log.length > 0) {
                const lastLog = stats.log[stats.log.length - 1];
                const lastDate = new Date(lastLog.time || Date.now());
                const timeStr = lastDate.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
                document.getElementById("lastPostTime").innerText = `${lastLog.slot || 'سابقاً'}`;
                document.getElementById("lastPostReciter").innerText = `الساعة: ${timeStr} | بصوت: ${lastLog.reciter_name || 'غير معروف'}`;
            } else {
                document.getElementById("lastPostTime").innerText = "لا يوجد";
            }
            calculateNextPost();
        } catch(e) { console.log(e); }
    }

    async function calculateNextPost() {
        try {
            const now = new Date();
            const res = await fetch(`https://api.aladhan.com/v1/timingsByCity?city=Cairo&country=Egypt&method=5`);
            const data = await res.json();
            const timings = data.data.timings;
            let upcomingSlots = [];
            for (let [key, offset] of Object.entries(slotsData)) {
                if (!timings[key]) continue;
                let [h, m] = timings[key].split(':').map(Number);
                let slotTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), h, m, 0);
                slotTime.setMinutes(slotTime.getMinutes() + offset);
                if (slotTime > now) { upcomingSlots.push({ name: key, time: slotTime }); }
            }
            upcomingSlots.sort((a, b) => a.time - b.time);
            if (upcomingSlots.length > 0) {
                const next = upcomingSlots[0];
                const timeStr = next.time.toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' });
                document.getElementById("nextPostTime").innerText = `الساعة: ${timeStr}`;
                document.getElementById("nextPostReciter").innerHTML += `<br><span style="color:var(--text-muted); font-size:11px;">(ميعاد: ${next.name})</span>`;
            } else {
                document.getElementById("nextPostTime").innerText = "غداً (شروق)";
            }
        } catch(e) { document.getElementById("nextPostTime").innerText = "تعذر الحساب"; }
    }

    function login() {
        if (PAT) { showAdmin(); return; }
        let token = prompt("أدخل GitHub Token:");
        if (token) { PAT = token; localStorage.setItem("gh_pat", PAT); showAdmin(); }
    }

    function showAdmin() {
        document.getElementById("adminPanel").classList.remove("hidden");
        document.getElementById("loginBtn").innerText = "خروج";
        document.getElementById("loginBtn").classList.add("btn-danger");
        document.getElementById("loginBtn").onclick = () => { localStorage.removeItem("gh_pat"); location.reload(); };
        loadReciters();
        loadSlots();
    }

    async function getFile(path) {
        const res = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}`, { headers: { 'Authorization': `Bearer ${PAT}` } });
        const data = await res.json();
        if (!data.content) throw new Error("Auth failed");
        const content = decodeURIComponent(atob(data.content).split('').map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)).join(''));
        return { data: JSON.parse(content), sha: data.sha };
    }

    async function updateFile(path, obj, sha, msg) {
        const content = btoa(unescape(encodeURIComponent(JSON.stringify(obj, null, 2))));
        const res = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}`, {
            method: 'PUT',
            headers: { 'Authorization': `Bearer ${PAT}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, content: content, sha: sha })
        });
        if (!res.ok) throw new Error("Update failed");
    }

    async function loadReciters() {
        try {
            const { data, sha } = await getFile("reciters.json");
            let html = "";
            for (let [key, name] of Object.entries(data)) {
                html += `
                <div class="list-item">
                    <div class="item-info">
                        <span class="item-name">${name}</span>
                        <span class="item-key">${key}</span>
                    </div>
                    <button class="btn btn-danger btn-sm" onclick="deleteReciter('${key}')">حذف</button>
                </div>`;
            }
            document.getElementById("recitersList").innerHTML = html;
        } catch(e) { alert("خطأ في تحميل القراء. تأكد من التوكن."); }
    }

    async function addReciter() {
        const name = document.getElementById("newReciterName").value.trim();
        const key = document.getElementById("newReciterKey").value.trim();
        if (!key || !name) return alert("أدخل الاسم والمفتاح");
        try {
            const { data, sha } = await getFile("reciters.json");
            data[key] = name;
            await updateFile("reciters.json", data, sha, `Add reciter: ${name}`);
            document.getElementById("newReciterName").value = "";
            document.getElementById("newReciterKey").value = "";
            loadReciters(); loadData();
        } catch(e) { alert("حدث خطأ أثناء الإضافة"); }
    }

    async function deleteReciter(key) {
        if (!confirm("هل أنت متأكد من الحذف؟")) return;
        try {
            const { data, sha } = await getFile("reciters.json");
            delete data[key];
            await updateFile("reciters.json", data, sha, `Delete reciter: ${key}`);
            loadReciters(); loadData();
        } catch(e) { alert("حدث خطأ أثناء الحذف"); }
    }

    async function loadSlots() {
        try {
            const { data, sha } = await getFile("slots.json");
            let html = "";
            for (let [key, offset] of Object.entries(data)) {
                html += `
                <div class="list-item">
                    <div class="item-info">
                        <span class="item-name" style="color:var(--gold);">${key}</span>
                    </div>
                    <div style="display:flex; gap:10px; align-items:center;">
                        <input type="number" id="off_${key}" value="${offset}" style="width:80px; text-align:center;">
                        <button class="btn btn-sm" onclick="saveSlot('${key}')">حفظ</button>
                    </div>
                </div>`;
            }
            document.getElementById("slotsList").innerHTML = html;
        } catch(e) { console.log(e); }
    }

    async function saveSlot(key) {
        const newOffset = parseInt(document.getElementById(`off_${key}`).value);
        if (isNaN(newOffset)) return alert("أدخل رقم صحيح");
        try {
            const { data, sha } = await getFile("slots.json");
            data[key] = newOffset;
            await updateFile("slots.json", data, sha, `Update slot ${key} to ${newOffset}`);
            alert("تم الحفظ!"); loadData();
        } catch(e) { alert("حدث خطأ"); }
    }

    async function triggerWorkflow() {
        document.getElementById("workflowStatus").innerText = "جاري التشغيل...";
        try {
            const res = await fetch(`https://api.github.com/repos/${REPO}/actions/workflows/post.yml/dispatches`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${PAT}`, 'Accept': 'application/vnd.github.v3+json' },
                body: JSON.stringify({ ref: "main", inputs: { force: "true" } })
            });
            if (res.ok) document.getElementById("workflowStatus").innerText = "تم التشغيل بنجاح ✅";
            else document.getElementById("workflowStatus").innerText = "فشل التشغيل ❌";
        } catch(e) { document.getElementById("workflowStatus").innerText = "خطأ ❌"; }
    }

    loadData();
    if (PAT) showAdmin();
</script>
</body>
</html>"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html)
print("✅ Premium Dashboard Built Successfully!")
