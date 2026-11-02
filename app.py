import hashlib, html, json, os, re, secrets, sqlite3, uuid
from datetime import date
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Jeevan Saathi AI", page_icon="🌱", initial_sidebar_state="auto")
S = st.session_state
I18N = json.loads((Path(__file__).parent / "i18n.json").read_text(encoding="utf-8"))
LANGS = ["English", "हिन्दी", "मराठी"]
esc = html.escape
S.setdefault("lang", "English")
L = S.lang

def t(key):
    en = key.split(":", 1)[1] if ":" in key else key
    return en if L == "English" else I18N[L].get(key, en)

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,.stApp,button,input{font-family:Inter,system-ui,sans-serif}
header[data-testid="stHeader"]{background:transparent}
[data-testid="stToolbarActions"],[data-testid="stAppDeployButton"],[data-testid="stMainMenu"],[data-testid="stDecoration"],footer{display:none!important}
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"]{display:flex!important;visibility:visible!important;opacity:1!important}
.block-container{padding:2rem 20px 4rem!important;max-width:1100px}
section[data-testid="stSidebar"]{background:#fbf9f3;border-right:1px solid #e7e1d4}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"]{border-radius:12px;padding:.5rem .7rem;font-weight:600}
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"]{background:#e9efe9;outline:1px solid #e7e1d4}
.brand{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;color:#203c36;line-height:1.1}
.brand small{display:block;font-size:9px;letter-spacing:.14em;color:#758079;font-weight:600;margin-top:3px}
.mark{background:#267a69;border-radius:12px;width:38px;height:38px;display:inline-flex;align-items:center;justify-content:center;font-size:19px;flex:none}
.eb{font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#758079}
.tp{background:#e9f1ec;border:1px solid #dbe6df;border-radius:14px;padding:12px;font-size:12px;color:#53655d;line-height:1.5;margin:14px 0}
.tp b{color:#267a69}
.st-key-hero{background:radial-gradient(circle at 92% 8%,transparent 0 170px,#ffffff22 171px,transparent 172px),radial-gradient(circle at 80% 100%,#c9a96e55,transparent 260px),#205f53;border-radius:28px;padding:34px 30px}
.pill{display:inline-block;border:1px solid #ffffff40;background:#ffffff14;color:#fff;border-radius:99px;padding:6px 13px;font-size:11px;font-weight:800;letter-spacing:.08em}
.st-key-hero .h1{color:#fff;font-size:clamp(2.2rem,5vw,3.4rem);font-weight:800;line-height:1.05;margin:1.1rem 0 .9rem;letter-spacing:-.02em}
.st-key-hero p.hp{color:#ffffffd0;font-size:15px;line-height:1.7;max-width:560px}
.priv{color:#ffffffc0;font-size:12px;border-top:1px solid #ffffff30;margin-top:22px;padding-top:14px;max-width:560px}
.st-key-hb1 a,.st-key-hb2 a{border-radius:12px;padding:.7rem 1.1rem;width:fit-content;font-weight:700}
.st-key-hb1 a{background:#f5f2e9}.st-key-hb1 p{color:#205f53!important}
.st-key-hb2 a{background:#ffffff14;border:1px solid #ffffff40}.st-key-hb2 p{color:#fff!important}
.sec{display:flex;justify-content:space-between;align-items:flex-end;flex-wrap:wrap;gap:6px;margin:34px 0 12px}
.sec h2{font-size:1.8rem;font-weight:800;margin:0;padding:.2rem 0 0;color:#203c36}.mute{color:#758079;font-size:13px}
[class*="st-key-card_"] a{display:flex;flex-direction:column;align-items:flex-start;gap:.55rem;background:#fffefa;border:1px solid #e7e1d4;border-radius:20px;padding:20px;min-height:170px;text-decoration:none}
[class*="st-key-card_"] a:hover{border-color:#267a69;box-shadow:0 6px 18px #0000000d}
[class*="st-key-card_"] [data-testid="stIconMaterial"]{font-size:24px;padding:11px;border-radius:13px;background:var(--tile);color:var(--ic)}
[class*="st-key-card_"] p{white-space:pre-line;color:#758079;font-size:13.5px;line-height:1.55;margin:0}
[class*="st-key-card_"] p::first-line{font-size:10.5px;font-weight:800;letter-spacing:.14em}
[class*="st-key-card_"] p strong{color:#203c36;font-size:19px}




.st-key-card_sch{--tile:#e9f1eb;--ic:#286c5e}.st-key-card_car{--tile:#fbede3;--ic:#a75d3b}
.st-key-card_plan{--tile:#f6efdb;--ic:#967431}.st-key-card_ask{--tile:#e8eef0;--ic:#4c7079}
.ph h1{font-size:2.2rem;font-weight:800;margin:.35rem 0 .3rem;letter-spacing:-.02em;color:#203c36;padding:0}
.mute{color:#758079;font-size:14px;line-height:1.6}
.h2{font-size:1.7rem;font-weight:800;margin:.2rem 0 .4rem;color:#203c36;padding:0}
[class*="st-key-sc_"],[class*="st-key-cc_"],.st-key-quick,.st-key-chatbox,.st-key-plancard,.st-key-profcard,.st-key-authcard,.st-key-stat1,.st-key-stat2{background:#fffefa;border:1px solid #e7e1d4;border-radius:20px;padding:20px;margin-bottom:6px}
.st-key-quick{margin-top:18px}
.tilerow{display:flex;justify-content:space-between;align-items:flex-start}
.tile{width:48px;height:48px;border-radius:16px;display:inline-flex;align-items:center;justify-content:center;font-size:22px}
.tag{display:inline-block;background:#e9efe9;color:#267a69;font-size:10px;font-weight:800;letter-spacing:.1em;padding:5px 10px;border-radius:99px;margin:2px 4px 2px 0}
.ct{font-size:1.2rem;font-weight:800;margin:12px 0 4px;color:#203c36;padding:0}
.for{font-size:12px;color:#77837b;border-top:1px solid #eee8dc;padding-top:12px;margin-top:8px}
.careerhero{background:#ebeee5;border-radius:23px;padding:26px 24px;margin:14px 0 6px}
.res{background:#f1f7f0;border:1px solid #d9e8dc;border-radius:14px;padding:14px;margin-top:12px;color:#236b5c}
.ck{font-size:13px;color:#4b6b5a;margin:6px 0}
.avatar{width:56px;height:56px;border-radius:50%;background:#267a69;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:800;flex:none}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------- data (from the original React app) ----------
INTRO = "Namaste. I’m Saathi, a sample guidance companion. What would you like help thinking through today?"
SCHEMES = [
 dict(title="Education support", cat="Students", emoji="🎓", tone="#edf2e7", ic="#6d8755", tag="LEARNING", aud="Students and learners", kw="student education learning", desc="Illustrative fee assistance and scholarship pathways for eligible learners."),
 dict(title="Skill development", cat="Job seekers", emoji="💼", tone="#e8eff0", ic="#547b7c", tag="SKILLS", aud="Youth and job seekers", kw="job seeker skills work", desc="Examples of training and placement support that may be available locally."),
 dict(title="Women’s livelihood support", cat="Women", emoji="🤝", tone="#faeee6", ic="#b36c46", tag="LIVELIHOOD", aud="Women and entrepreneurs", kw="women livelihood business", desc="A starting point for exploring enterprise, self-help group and livelihood resources."),
 dict(title="Senior citizen services", cat="Senior citizens", emoji="🧓", tone="#f5efdf", ic="#a08036", tag="WELLBEING", aud="Older adults and caregivers", kw="senior citizen pension care", desc="Examples of care, wellbeing and pension information to verify with local offices."),
]
CAREERS = [
 dict(role="Community health worker", type="Community service", mark="COMMUNITY", skills="Communication · Care · Local knowledge", detail="Explore local public-health and community outreach training pathways."),
 dict(role="Solar installation trainee", type="Skilled trades", mark="TECHNICAL", skills="Practical learning · Safety · Teamwork", detail="Look into vocational courses and apprenticeships in clean-energy work."),
 dict(role="Digital services assistant", type="Digital work", mark="DIGITAL", skills="Computer basics · Communication · Accuracy", detail="Build digital confidence through a local training centre or trusted course."),
 dict(role="Small business / self-help group", type="Self-employment", mark="ENTERPRISE", skills="Planning · Craft · Customer care", detail="Explore local enterprise support and peer-led self-help networks."),
]
HOME_CARDS = [
 ("sch", ":material/account_balance_wallet:", "SUPPORT", "Find a support scheme", "Explore sample benefits and check a few basic eligibility details."),
 ("car", ":material/work:", "WORK & LEARNING", "Explore your next career", "Look at learning paths, work options and practical next steps."),
 ("plan", ":material/calendar_month:", "YOUR PLAN", "Build a steady routine", "Turn a big goal into small tasks you can actually finish."),
 ("ask", ":material/chat_bubble:", "ASK SAATHI", "Ask what’s on your mind", "Try a sample conversation and get a useful place to start."),
]
DEFAULT_TASKS = [
 {"id": "task-focus", "text": "Review one study topic", "time": "Today · 25 min", "done": False},
 {"id": "task-break", "text": "Take a screen-free break", "time": "Today · 10 min", "done": False},
 {"id": "task-next", "text": "Write down one question to ask", "time": "Today · 5 min", "done": True},
]
S.setdefault("user", None); S.setdefault("name", ""); S.setdefault("careers", [])
S.setdefault("msgs", []); S.setdefault("checked", False); S.setdefault("saved", False)
S.setdefault("tasks", [dict(x) for x in DEFAULT_TASKS])

# ---------- storage (SQLite file; Streamlit Cloud may reset it on restart) ----------
DB = "jsa.db"

def db():
    c = sqlite3.connect(DB)
    c.execute("create table if not exists users(name text primary key, salt text, pw text)")
    c.execute("create table if not exists kv(name text, k text, v text, primary key(name,k))")
    return c

def hp(p, salt):
    return hashlib.pbkdf2_hmac("sha256", p.encode(), bytes.fromhex(salt), 100000).hex()

def register(u, p):
    with db() as c:
        if c.execute("select 1 from users where name=?", (u,)).fetchone():
            return False
        s = secrets.token_hex(8)
        c.execute("insert into users values(?,?,?)", (u, s, hp(p, s)))
    return True

def check_login(u, p):
    with db() as c:
        r = c.execute("select salt,pw from users where name=?", (u,)).fetchone()
    return bool(r) and secrets.compare_digest(hp(p, r[0]), r[1])

def kv_get(k, default=None):
    with db() as c:
        r = c.execute("select v from kv where name=? and k=?", (S.user, k)).fetchone()
    return json.loads(r[0]) if r else default

def save_all():
    if S.user:
        with db() as c:
            c.execute("insert or replace into kv values(?,?,?)", (S.user, "tasks", json.dumps(S.tasks)))
            c.execute("insert or replace into kv values(?,?,?)", (S.user, "prefs", json.dumps({"name": S.name, "careers": S.careers})))

def sign_in(u):
    S.user = u
    prefs = kv_get("prefs", {})
    S.name = prefs.get("name", S.name); S.careers = prefs.get("careers", S.careers)
    saved = kv_get("tasks")
    if saved and all("text" in x for x in saved):
        S.tasks = saved
    save_all()

def sign_out():
    S.update(user=None, name="", careers=[], msgs=[], tasks=[dict(x) for x in DEFAULT_TASKS])

# ---------- assistant ----------
def sample_answer(q):
    v = q.lower()
    if re.search(r"job|career|work|skill", v):
        return "A helpful first step is to name the kind of work you enjoy and the skills you already use. You could explore a local skill-development centre or apprenticeship option, then check the official eligibility and dates. Want to add a career research task to your planner?"
    if re.search(r"scheme|money|benefit|support|student", v):
        return "There may be different support options depending on your age, location, household and current situation. Start with the Schemes page to see illustrative examples, then confirm details on the relevant official portal or at a nearby service centre."
    if re.search(r"study|exam|plan|learn", v):
        return "Try making the goal smaller: choose one topic, set a 25-minute focus block, and leave five minutes to note what you understood. The planner can help you keep a gentle daily rhythm."
    if re.search(r"women|safety|help", v):
        return "If you are in immediate danger, contact local emergency services (112 in India) or someone you trust now. For non-urgent support, a nearby women’s support organisation or official helpline can help you understand your options. I can help you make a list of questions to ask."
    return "Thanks for sharing that. A good next step is to clarify what matters most right now, then find one trusted local or official source to check. I can help you explore support schemes, work and learning options, or make a simple plan."

def ai(history):
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        try:
            import anthropic
            r = anthropic.Anthropic(api_key=key).messages.create(
                model=os.environ.get("JSA_MODEL", "claude-sonnet-5-5"), max_tokens=500,
                system="You are Saathi, a kind guidance companion for students, job seekers, women and senior citizens in India. "
                       f"Reply briefly in {L}. Give examples, not guarantees; tell people to verify with official sources. "
                       "If someone may be in danger, advise calling 112.", messages=history)
            return r.content[0].text
        except Exception:
            pass
    return sample_answer(history[-1]["content"])

# ---------- small UI helpers ----------
def head(e, ti, d):
    st.markdown(f"<div class='ph'><div class='eb'>{t('head:' + e)}</div><h1>{t('head:' + ti)}</h1><p class='mute'>{t('head:' + d)}</p></div>", unsafe_allow_html=True)

def caveat():
    st.markdown(f"<div class='warn'><b>{t('common:Sample information only.')}</b> "
                f"{t('common:This demo is not connected to live AI, government databases, or current job listings. Please verify requirements, dates and eligibility with official sources.')}</div>", unsafe_allow_html=True)

def row_head(eyebrow, title):
    st.markdown(f"<div class='eb' style='margin-top:26px'>{eyebrow}</div><h2 class='h2'>{title}</h2>", unsafe_allow_html=True)

# ---------- pages ----------
def p_home():
    a, b = st.columns([3, 2], vertical_alignment="center")
    a.markdown(f"<div class='eb'>{date.today().strftime('%A, %d %B')}</div>", unsafe_allow_html=True)
    with b:
        st.page_link(P["profile"], label=t("dashboard:Your space, your pace"), icon=":material/notifications:")
    welcome = t("dashboard:Welcome") + ((", " + esc(S.name)) if S.name else "") + ". "
    h1 = t("dashboard:A little guidance.") + "<br>" + t("dashboard:A lot more possible.")
    with st.container(key="hero"):
        st.markdown(f"<span class='pill'>✦ {t('dashboard:YOUR NEXT STEP STARTS HERE')}</span><div class='h1'>{h1}</div>"
                    f"<p class='hp'>{welcome}{t('dashboard:Find a benefit, plan your learning, or talk through what comes next — one clear step at a time.')}</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1, st.container(key="hb1"):
            st.page_link(P["ask"], label=t("dashboard:Talk to Saathi") + " →")
        with c2, st.container(key="hb2"):
            st.page_link(P["sch"], label=t("dashboard:Explore support"))
        st.markdown(f"<div class='priv'>🛡️ {t('dashboard:Private by design in this demo. Your information stays in this browser.')}</div>", unsafe_allow_html=True)
    row_head(t("dashboard:Make it yours"), t("dashboard:Where would you like to begin?"))
    st.caption(t("dashboard:Choose a path that feels right"))
    for pair in (HOME_CARDS[:2], HOME_CARDS[2:]):
        for col, (k, ic, tag, label, note) in zip(st.columns(2), pair):
            with col, st.container(key="card_" + k):
                st.page_link(P[k], label=f"{t('dashboard:' + tag)}\n**{t('dashboard:' + label)}**\n{t('dashboard:' + note)}", icon=ic)
    st.markdown(f"<div class='card'><div class='eb'>{t('dashboard:A thought for today')}</div><h2 class='h2'>{t('dashboard:Small steps still move you forward.')}</h2>"
                f"<p class='mute'>{t('dashboard:You don’t need to figure everything out today. Choose one thing that matters, and give it a little attention.')}</p></div>", unsafe_allow_html=True)
    st.page_link(P["plan"], label=t("dashboard:Plan one small thing") + " →")
    caveat()

def p_ask():
    head("A friendly place to start", "Ask Saathi", "Talk through a question, find a starting point, or make a plan. Responses here are examples, not live AI advice.")
    main, side = st.columns([2, 1])
    pending = None
    with main, st.container(key="chatbox"):
        h, x = st.columns([6, 1], vertical_alignment="center")
        h.markdown(f"🌱 **Saathi**<br><span class='mute'>● {t('common:Sample mode · No live service')}</span>", unsafe_allow_html=True)
        if x.button("✕", key="reset", help="Start a fresh conversation"):
            S.msgs = []; st.rerun()
        st.chat_message("assistant").write(INTRO)
        for m in S.msgs:
            st.chat_message(m["role"]).write(m["content"])
        if not S.msgs:
            st.caption(t("common:Try asking about"))
            for i, s in enumerate(["Finding a skill course", "Planning my studies", "Support for my family"]):
                if st.button(t("common:" + s), key=f"sg{i}"):
                    pending = s
    with side:
        caveat()
        items = "".join(f"<div class='ck'>✓ {t(k)}</div>" for k in ["common:Ask in your own words", "common:Keep personal details private", "common:Double-check key information"])
        st.markdown(f"<div class='card'><div class='eb'>Keep in mind</div><h3 class='ct'>{t('common:Your choices matter.')}</h3>"
                    f"<p class='mute'>Saathi helps you explore a next step. For important decisions, verify information with a trusted person or official source.</p>{items}</div>", unsafe_allow_html=True)
        st.page_link(P["plan"], label=f"{t('common:Ready to act?')}\n**{t('common:Make a small plan')}** →", icon=":material/calendar_month:")
    q = st.chat_input(t("common:Write your question…")) or pending
    if q:
        S.msgs.append({"role": "user", "content": q})
        with st.spinner("…"):
            S.msgs.append({"role": "assistant", "content": ai(S.msgs)})
        st.rerun()

def p_sch():
    head("Find a helpful starting point", "Support that meets you here", "Explore a few illustrative support categories and use the simple checker to think about what to ask next.")
    caveat()
    with st.container(key="quick"):
        st.markdown(f"<div class='eb'>{t('scheme:Quick private check')}</div><h2 class='h2'>{t('scheme:What kind of support are you looking for?')}</h2>"
                    "<p class='mute'>This is a sample matching tool, not an official eligibility decision. Your entries are not sent anywhere.</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        age = c1.selectbox(t("scheme:Your age group"), ["", "Under 18", "18–29", "30–59", "60+"], format_func=lambda a: a or t("scheme:Choose one"))
        state = c2.text_input(t("scheme:State or union territory"), placeholder=t("scheme:For example, Maharashtra"))
        if st.button(t("common:Show sample starting points"), type="primary", use_container_width=True):
            S.checked = True
        if S.checked:
            pick = [s for s in SCHEMES if not age or (s["cat"] == "Senior citizens") == (age == "60+")][:3]
            pills = " ".join(f"<span class='tag'>{s['title']}</span>" for s in pick)
            where = (f" ({age})" if age else "") + (f" in {esc(state)}" if state else "")
            st.markdown(f"<div class='res'><b>✓ {t('common:A few places to begin')}</b><p class='mute'>Based on the details you entered{where}, explore the examples below. "
                        f"This is not a confirmed match or eligibility result; check with an official source.</p>{pills}</div>", unsafe_allow_html=True)
    a, b = st.columns([3, 2], vertical_alignment="bottom")
    a.markdown(f"<div class='eb' style='margin-top:26px'>{t('scheme:Explore by need')}</div><h2 class='h2'>{t('scheme:A few places to begin')}</h2>", unsafe_allow_html=True)
    q = b.text_input("q", placeholder=t("common:Search examples"), label_visibility="collapsed", key="sq")
    cat = st.pills("cat", ["Everyone", "Students", "Job seekers", "Women", "Senior citizens"], default="Everyone",
                   format_func=lambda c: t("filter:" + c), label_visibility="collapsed", key="scat") or "Everyone"
    items = [s for s in SCHEMES if (cat == "Everyone" or s["cat"] == cat) and q.lower() in f"{s['title']} {s['desc']} {s['kw']}".lower()]
    cols = st.columns(2)
    for i, s in enumerate(items):
        with cols[i % 2], st.container(key=f"sc_{i}"):
            st.markdown(f"<div class='tilerow'><span class='tile' style='background:{s['tone']};color:{s['ic']}'>{s['emoji']}</span><span class='tag'>{s['tag']}</span></div>"
                        f"<h3 class='ct'>{s['title']}</h3><p class='mute'>{s['desc']}</p><div class='for'>For: {s['aud']}</div>", unsafe_allow_html=True)
            with st.expander(t("common:Check example") + " →"):
                st.write(f"Suitable for: {s['aud']}." + (f" Age group you chose: {age}." if age else "") + (f" State: {state}." if state else "")
                         + " Confirm eligibility, dates and documents on the official portal or at a nearby service centre.")
    if not items:
        st.info("No examples found. Try a different phrase or clear the category filter.")
        st.button(t("common:Clear filters"), on_click=lambda: S.update(scat="Everyone", sq=""))

def p_car():
    head("Work, skills & possibilities", "Build a path that fits you", "Explore career ideas and simple next steps. These are examples for reflection, not live vacancies or placement offers.")
    caveat()
    st.markdown("<div class='careerhero'><span class='tag'>START WITH WHAT YOU KNOW</span><h2 class='h2' style='font-size:1.9rem'>Your experience is already a kind of skill.</h2>"
                "<p class='mute'>Care work, fixing things, helping a neighbour, using a phone — name what you do well. Then find a way to build on it.</p></div>", unsafe_allow_html=True)
    st.page_link(P["plan"], label="Plan your next step →")
    a, b = st.columns([3, 2], vertical_alignment="bottom")
    a.markdown(f"<div class='eb' style='margin-top:26px'>{t('common:Ideas to explore')}</div><h2 class='h2'>{t('common:Paths, not promises')}</h2>", unsafe_allow_html=True)
    q = b.text_input("q", placeholder=t("common:Search career ideas"), label_visibility="collapsed", key="cq")
    kinds = ["All paths"] + [c["type"] for c in CAREERS]
    kind = st.pills("kind", kinds, default="All paths", format_func=lambda k: t("filter:" + k), label_visibility="collapsed", key="ckind") or "All paths"
    items = [c for c in CAREERS if (kind == "All paths" or c["type"] == kind) and q.lower() in f"{c['role']} {c['type']} {c['skills']}".lower()]
    cols = st.columns(2)
    for i, c in enumerate(items):
        with cols[i % 2], st.container(key=f"cc_{i}"):
            st.markdown(f"<div class='eb'>{c['mark']}</div><h3 class='ct'>{c['role']}</h3><p class='mute'>{c['detail']}</p>"
                        f"<div class='for'><div class='eb'>{t('common:Useful strengths')}</div><b style='font-size:13px'>{c['skills']}</b></div>", unsafe_allow_html=True)
            saved = c["role"] in S.careers
            if st.button(("✓ " + t("common:Saved to this browser")) if saved else t("common:Keep this in mind"), key=f"cs{i}", type="primary" if saved else "secondary"):
                S.careers = [r for r in S.careers if r != c["role"]] if saved else S.careers + [c["role"]]
                save_all(); st.rerun()
    if not items:
        st.info("No matches yet. Try a broader search.")
    st.markdown("<div class='card' style='margin-top:18px'><div class='eb'>Keep learning</div><h3 class='ct'>The next step can be a conversation.</h3>"
                "<p class='mute'>Ask Saathi to help you think through what you enjoy and what to explore.</p></div>", unsafe_allow_html=True)
    st.page_link(P["ask"], label=t("common:Talk it through") + " →")

def p_plan():
    head("A gentle rhythm, built by you", "Your planner", "Keep your next steps small and doable. Your tasks are saved only in this browser.")
    d, n = sum(x["done"] for x in S.tasks), len(S.tasks)
    prog = {"English": f"{d} of {n} steps completed", "हिन्दी": f"{n} में से {d} कदम पूरे", "मराठी": f"{n} पैकी {d} पावले पूर्ण"}[L]
    c1, c2 = st.columns(2)
    with c1, st.container(key="stat1"):
        st.markdown(f"<div class='eb'>{t('common:Today’s progress')}</div><h3 class='ct' style='margin-top:6px'>{prog}</h3>", unsafe_allow_html=True)
        st.progress(d / n if n else 0.0)
    with c2, st.container(key="stat2"):
        st.markdown(f"<div class='eb'>{t('common:A REMINDER')}</div><h3 class='ct' style='margin-top:6px'>{t('common:One thing at a time.')}</h3>", unsafe_allow_html=True)
    main, side = st.columns([2, 1])
    with main, st.container(key="plancard"):
        st.markdown(f"<div class='eb'>{t('common:Your to-do list')}</div><h2 class='h2'>{t('common:A few meaningful steps')}</h2>"
                    f"<p class='mute'>{n} {t('common:task' if n == 1 else 'common:tasks')}</p>", unsafe_allow_html=True)
        with st.form("addtask", clear_on_submit=True):
            a, b, c = st.columns([5, 3, 3], vertical_alignment="bottom")
            txt = a.text_input(t("common:Add a task"), placeholder=t("common:What would you like to do?"))
            mins = b.selectbox("⏱", ["5 min", "10 min", "25 min", "45 min"], index=2)
            ok = c.form_submit_button("+ " + t("common:Add"), use_container_width=True)
        if ok and txt.strip():
            S.tasks.insert(0, {"id": uuid.uuid4().hex[:8], "text": txt.strip(), "time": "Today · " + mins, "done": False})
            S.saved = False; save_all(); st.rerun()
        for x in list(S.tasks):
            a, b = st.columns([8, 1], vertical_alignment="center")
            label = ("~~" + x["text"] + "~~") if x["done"] else x["text"]
            new = a.checkbox(f"{label}  ·  {x['time']}", value=x["done"], key="c" + x["id"])
            if new != x["done"]:
                x["done"] = new; save_all(); st.rerun()
            if b.button("✕", key="x" + x["id"], help=t("common:Remove")):
                S.tasks.remove(x); save_all(); st.rerun()
        if not S.tasks:
            st.caption(t("common:A little space for your next idea. Add a task above."))
        st.caption(t("common:Tasks stay on this device. No reminders are sent.") if not S.user else "Signed in: your tasks are saved to your account.")
        if st.button(t("common:Saved on this device") if S.saved else t("common:Save my plan")):
            save_all(); S.saved = True; st.rerun()
    with side:
        st.markdown(f"<div class='card'><div class='eb'>{t('common:A gentle reminder')}</div><h3 class='ct'>{t('common:Progress isn’t always a straight line.')}</h3>"
                    f"<p class='mute'>{t('common:Rest is part of your plan. If today changes, move a task — you’re still moving forward.')}</p>"
                    f"<div class='ck'>♡ {t('common:Make the plan work for you.')}</div></div>", unsafe_allow_html=True)
        caveat()

def p_profile():
    head("Your space, your choices", "Profile & settings", "Set up a few preferences for this demo. Nothing here creates an account or connects to a service.")
    main, side = st.columns([2, 1])
    S["plang"] = L
    with main, st.container(key="profcard"):
        ini = esc(S.name[:2].upper()) if S.name else "AS"
        st.markdown(f"<div style='display:flex;gap:14px;align-items:center'><span class='avatar'>{ini}</span><div><h2 class='h2' style='margin:0'>{esc(S.name) if S.name else t('profile:A Saathi explorer')}</h2>"
                    f"<span class='mute'>{t('profile:Demo preferences stored in this browser')}</span></div></div>", unsafe_allow_html=True)
        nm = st.text_input(t("profile:What should we call you?"), value=S.name, placeholder=t("profile:Your name (optional)"))
        st.selectbox(t("profile:Preferred language"), LANGS, key="plang", on_change=lambda: S.update(lang=S.plang))
        st.caption(f"{t('profile:Language preference')}: {t('profile:Some sample descriptions may remain in English.')}")
        if st.button("✓ " + t("profile:Save preferences")):
            S.name = nm; save_all(); st.success(t("profile:Preferences saved"))
    with side:
        st.markdown(f"<div class='card'><div class='eb'>{t('profile:Account & privacy')}</div><h3 class='ct'>{t('profile:No sign-in required')}</h3>"
                    "<p class='mute'>You can use everything without an account. Sign in only if you want your planner and preferences kept for next time. "
                    "This is a demo, so please avoid entering sensitive personal details.</p></div>", unsafe_allow_html=True)
        if not S.user:
            st.page_link(P["login"], label=t("nav:Sign in") + " →")
        caveat()

def auth(mode):
    if S.user:
        st.success(t("auth:Welcome back."))
        st.page_link(P["home"], label=t("auth:Go to your home") + " →")
        return
    login = mode == "login"
    st.markdown(f"<div class='ph'><div class='eb'>{t('auth:Welcome back' if login else 'auth:Start with a name')}</div>"
                f"<h1>{t('auth:Sign in to your space' if login else 'auth:Create your demo profile')}</h1>"
                f"<p class='mute'>{'Sign in to keep your planner and preferences.' if login else t('auth:A simple local profile helps personalize this browser experience.')}</p></div>", unsafe_allow_html=True)
    with st.container(key="authcard"):
        nm = "" if login else st.text_input(t("auth:Your name"), placeholder=t("auth:How should we call you?"), key="rn")
        em = st.text_input(t("auth:Email address"), placeholder="you@example.com", key="em_" + mode).strip().lower()
        pw = st.text_input(t("auth:Password"), type="password", placeholder=t("auth:Enter any 4 or more characters"), key="pw_" + mode)
        if st.button(t("auth:Sign in") if login else t("auth:Create demo profile"), type="primary", use_container_width=True):
            if login:
                if check_login(em, pw):
                    sign_in(em); st.rerun()
                else:
                    st.error("Wrong email or password.")
            elif not em or len(pw) < 4:
                st.error("Enter an email and a password of 4 or more characters.")
            elif register(em, pw):
                S.name = nm.strip(); sign_in(em); st.rerun()
            else:
                st.error("This email is already registered. Please sign in.")
    st.page_link(P["register" if login else "login"], label=t("auth:New here? " if login else "auth:Already have a profile? ") + t("auth:Create a demo profile" if login else "auth:Sign in") + " →")

def p_login():
    auth("login")

def p_register():
    auth("register")

# ---------- navigation (each page has its own URL, so the browser Back button works) ----------
P = {
    "home": st.Page(p_home, title="Jeevan Saathi AI", icon="🌱", default=True),
    "ask": st.Page(p_ask, title="Ask Saathi", url_path="ask"),
    "sch": st.Page(p_sch, title="Schemes", url_path="schemes"),
    "car": st.Page(p_car, title="Careers", url_path="careers"),
    "plan": st.Page(p_plan, title="Planner", url_path="planner"),
    "profile": st.Page(p_profile, title="Profile", url_path="profile"),
    "login": st.Page(p_login, title="Sign in", url_path="login"),
    "register": st.Page(p_register, title="Register", url_path="register"),
}
pg = st.navigation(list(P.values()), position="hidden")
NAV = [("home", ":material/explore:", "nav:Home"), ("ask", ":material/chat_bubble:", "nav:Ask Saathi"),
       ("sch", ":material/account_balance_wallet:", "nav:Schemes & support"), ("car", ":material/work:", "nav:Careers"),
       ("plan", ":material/calendar_month:", "nav:My planner")]
with st.sidebar:
    st.markdown("<div class='brand'><span class='mark'>🌱</span><div>Jeevan Saathi<small>AI · A LITTLE HELP, EVERY DAY</small></div></div>"
                f"<div class='eb' style='margin:22px 0 6px'>{t('shell:Your guide')}</div>", unsafe_allow_html=True)
    for k, ic, lab in NAV:
        st.page_link(P[k], label=t(lab), icon=ic)
    st.selectbox(t("shell:Choose language"), LANGS, key="lang", label_visibility="collapsed")
    st.markdown(f"<div class='tp'><b>🛡️ {t('shell:A thoughtful starting point')}</b><br>{t('shell:Examples are for guidance. Confirm details with the official service before acting.')}</div>"
                f"<div class='eb' style='margin:6px 0'>{t('nav:Your space')}</div>", unsafe_allow_html=True)
    st.page_link(P["profile"], label=t("nav:Profile & settings"), icon=":material/person:")
    if S.user:
        st.caption(S.user)
        st.button("Sign out", on_click=sign_out, icon=":material/logout:")
    else:
        st.page_link(P["login"], label=t("nav:Sign in"), icon=":material/login:")
pg.run()
