import hashlib, json, os, secrets, sqlite3, uuid
from datetime import date
import streamlit as st

st.set_page_config(page_title="Jeevan Saathi AI", page_icon="🌱", initial_sidebar_state="auto")
DB = "jsa.db"
S = st.session_state

T = {
"en": dict(home="Home", ask="Ask Saathi", sch="Schemes", car="Careers", plan="Planner", acct="Account",
  h1="A little guidance. A lot more possible.", sub="Find a benefit, plan your learning, or talk through what's next, one clear step at a time.",
  age="Your age", grp="Who is it for?", chk="Check", found="Possible matches", none="No match. Try another group or age.",
  q="Search", add="Add", task="What would you like to do?", prog="steps completed", save="Add to planner", saved="Added to planner ✓",
  ph="Write your question…", greet="Namaste. I'm Saathi. What would you like help thinking through today?",
  user="Username", pw="Password", login="Log in", reg="Create account", out="Log out", hi="Hello",
  bad="Wrong username or password", taken="Username already taken", short="Enter a username and a password of 6+ characters",
  note="Sample information only. Verify details with official sources.", All="All",
  Students="Students", Jobseekers="Job seekers", Women="Women", Seniors="Senior citizens", strengths="Useful strengths"),
"hi": dict(home="होम", ask="साथी से पूछें", sch="योजनाएँ", car="करियर", plan="प्लानर", acct="खाता",
  h1="थोड़ा मार्गदर्शन। बहुत कुछ संभव।", sub="लाभ खोजें, पढ़ाई की योजना बनाएँ या आगे की बात करें, एक-एक कदम।",
  age="आपकी उम्र", grp="किसके लिए?", chk="जाँचें", found="संभावित विकल्प", none="कोई विकल्प नहीं मिला। दूसरा वर्ग या उम्र आज़माएँ।",
  q="खोजें", add="जोड़ें", task="आप क्या करना चाहेंगे?", prog="कदम पूरे", save="प्लानर में जोड़ें", saved="प्लानर में जुड़ गया ✓",
  ph="अपना सवाल लिखें…", greet="नमस्ते। मैं साथी हूँ। आज किस बात में मदद चाहिए?",
  user="यूज़रनेम", pw="पासवर्ड", login="लॉग इन", reg="खाता बनाएँ", out="लॉग आउट", hi="नमस्ते",
  bad="यूज़रनेम या पासवर्ड गलत है", taken="यह यूज़रनेम पहले से है", short="यूज़रनेम और 6+ अक्षर का पासवर्ड डालें",
  note="केवल उदाहरण जानकारी। विवरण आधिकारिक स्रोत से जाँचें।", All="सभी",
  Students="विद्यार्थी", Jobseekers="नौकरी खोजने वाले", Women="महिलाएँ", Seniors="वरिष्ठ नागरिक", strengths="उपयोगी ताकतें"),
"mr": dict(home="मुख्यपृष्ठ", ask="साथीला विचारा", sch="योजना", car="करिअर", plan="प्लॅनर", acct="खाते",
  h1="थोडे मार्गदर्शन. खूप काही शक्य.", sub="लाभ शोधा, अभ्यासाचे नियोजन करा किंवा पुढच्या गोष्टींवर बोला, एकेक पाऊल.",
  age="तुमचे वय", grp="कोणासाठी?", chk="तपासा", found="संभाव्य पर्याय", none="पर्याय सापडला नाही. दुसरा गट किंवा वय वापरा.",
  q="शोधा", add="जोडा", task="तुम्हाला काय करायचे आहे?", prog="पावले पूर्ण", save="प्लॅनरमध्ये जोडा", saved="प्लॅनरमध्ये जोडले ✓",
  ph="तुमचा प्रश्न लिहा…", greet="नमस्कार. मी साथी. आज कशात मदत हवी?",
  user="युजरनेम", pw="पासवर्ड", login="लॉग इन", reg="खाते तयार करा", out="लॉग आउट", hi="नमस्कार",
  bad="युजरनेम किंवा पासवर्ड चुकीचा", taken="हे युजरनेम आधीच आहे", short="युजरनेम आणि 6+ अक्षरी पासवर्ड टाका",
  note="फक्त नमुना माहिती. तपशील अधिकृत स्रोतावर तपासा.", All="सर्व",
  Students="विद्यार्थी", Jobseekers="नोकरी शोधणारे", Women="महिला", Seniors="ज्येष्ठ नागरिक", strengths="उपयुक्त ताकद"),
}
LANGS = {"English": "en", "हिन्दी": "hi", "मराठी": "mr"}

T["en"].update(acct="Profile", eb="✨ YOUR NEXT STEP STARTS HERE", talk="Talk to Saathi", exp="Explore support", begin="Where would you like to begin?")
T["hi"].update(acct="प्रोफ़ाइल", eb="✨ आपका अगला कदम यहाँ से शुरू", talk="साथी से बात करें", exp="सहायता खोजें", begin="आप कहाँ से शुरू करना चाहेंगे?")
T["mr"].update(acct="प्रोफाइल", eb="✨ तुमचे पुढचे पाऊल इथून सुरू", talk="साथीशी बोला", exp="मदत शोधा", begin="तुम्हाला कुठून सुरू करायचे आहे?")
CARDS = {
 "sch": {"en": ("Find a support scheme", "Explore sample benefits and check basic eligibility."),
         "hi": ("सहायता योजना खोजें", "उदाहरण लाभ देखें और पात्रता जाँचें।"),
         "mr": ("मदत योजना शोधा", "नमुना लाभ पहा आणि पात्रता तपासा.")},
 "car": {"en": ("Explore your next career", "Learning paths, work options and practical next steps."),
         "hi": ("अपना अगला करियर खोजें", "सीखने के रास्ते, काम के विकल्प और अगले कदम।"),
         "mr": ("तुमचे पुढील करिअर शोधा", "शिकण्याचे मार्ग, कामाचे पर्याय आणि पुढची पावले.")},
 "plan": {"en": ("Build a steady routine", "Turn a big goal into small tasks you can finish."),
          "hi": ("नियमित दिनचर्या बनाएँ", "बड़े लक्ष्य को छोटे कामों में बाँटें।"),
          "mr": ("नियमित दिनक्रम बनवा", "मोठे ध्येय लहान कामांत विभागा.")},
 "ask": {"en": ("Ask what's on your mind", "Try a sample conversation and get a place to start."),
         "hi": ("अपने मन की बात पूछें", "एक नमूना बातचीत करें और शुरुआत पाएँ।"),
         "mr": ("मनातले विचारा", "नमुना संभाषण करा आणि सुरुवात मिळवा.")},
}
T["en"].update(sch="Schemes & support", plan="My planner", prof="Profile & settings", signin="Sign in", guide="YOUR GUIDE", mine="MAKE IT YOURS", choose="Choose a path that feels right",
  priv="Private by design in this demo. Your information stays in this browser.", tp="A thoughtful starting point", tpd="Examples are for guidance. Confirm details with the official service before acting.")
T["hi"].update(sch="योजनाएँ और सहायता", plan="मेरा प्लानर", prof="प्रोफ़ाइल और सेटिंग्स", signin="साइन इन", guide="आपका मार्गदर्शक", mine="इसे अपना बनाएँ", choose="ऐसा रास्ता चुनें जो सही लगे",
  priv="इस डेमो में आपकी जानकारी निजी रहती है और इसी ब्राउज़र में रहती है।", tp="सोच-समझकर शुरुआत", tpd="उदाहरण केवल मार्गदर्शन के लिए हैं। कदम उठाने से पहले आधिकारिक सेवा से विवरण जाँचें।")
T["mr"].update(sch="योजना आणि मदत", plan="माझा प्लॅनर", prof="प्रोफाइल आणि सेटिंग्ज", signin="साइन इन", guide="तुमचा मार्गदर्शक", mine="हे तुमचे करा", choose="तुम्हाला योग्य वाटेल असा मार्ग निवडा",
  priv="या डेमोमध्ये तुमची माहिती खाजगी राहते आणि याच ब्राउझरमध्ये राहते.", tp="विचारपूर्वक सुरुवात", tpd="उदाहरणे फक्त मार्गदर्शनासाठी आहेत. कृती करण्यापूर्वी अधिकृत सेवेकडून तपशील तपासा.")
EB = {"sch": dict(en="SUPPORT", hi="सहायता", mr="मदत"), "car": dict(en="WORK & LEARNING", hi="काम और सीख", mr="काम आणि शिक्षण"),
      "plan": dict(en="ROUTINE", hi="दिनचर्या", mr="दिनक्रम"), "ask": dict(en="CONVERSATION", hi="बातचीत", mr="संवाद")}
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
.st-key-card_sch{--tile:#e1f0ec;--ic:#267a69}.st-key-card_car{--tile:#fbe7de;--ic:#d1693b}
.st-key-card_plan{--tile:#fbefcf;--ic:#b98a1b}.st-key-card_ask{--tile:#e0ecf8;--ic:#3b73b8}
@media(max-width:768px){.block-container{padding-top:4.2rem!important}}
</style>"""

# (title, group key, tag, min_age, max_age, description)
SCHEMES = [
 ("Education support", "Students", "LEARNING", 5, 30, "Illustrative fee assistance and scholarship pathways for eligible learners."),
 ("Skill development", "Jobseekers", "SKILLS", 18, 45, "Examples of training and placement support that may be available locally."),
 ("Women's livelihood support", "Women", "LIVELIHOOD", 18, 70, "Enterprise, self-help group and livelihood resources to explore."),
 ("Senior citizen services", "Seniors", "WELLBEING", 60, 120, "Examples of care, wellbeing and pension information to verify with local offices."),
]
CAREERS = [
 ("Community health worker", "Community service", "Communication, care, local knowledge", "Local public-health and outreach training pathways."),
 ("Solar installation trainee", "Skilled trades", "Practical learning, safety, teamwork", "Vocational courses and apprenticeships in clean-energy work."),
 ("Digital services assistant", "Digital work", "Computer basics, communication, accuracy", "Build digital confidence through a local centre or trusted course."),
 ("Small business / self-help group", "Self-employment", "Planning, craft, customer care", "Local enterprise support and peer-led self-help networks."),
]

# ---------- storage (SQLite; resets if the host wipes its disk) ----------
def db():
    c = sqlite3.connect(DB)
    c.execute("create table if not exists users(name text primary key, salt text, pw text)")
    c.execute("create table if not exists tasks(name text primary key, data text)")
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

def save_tasks():
    if S.user:
        with db() as c:
            c.execute("insert or replace into tasks values(?,?)", (S.user, json.dumps(S.tasks)))

def load_tasks(u):
    with db() as c:
        r = c.execute("select data from tasks where name=?", (u,)).fetchone()
    return json.loads(r[0]) if r else None

# ---------- assistant ----------
def fallback(q):
    q = q.lower()
    if any(w in q for w in ("job", "career", "work", "skill", "course", "नौकरी", "करियर", "नोकरी")):
        return "Name the work you enjoy and the skills you already use, then look for a local skill centre or apprenticeship and check official dates. See the Careers page."
    if any(w in q for w in ("scheme", "money", "benefit", "support", "student", "family", "योजना")):
        return "Support depends on age, location and household. Use the Schemes page to see examples, then confirm on the official portal or a service centre."
    if any(w in q for w in ("study", "exam", "plan", "learn", "पढ़ाई", "अभ्यास")):
        return "Make the goal small: one topic, a 25-minute focus block, then 5 minutes to note what you understood. Add it to the Planner."
    if any(w in q for w in ("safety", "danger", "women", "help")):
        return "If you are in immediate danger, call 112 or someone you trust now. For non-urgent help, a local women's helpline or support group can explain your options."
    return "Thanks for sharing. Decide what matters most right now, then check one trusted official source. I can help with schemes, careers or a simple plan."

def ai(history):
    try:
        key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        key = os.environ.get("ANTHROPIC_API_KEY")
    if key:
        try:
            import anthropic
            lang = {"en": "English", "hi": "Hindi", "mr": "Marathi"}[L]
            r = anthropic.Anthropic(api_key=key).messages.create(
                model=os.environ.get("JSA_MODEL", "claude-sonnet-5-5"), max_tokens=500,
                system=f"You are Saathi, a kind guidance companion for students, job seekers, women and senior citizens in India. "
                       f"Reply briefly in {lang}. Give examples, not guarantees; tell people to verify with official sources. "
                       f"If someone may be in danger, advise calling 112.", messages=history)
            return r.content[0].text
        except Exception:
            pass
    return fallback(history[-1]["content"])

# ---------- state / sidebar ----------
S.setdefault("user", None); S.setdefault("page", "home"); S.setdefault("msgs", [])
S.setdefault("tasks", [{"id": "a", "t": "Review one study topic", "m": "25 min", "d": False},
                       {"id": "b", "t": "Take a screen-free break", "m": "10 min", "d": False}])
st.markdown(CSS, unsafe_allow_html=True)
L = LANGS[S.get("lang", "English")]
t = lambda k: T[L].get(k, T["en"].get(k, k))
ICONS = dict(home=":material/explore:", ask=":material/chat_bubble:", sch=":material/account_balance_wallet:",
             car=":material/work:", plan=":material/calendar_month:", acct=":material/person:")
CI = dict(sch=":material/inbox:", car=":material/work:", plan=":material/calendar_month:", ask=":material/chat_bubble:")

# ---------- pages ----------
def p_home():
    with st.container(key="hero"):
        st.markdown(f"<span class='pill'>✦ {t('eb').replace('✨ ', '')}</span>"
                    f"<div class='h1'>{t('h1').replace('. ', '.<br>').replace('। ', '।<br>')}</div>"
                    f"<p class='hp'>{(S.user + ', ') if S.user else ''}{t('sub')}</p>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1, st.container(key="hb1"):
            st.page_link(P["ask"], label=t("talk") + " →")
        with c2, st.container(key="hb2"):
            st.page_link(P["sch"], label=t("exp"))
        st.markdown(f"<div class='priv'>🛡️ {t('priv')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sec'><div><div class='eb'>{t('mine')}</div><h2>{t('begin')}</h2></div>"
                f"<span class='mute'>{t('choose')}</span></div>", unsafe_allow_html=True)
    for row in (["sch", "car"], ["plan", "ask"]):
        for col, k in zip(st.columns(2), row):
            ti, de = CARDS[k][L]
            with col, st.container(key="card_" + k):
                st.page_link(P[k], label=f"{EB[k][L]}\n**{ti}**\n{de}", icon=CI[k])



def p_ask():
    st.header(t("ask"))
    st.chat_message("assistant").write(t("greet"))
    for m in S.msgs:
        st.chat_message(m["role"]).write(m["content"])
    if q := st.chat_input(t("ph")):
        S.msgs.append({"role": "user", "content": q})
        with st.spinner("…"):
            S.msgs.append({"role": "assistant", "content": ai(S.msgs)})
        st.rerun()


def p_sch():
    st.header(t("sch"))
    c1, c2 = st.columns(2)
    age = c1.number_input(t("age"), 1, 120, 25)
    grp = c2.selectbox(t("grp"), ["All", "Students", "Jobseekers", "Women", "Seniors"], format_func=t)
    word = st.text_input(t("q"))
    hits = [s for s in SCHEMES if (grp == "All" or s[1] == grp) and s[3] <= age <= s[4]
            and word.lower() in " ".join(map(str, s)).lower()]
    st.subheader(t("found"))
    for s in hits:
        with st.container(border=True):
            st.markdown(f"**{s[0]}** · `{s[2]}` · {t(s[1])}")
            st.write(s[5])
    if not hits:
        st.warning(t("none"))
    st.caption(t("note"))


def p_car():
    st.header(t("car"))
    kinds = ["All"] + [c[1] for c in CAREERS]
    kind = st.radio("", kinds, horizontal=True, format_func=lambda k: t(k) if k == "All" else k, label_visibility="collapsed")
    for c in CAREERS:
        if kind in ("All", c[1]):
            with st.container(border=True):
                st.markdown(f"**{c[0]}** · {c[1]}")
                st.write(c[3])
                st.caption(f"{t('strengths')}: {c[2]}")
                if st.button(t("save"), key="s" + c[0]):
                    S.tasks.insert(0, {"id": uuid.uuid4().hex[:8], "t": "Research: " + c[0], "m": "25 min", "d": False})
                    save_tasks(); st.toast(t("saved"))
    st.caption(t("note"))


def p_plan():
    st.header(t("plan"))
    done = sum(x["d"] for x in S.tasks)
    st.progress(done / len(S.tasks) if S.tasks else 0.0, text=f"{done}/{len(S.tasks)} {t('prog')}")
    with st.form("add", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        txt = c1.text_input(t("task")); mins = c2.selectbox("⏱", ["5 min", "10 min", "25 min", "45 min"], index=2)
        if st.form_submit_button(t("add")) and txt.strip():
            S.tasks.insert(0, {"id": uuid.uuid4().hex[:8], "t": txt.strip(), "m": mins, "d": False})
            save_tasks(); st.rerun()
    for x in list(S.tasks):
        a, b = st.columns([6, 1])
        new = a.checkbox(f"{x['t']} · {x['m']}", value=x["d"], key="c" + x["id"])
        if new != x["d"]:
            x["d"] = new; save_tasks(); st.rerun()
        if b.button("✕", key="x" + x["id"]):
            S.tasks.remove(x); save_tasks(); st.rerun()
    if not S.user:
        st.caption("Log in (Account) to keep your tasks saved.")


def p_acct():
    st.header(t("prof") if S.user else t("signin"))
    if S.user:
        st.success(f"{t('hi')}, {S.user}")
        st.button(t("out"), on_click=lambda: S.update(user=None))
    else:
        tl, tr = st.tabs([t("login"), t("reg")])
        with tl:
            u = st.text_input(t("user"), key="lu").strip().lower(); p = st.text_input(t("pw"), type="password", key="lp")
            if st.button(t("login")):
                if check_login(u, p):
                    S.user = u
                    S.tasks = load_tasks(u) or S.tasks
                    save_tasks(); st.rerun()
                else:
                    st.error(t("bad"))
        with tr:
            u = st.text_input(t("user"), key="ru").strip().lower(); p = st.text_input(t("pw"), type="password", key="rp")
            if st.button(t("reg")):
                if not u or len(p) < 6:
                    st.error(t("short"))
                elif register(u, p):
                    S.user = u; save_tasks(); st.rerun()
                else:
                    st.error(t("taken"))


# ---------- navigation (each page has its own URL, so the browser Back button works) ----------
P = {
    "home": st.Page(p_home, title="Jeevan Saathi AI", icon="🌱", default=True),
    "ask": st.Page(p_ask, title="Ask Saathi", url_path="ask"),
    "sch": st.Page(p_sch, title="Schemes", url_path="schemes"),
    "car": st.Page(p_car, title="Careers", url_path="careers"),
    "plan": st.Page(p_plan, title="Planner", url_path="planner"),
    "acct": st.Page(p_acct, title="Account", url_path="account"),
}
pg = st.navigation(list(P.values()), position="hidden")
with st.sidebar:
    st.markdown("<div class='brand'><span class='mark'>🌱</span><div>Jeevan Saathi<small>AI · A LITTLE HELP, EVERY DAY</small></div></div>"
                f"<div class='eb' style='margin:22px 0 6px'>{t('guide')}</div>", unsafe_allow_html=True)
    for k in ["home", "ask", "sch", "car", "plan"]:
        st.page_link(P[k], label=t(k), icon=ICONS[k])
    st.selectbox("🌐", list(LANGS), key="lang")
    st.markdown(f"<div class='tp'><b>🛡️ {t('tp')}</b><br>{t('tpd')}</div>", unsafe_allow_html=True)
    st.page_link(P["acct"], label=t("prof") if S.user else t("signin"), icon=ICONS["acct"] if S.user else ":material/login:")
pg.run()
