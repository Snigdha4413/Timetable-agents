"""Light-blue (Blue Marble) version of the red / cream / deep-blue theme.
Usage in app.py: replace `from theme import inject_theme`
with              `from theme_light import inject_theme`
and use .streamlit/config_light.toml as your .streamlit/config.toml.
"""
import streamlit as st

GOCHUJANG, CRIMSON, CREAM, COSMOS, MARBLE = "#780000", "#C1121F", "#FDF0D5", "#003049", "#669BBC"

_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&display=swap');

:root {{
  --gochujang:{GOCHUJANG}; --crimson:{CRIMSON}; --cream:{CREAM};
  --cosmos:{COSMOS}; --marble:{MARBLE}; --cut:14px;
}}
html, body, [class*="css"], .stApp {{ font-family:'Chakra Petch', sans-serif; color:var(--cosmos); }}

/* background: light blue with a sharp crimson wedge and fine diagonal hatching */
.stApp {{
  background:
    linear-gradient(115deg, transparent 0 80%, var(--crimson) 80% 100%) 0 0/100% 360px no-repeat,
    repeating-linear-gradient(135deg, transparent 0 22px, rgba(0,48,73,.09) 22px 23px),
    var(--marble);
}}

/* headings */
h1 {{ font-weight:700; letter-spacing:.01em; color:var(--cosmos); }}
h1::after {{ content:""; display:block; width:84px; height:6px; margin-top:8px;
            background:var(--crimson); clip-path:polygon(0 0,100% 0,calc(100% - 6px) 100%,0 100%); }}
h2, h3 {{ font-weight:600; color:var(--cosmos); }}

/* metric tiles: deep-blue cards, chamfered corner, coloured spine */
[data-testid="stMetric"] {{
  background:var(--cosmos); border-left:8px solid var(--cream);
  padding:14px 18px;
  clip-path:polygon(0 0, calc(100% - var(--cut)) 0, 100% var(--cut), 100% 100%, 0 100%);
}}
[data-testid="stMetricValue"], [data-testid="stMetricValue"] * {{ color:var(--cream); font-weight:700; }}
[data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {{ color:var(--marble); font-weight:600; }}
div[data-testid="column"]:nth-child(2) [data-testid="stMetric"] {{ border-left-color:var(--crimson); }}
div[data-testid="column"]:nth-child(3) [data-testid="stMetric"] {{ border-left-color:var(--marble); }}

/* buttons: chamfered, solid crimson, flips to deep blue on hover */
.stButton > button, .stDownloadButton > button {{
  font-family:'Chakra Petch'; font-weight:700; letter-spacing:.04em;
  color:var(--cream); background:linear-gradient(180deg, var(--crimson) 0 82%, var(--gochujang) 82% 100%);
  border:0; border-radius:0; padding:.6rem 1.4rem;
  clip-path:polygon(var(--cut) 0, 100% 0, 100% calc(100% - var(--cut)), calc(100% - var(--cut)) 100%, 0 100%, 0 var(--cut));
  transition:background .15s, color .15s, transform .15s;
}}
.stButton > button:hover, .stDownloadButton > button:hover {{
  background:linear-gradient(180deg, var(--cosmos) 0 82%, #00182A 82% 100%);
  color:var(--cream); transform:translateY(-2px);
}}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {{ outline:3px solid var(--cosmos); outline-offset:3px; }}

/* inputs: cream fields, deep-blue text */
input, textarea, [data-baseweb="select"] > div {{
  background:var(--cream) !important; border-radius:0 !important;
  border:2px solid var(--cosmos) !important; color:var(--cosmos) !important;
}}
input:focus, textarea:focus {{ border-color:var(--crimson) !important; box-shadow:0 0 0 2px var(--crimson) !important; }}

/* tabs */
button[role="tab"] {{ font-weight:600; border-radius:0; color:var(--cosmos); }}
button[role="tab"][aria-selected="true"] {{ color:var(--cosmos); }}
[data-baseweb="tab-highlight"] {{ background:var(--crimson) !important; height:4px; }}

/* alerts: cream cards; success = deep blue edge, error = crimson edge */
[data-testid="stAlert"] {{ border-radius:0; background:var(--cream); border:1px solid var(--cosmos); border-left-width:6px;
  clip-path:polygon(0 0, calc(100% - var(--cut)) 0, 100% var(--cut), 100% 100%, 0 100%); }}
[data-testid="stAlert"] * {{ color:var(--cosmos) !important; }}
[data-testid="stAlert"]:has([data-testid="stAlertContentSuccess"]) {{ border-left-color:var(--cosmos); }}
[data-testid="stAlert"]:has([data-testid="stAlertContentError"])   {{ border-left-color:var(--crimson); }}
[data-testid="stAlert"]:has([data-testid="stAlertContentError"]) * {{ color:var(--gochujang) !important; }}

/* tables */
[data-testid="stDataFrame"] {{ border:2px solid var(--cosmos); }}

/* sidebar: cream panel with a crimson edge */
section[data-testid="stSidebar"] {{ background:var(--cream); border-right:4px solid var(--crimson); }}

@media (prefers-reduced-motion: reduce) {{ * {{ transition:none !important; }} }}
</style>
"""

def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)
