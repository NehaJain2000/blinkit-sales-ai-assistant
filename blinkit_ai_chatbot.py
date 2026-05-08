#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import webbrowser
import threading
import time
from groq import Groq

API_KEY = "Put your Groq API"

client = Groq(api_key=API_KEY)

SYSTEM_PROMPT = """You are an AI analyst for a Blinkit Grocery Sales Dashboard built in Power BI.
You help business managers analyze grocery outlet performance and product ratings.

Data you know:
- Item Types: Fruits & Vegetables, Dairy, Snack Foods, Frozen Foods, Household, Beverages, Meat, Seafood, Breakfast, Drinks, Baking Goods, Health & Hygiene, Canned, Starchy Foods
- Item Fat Content: Low Fat, Regular
- Outlet Types: Grocery Store, Supermarket Type1, Type2, Type3
- Outlet Location: Tier 1 (metro), Tier 2 (mid cities), Tier 3 (small cities)
- Outlet Size: Small, Medium, High
- Metrics: Sales, Avg Sales, Avg Rating, Item Visibility, Number of Items, Total Sales

Always respond in the SAME language the user writes in.
Format as bullet points starting with - on separate lines. Max 5 points. No paragraphs."""

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Blinkit AI Analyzer</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #fffef5; --surface: #fff; --surface2: #fdf9e8;
  --border: #e8e0c0; --accent: #f0c000; --dark: #c49a00;
  --text: #1a1600; --dim: #7a6f40; --user: #1a1600;
}
body { font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); height: 100vh; display: flex; flex-direction: column; overflow: hidden; }

.header { padding: 12px 20px; background: var(--accent); display: flex; align-items: center; gap: 10px; flex-shrink: 0; border-bottom: 1px solid var(--border); }
.header-logo { font-size: 18px; font-weight: 700; }
.header-sub { font-size: 11px; color: #1a160099; text-transform: uppercase; letter-spacing: .06em; }
.badge { margin-left: auto; background: #1a160022; border: 1px solid #1a160044; font-size: 10px; padding: 3px 8px; border-radius: 20px; font-weight: 600; }

.main { display: flex; flex: 1; overflow: hidden; }

.sidebar { width: 250px; flex-shrink: 0; background: var(--surface); border-right: 1px solid var(--border); overflow-y: auto; }
.sidebar-title { padding: 12px 14px; font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; color: var(--dim); border-bottom: 1px solid var(--border); }
.cat-title { padding: 10px 14px 5px; font-size: 11px; font-weight: 600; color: var(--dark); text-transform: uppercase; letter-spacing: .06em; }
.q { padding: 6px 14px 6px 24px; font-size: 12px; color: var(--dim); cursor: pointer; border-left: 2px solid transparent; transition: all .15s; line-height: 1.4; }
.q:hover { background: var(--surface2); color: var(--text); border-left-color: var(--accent); }

.chat-wrap { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 12px; }

.welcome { text-align: center; padding: 24px 16px; }
.welcome-icon { font-size: 28px; margin-bottom: 8px; }
.greet-wrap { position: relative; height: 40px; margin-bottom: 4px; }
.greet { font-size: 20px; font-weight: 600; position: absolute; width: 100%; text-align: center; opacity: 0; transition: opacity .8s; }
.greet.on { opacity: 1; }
.lang { font-size: 12px; color: var(--dark); height: 18px; font-weight: 500; margin-bottom: 8px; }
.welcome p { font-size: 13px; color: var(--dim); }

.msg { display: flex; gap: 8px; max-width: 90%; opacity: 0; animation: pop .3s ease forwards; }
@keyframes pop { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.msg.user { margin-left: auto; flex-direction: row-reverse; }
.msg.bot { margin-right: auto; }
.av { width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; flex-shrink: 0; }
.av.bot { background: var(--accent); }
.av.user { background: var(--user); }
.bbl { padding: 9px 13px; border-radius: 14px; font-size: 13px; line-height: 1.6; }
.msg.user .bbl { background: var(--user); color: #fff; border-bottom-right-radius: 3px; }
.msg.bot .bbl { background: var(--surface); border: 1px solid var(--border); color: var(--text); border-bottom-left-radius: 3px; }
.typing .bbl { display: flex; gap: 4px; align-items: center; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: var(--dark); animation: b 1.2s infinite; }
.dot:nth-child(2){animation-delay:.2s}.dot:nth-child(3){animation-delay:.4s}
@keyframes b { 0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1} }

.input-row { padding: 10px 16px; border-top: 1px solid var(--border); background: var(--surface); display: flex; gap: 8px; align-items: flex-end; flex-shrink: 0; }
#inp { flex: 1; background: var(--surface2); border: 1.5px solid var(--border); border-radius: 10px; color: var(--text); font-family: 'DM Sans', sans-serif; font-size: 13px; padding: 9px 13px; resize: none; outline: none; min-height: 38px; max-height: 90px; line-height: 1.5; }
#inp:focus { border-color: var(--dark); }
#inp::placeholder { color: var(--dim); }
#sbtn { width: 38px; height: 38px; background: var(--accent); border: none; border-radius: 10px; cursor: pointer; font-size: 16px; font-weight: 700; flex-shrink: 0; }
#sbtn:hover { background: var(--dark); color: #fff; }
#sbtn:disabled { opacity: .4; cursor: not-allowed; }
.foot { text-align: center; font-size: 10px; color: var(--dim); padding: 5px; background: var(--surface2); border-top: 1px solid var(--border); flex-shrink: 0; }
</style>
</head>
<body>

<div class="header">
  <div>
    <div class="header-logo">blinkit 🛒</div>
    <div class="header-sub">AI Sales & Rating Analyzer</div>
  </div>
  <div class="badge">● Live · Groq AI</div>
</div>

<div class="main">
  <div class="sidebar">
    <div class="sidebar-title">📋 Quick Questions</div>

    <div class="cat-title">⭐ Rating Analysis</div>
    <div class="q">Which items have the lowest ratings?</div>
    <div class="q">Why do grocery stores have low ratings?</div>
    <div class="q">How to improve product ratings?</div>

    <div class="cat-title">📈 Sales Performance</div>
    <div class="q">Which outlet type has highest sales?</div>
    <div class="q">Why does Tier 3 perform well?</div>
    <div class="q">Top 3 best selling item categories?</div>

    <div class="cat-title">🏪 Outlet Insights</div>
    <div class="q">Why do small outlets underperform?</div>
    <div class="q">Which location tier is most profitable?</div>
    <div class="q">Supermarket Type1 vs Type2 difference?</div>

    <div class="cat-title">🥗 Product Strategy</div>
    <div class="q">Low fat vs regular — which sells better?</div>
    <div class="q">Which items have low visibility?</div>
    <div class="q">How to increase item visibility?</div>

    <div class="cat-title">💡 Recommendations</div>
    <div class="q">Top 3 ways to boost overall revenue</div>
    <div class="q">How to improve Tier 1 performance?</div>
    <div class="q">Which category needs most attention?</div>
  </div>

  <div class="chat-wrap">
    <div class="messages" id="msgs">
      <div class="welcome" id="welcome">
        <div class="welcome-icon">🛒</div>
        <div class="greet-wrap" id="gw"></div>
        <div class="lang" id="gl"></div>
        <p>Click a question on the left or type below.</p>
      </div>
    </div>
    <div class="input-row">
      <textarea id="inp" placeholder="Ask anything..." rows="1"></textarea>
      <button id="sbtn">↑</button>
    </div>
    <div class="foot">Blinkit Dashboard · Power BI + Groq AI</div>
  </div>
</div>

<script>
const greetings = [
  {t:"Hello! I am Blinkit AI",     l:"🇬🇧 English"},
  {t:"नमस्ते! मैं हूँ Blinkit AI", l:"🇮🇳 Hindi"},
  {t:"Hallo! Ich bin Blinkit AI",   l:"🇩🇪 German"},
  {t:"Bonjour! Je suis Blinkit AI", l:"🇫🇷 French"},
  {t:"Hola! Soy Blinkit AI",        l:"🇪🇸 Spanish"},
  {t:"Blinkit AI desu!",            l:"🇯🇵 Japanese"},
  {t:"Ana Blinkit AI!",             l:"🇸🇦 Arabic"},
  {t:"Ola! Eu sou Blinkit AI",      l:"🇧🇷 Portuguese"},
  {t:"Privet! Ya Blinkit AI",       l:"🇷🇺 Russian"},
  {t:"Ni hao! Wo shi Blinkit AI",   l:"🇨🇳 Chinese"},
];
let cur=null, gi=0;
const gw=document.getElementById('gw'), gl=document.getElementById('gl');
function nextGreet(){
  const g=greetings[gi];
  if(cur) cur.classList.remove('on');
  const el=document.createElement('div');
  el.className='greet'; el.textContent=g.t; gw.appendChild(el);
  setTimeout(()=>{el.classList.add('on'); gl.textContent=g.l;},100);
  const old=cur; setTimeout(()=>{if(old)old.remove();},900);
  cur=el; gi=(gi+1)%greetings.length;
}
nextGreet(); setInterval(nextGreet,3000);

const msgs=document.getElementById('msgs');
const inp=document.getElementById('inp');
const sbtn=document.getElementById('sbtn');

// Sidebar clicks
document.querySelectorAll('.q').forEach(q=>{
  q.addEventListener('click',()=>{
    inp.value=q.textContent.trim();
    send();
  });
});

// Enter key
inp.addEventListener('keydown',e=>{
  if(e.key==='Enter' && !e.shiftKey){
    e.preventDefault();
    send();
  }
});

// Send button
sbtn.addEventListener('click', send);

// Auto resize
inp.addEventListener('input',()=>{
  inp.style.height='auto';
  inp.style.height=Math.min(inp.scrollHeight,90)+'px';
});

function addMsg(text,role){
  const w=document.getElementById('welcome');
  if(w) w.remove();
  const m=document.createElement('div');
  m.className='msg '+role;
  const av=document.createElement('div');
  av.className='av '+role;
  av.textContent=role==='bot'?'🛒':'👤';
  const b=document.createElement('div');
  b.className='bbl';
  if(role==='bot'){
    b.innerHTML=text.split('\\n').map(l=>l.trim()).filter(l=>l).join('<br>');
  } else {
    b.textContent=text;
  }
  m.appendChild(av); m.appendChild(b);
  msgs.appendChild(m);
  msgs.scrollTop=msgs.scrollHeight;
}

function addTyping(){
  const m=document.createElement('div');
  m.className='msg bot typing'; m.id='typing';
  m.innerHTML='<div class="av bot">🛒</div><div class="bbl"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
  msgs.appendChild(m); msgs.scrollTop=msgs.scrollHeight;
}
function removeTyping(){const t=document.getElementById('typing');if(t)t.remove();}

async function send(){
  const text=inp.value.trim();
  if(!text) return;
  addMsg(text,'user');
  inp.value=''; inp.style.height='auto';
  sbtn.disabled=true; addTyping();
  try{
    const r=await fetch('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});
    const d=await r.json();
    removeTyping(); addMsg(d.reply,'bot');
  }catch(e){removeTyping();addMsg('Something went wrong. Please try again.','bot');}
  sbtn.disabled=false; inp.focus();
}
</script>
</body>
</html>"""

conversation_history = []

class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_PAGE.encode('utf-8'))
    def do_POST(self):
        length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(length))
        user_msg = body.get('message', '')
        conversation_history.append({"role": "user", "content": user_msg})
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversation_history,
            max_tokens=300
        )
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode())

def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:8767")

if __name__ == "__main__":
    print("="*45)
    print("  Blinkit AI Sales & Rating Analyzer")
    print("="*45)
    print("  Browser mein khul raha hai...")
    print("  Band karne ke liye Ctrl+C dabaao")
    print("="*45)
    threading.Thread(target=open_browser, daemon=True).start()
    server = HTTPServer(('localhost', 8767), ChatHandler)
    server.serve_forever()
