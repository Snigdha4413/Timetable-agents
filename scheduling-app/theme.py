"""Roma-poster theme for the scheduling app.

Cream poster panel on a pink ground, thick black outlines, hard offset
shadows, chunky type, and a little scooter driving across the header.

Usage in app.py, right after st.set_page_config(...):
    from theme import inject_theme, hero
    inject_theme()
    ...
    hero()          # optional animated header strip

Also drop .streamlit/config.toml next to app.py so Streamlit's own widgets
(tables, pickers) use the same light palette.
"""
import streamlit as st

# palette, sampled from the illustration
INK, CREAM, PAPER = "#1A1A1A", "#F6E7CB", "#FFF8E8"
PINK, YELLOW, BLUE = "#EE8FBF", "#F4E04D", "#4350A8"
SKY, ORANGE, GREEN, LAVENDER = "#7FD0EA", "#F0875E", "#9BD37B", "#E4D4EE"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bowlby+One&family=DM+Sans:wght@400;500;700&display=swap');

:root {
  --ink:#1A1A1A; --cream:#F6E7CB; --paper:#FFF8E8;
  --pink:#EE8FBF; --yellow:#F4E04D; --blue:#4350A8;
  --sky:#7FD0EA; --orange:#F0875E; --green:#9BD37B; --lavender:#E4D4EE;
  --line:3px solid var(--ink);
  --shadow:4px 4px 0 var(--ink);
}

/* ---------- page: pink ground, cream poster panel ---------- */
html, body, .stApp, .stApp p, .stApp label, input, textarea, button,
[data-baseweb="tab"], li { font-family:'DM Sans', sans-serif; }
.stApp { background:var(--pink); color:var(--ink); }
header[data-testid="stHeader"] { background:transparent; }

[data-testid="stMainBlockContainer"], .block-container {
  background:
    radial-gradient(rgba(26,26,26,.13) 1.3px, transparent 1.8px) 0 0/22px 22px,
    var(--cream);
  border:4px solid var(--ink); border-radius:22px;
  box-shadow:10px 10px 0 var(--ink);
  max-width:min(1400px, calc(100% - 3rem)) !important;
  margin:1rem auto 2.5rem !important;
  padding:2.2rem 2.4rem 3rem !important;
}

/* ---------- type ---------- */
h1 {
  font-family:'Bowlby One', sans-serif !important; font-weight:400 !important;
  display:inline-block; width:fit-content; line-height:1.2; letter-spacing:.01em;
  padding:.3em .7em .35em !important; margin-bottom:.4rem;
  background:var(--blue); border:4px solid var(--ink); border-radius:14px;
  box-shadow:6px 6px 0 var(--ink);
  transition:transform .2s ease, box-shadow .2s ease;
}
h1, h1 * { color:var(--yellow) !important; text-shadow:none !important; }
h1:hover { transform:translate(-2px,-3px); box-shadow:9px 9px 0 var(--ink); }
h2, h3 {
  font-family:'Bowlby One', sans-serif !important; font-weight:400 !important;
  width:fit-content; color:var(--ink);
  background:linear-gradient(transparent 58%, var(--yellow) 58% 92%, transparent 92%);
}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] *, .stApp small {
  color:var(--ink) !important; font-weight:500; opacity:1 !important; }
[data-testid="stCaptionContainer"] { margin:.9rem 0 .2rem; font-size:1rem; }

/* dashed dividers, like the sprinkles on the poster */
hr { border:0 !important; height:6px; margin:1.6rem 0 !important; opacity:1 !important;
     background:repeating-linear-gradient(90deg, var(--ink) 0 12px, transparent 12px 22px); }

/* ---------- hero strip ---------- */
.hero { position:relative; height:140px; margin:.6rem 0 1.6rem; overflow:hidden;
  background:var(--sky); border:4px solid var(--ink); border-radius:18px; box-shadow:8px 8px 0 var(--ink); }
.hero .tag { position:absolute; left:20px; top:14px; z-index:2;
  font-family:'Bowlby One', sans-serif; font-size:clamp(1.1rem, 2.6vw, 1.9rem); color:var(--pink);
  text-shadow:-2px -2px 0 var(--ink), 2px -2px 0 var(--ink), -2px 2px 0 var(--ink), 2px 2px 0 var(--ink), 0 3px 0 var(--ink); }
.hero .sun { position:absolute; right:9%; top:16px; width:46px; height:46px; border-radius:50%;
  background:var(--pink); border:3px solid var(--ink); animation:bob 4s ease-in-out infinite; }
.hero .cloud { position:absolute; height:18px; width:78px; background:#fff; border:3px solid var(--ink);
  border-radius:999px; animation:drift 26s linear infinite; }
.hero .c1 { top:58px; left:-90px; }
.hero .c2 { top:34px; left:-90px; animation-delay:-13s; width:56px; }
.hero .ground { position:absolute; left:0; right:0; bottom:0; height:42px; background:var(--orange);
  border-top:4px solid var(--ink);
  background-image:radial-gradient(var(--ink) 2px, transparent 2.5px);
  background-size:26px 26px; background-position:6px 8px; }
.hero .scoot { position:absolute; bottom:26px; left:-70px; font-size:46px; line-height:1;
  animation:ride 9s linear infinite; cursor:pointer; user-select:none; }
.hero:hover .scoot { animation-duration:3.5s; }
@keyframes ride  { from { left:-70px; } to { left:calc(100% + 10px); } }
@keyframes drift { from { left:-90px; } to { left:calc(100% + 20px); } }
@keyframes bob   { 0%,100% { transform:translateY(0); } 50% { transform:translateY(8px); } }

/* ---------- metric tiles ---------- */
[data-testid="stMetric"] {
  background:var(--yellow); border:var(--line); border-radius:16px; box-shadow:var(--shadow);
  padding:14px 18px; transform:rotate(-.8deg);
  transition:transform .18s ease, box-shadow .18s ease;
}
[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"], div[data-testid="column"]:nth-child(2) [data-testid="stMetric"] { background:var(--sky); transform:rotate(.7deg); }
[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"], div[data-testid="column"]:nth-child(3) [data-testid="stMetric"] { background:var(--orange); transform:rotate(-.5deg); }
[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"], div[data-testid="column"]:nth-child(4) [data-testid="stMetric"] { background:var(--pink); transform:rotate(.9deg); }
[data-testid="stMetric"]:hover { transform:translate(-3px,-4px) rotate(0deg) !important; box-shadow:8px 9px 0 var(--ink); }
[data-testid="stMetricValue"] { font-family:'Bowlby One', sans-serif; font-weight:400; color:var(--ink); }
[data-testid="stMetricLabel"] { color:var(--ink); font-weight:700; }

/* ---------- buttons: chunky, press down on click ---------- */
.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] > button {
  font-family:'DM Sans', sans-serif; font-weight:700; color:var(--ink);
  background:var(--yellow); border:var(--line); border-radius:14px; box-shadow:var(--shadow);
  padding:.55rem 1.3rem; transition:transform .12s ease, box-shadow .12s ease, background .12s;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
  background:var(--sky); color:var(--ink); border-color:var(--ink);
  transform:translate(-2px,-3px) rotate(-.6deg); box-shadow:7px 8px 0 var(--ink);
}
.stButton > button:active, .stDownloadButton > button:active, [data-testid="stFormSubmitButton"] > button:active {
  transform:translate(4px,4px); box-shadow:0 0 0 var(--ink); background:var(--orange);
}
.stButton > button[kind="primary"], button[data-testid="stBaseButton-primary"] { background:var(--pink); }
.stButton > button[kind="primary"]:hover, button[data-testid="stBaseButton-primary"]:hover { background:var(--yellow); }
.stDownloadButton > button { background:var(--sky); }
.stDownloadButton > button:hover { background:var(--green); }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
  outline:3px solid var(--blue); outline-offset:3px; }

/* ---------- inputs ---------- */
[data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {
  background:var(--paper) !important; border:var(--line) !important; border-radius:12px !important;
  box-shadow:3px 3px 0 var(--ink); transition:box-shadow .15s, transform .15s;
}
[data-baseweb="input"] > div, [data-baseweb="base-input"] { background:transparent !important; border:0 !important; }
[data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within, [data-baseweb="select"] > div:focus-within {
  box-shadow:0 0 0 3px var(--yellow), 5px 5px 0 3px var(--ink) !important; transform:translate(-1px,-1px); }
input, textarea { color:var(--ink) !important; }
[data-baseweb="tag"] { background:var(--blue) !important; color:var(--yellow) !important;
  border:2px solid var(--ink); border-radius:8px !important; }
[data-baseweb="tag"] * { color:var(--yellow) !important; }
[data-baseweb="popover"] > div { border:var(--line); border-radius:12px; box-shadow:5px 5px 0 var(--ink); background:var(--paper); }
[data-baseweb="menu"] { background:var(--paper) !important; }
[role="option"]:hover, [role="option"][aria-selected="true"] { background:var(--yellow) !important; }

/* ---------- tabs: sticker tabs ---------- */
[data-baseweb="tab-list"] { gap:10px; }
[data-baseweb="tab-highlight"], [data-baseweb="tab-border"] { display:none !important; }
button[role="tab"] {
  font-family:'Bowlby One', sans-serif; font-weight:400; color:var(--ink);
  background:var(--paper); border:var(--line); border-radius:14px 14px 0 0; padding:.5rem 1.3rem;
  transition:transform .15s, background .15s;
}
button[role="tab"]:hover { background:var(--sky); transform:translateY(-3px) rotate(-1deg); }
button[role="tab"][aria-selected="true"] { background:var(--blue); color:var(--yellow);
  text-shadow:1px 1px 0 var(--ink); box-shadow:4px 0 0 var(--ink); }
button[role="tab"][aria-selected="true"] p { color:var(--yellow); }

/* ---------- radio: pill stickers ---------- */
[data-testid="stRadio"] [role="radiogroup"] > label {
  background:var(--paper); border:var(--line); border-radius:999px; padding:.3rem 1rem;
  box-shadow:3px 3px 0 var(--ink); transition:transform .12s, box-shadow .12s, background .12s; }
[data-testid="stRadio"] [role="radiogroup"] > label:hover { transform:translate(-1px,-2px) rotate(-1deg); background:var(--sky); }
[data-testid="stRadio"] [role="radiogroup"] > label:has(input:checked) { background:var(--yellow); box-shadow:4px 4px 0 var(--ink); }

/* ---------- alerts: comic callouts ---------- */
[data-testid="stAlert"] { border:var(--line); border-radius:14px; box-shadow:var(--shadow); color:var(--ink); }
[data-testid="stAlert"] * { color:var(--ink); }
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) { background:var(--green); }
[data-testid="stAlert"]:has([data-testid="stAlertContentInfo"])    { background:var(--sky); }
[data-testid="stAlert"]:has([data-testid="stAlertContentWarning"]) { background:var(--yellow); }
[data-testid="stAlert"]:has([data-testid="stAlertContentError"])   { background:var(--orange); }
[data-testid="stToast"] { border:var(--line) !important; border-radius:14px !important;
  box-shadow:var(--shadow) !important; background:var(--paper) !important; color:var(--ink) !important; }

/* ---------- file drop zone: wiggles when you hover ---------- */
[data-testid="stFileUploaderDropzone"] { background:var(--sky); border:3px dashed var(--ink); border-radius:16px;
  transition:transform .18s, background .18s; }
[data-testid="stFileUploaderDropzone"]:hover { background:var(--pink); transform:rotate(-.8deg) scale(1.01); }

/* ---------- tables ---------- */
[data-testid="stDataFrame"] { border:var(--line); border-radius:12px; box-shadow:5px 5px 0 var(--ink); overflow:hidden; }

/* ---------- sidebar: lavender panel ---------- */
section[data-testid="stSidebar"] {
  background:radial-gradient(rgba(26,26,26,.12) 1.3px, transparent 1.8px) 0 0/22px 22px, var(--lavender);
  border-right:4px solid var(--ink); }
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"] { background:transparent; }

@media (max-width:700px) {
  [data-testid="stMainBlockContainer"], .block-container { padding:1.2rem 1rem 2rem !important; box-shadow:6px 6px 0 var(--ink); }
  h1 { font-size:1.7rem !important; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation:none !important; transition:none !important; }
  .hero .scoot { left:40%; }
}
</style>
"""

_HERO = """
<div class="hero" aria-hidden="true">
  <div class="tag">Rooms, faculty, harmony</div>
  <div class="sun"></div>
  <div class="cloud c1"></div><div class="cloud c2"></div>
  <div class="ground"></div>
  <div class="scoot">🛵</div>
</div>
"""


def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def hero():
    """Sky strip with a scooter that speeds up when you hover over it."""
    st.markdown(_HERO, unsafe_allow_html=True)
