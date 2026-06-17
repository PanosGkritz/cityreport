import streamlit as st
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.db import get_problems, get_categories, get_statuses

try:
    from tab_manage import render_tab_manage
except ImportError:
    def render_tab_manage(df): st.error("Το αρχείο tab_manage.py λείπει!")

try:
    from tab_external_api import render_tab_external
except ImportError:
    def render_tab_external(df): st.error("Το αρχείο tab_external_api.py λείπει!")

try:
    from tab_analytics import render_tab_analytics
except ImportError:
    def render_tab_analytics(df): st.error("Το αρχείο tab_analytics.py λείπει!")

try:
    from tab_llm import render_tab_ai
except ImportError as e:
    def render_tab_ai(df):
        st.error("Το αρχείο tab_llm.py λείπει ή έχει σφάλμα import")
try:
    from tab_photo import render_tab_photo
except ImportError:
    def render_tab_photo(df): st.error("Το αρχείο tab_photo.py λείπει!")

st.set_page_config(page_title="CityReport Dashboard", page_icon="🏙️", layout="wide")
st.title("🏙️ CityReport - Πίνακας Ελέγχου Δήμου")
st.markdown("Διαχείριση, Ανάλυση και Τεχνητή Νοημοσύνη για τα προβλήματα της πόλης.")

categories = get_categories()
statuses = get_statuses()

st.sidebar.header("🔍 Φίλτρα Αναζήτησης")

cat_dict = {c['id']: c['name'] for c in categories}
cat_options = ["Όλες"] + list(cat_dict.values())
selected_cat_name = st.sidebar.selectbox("Κατηγορία Προβλήματος", cat_options)

stat_dict = {s['id']: s['name'] for s in statuses}
stat_options = ["Όλες"] + list(stat_dict.values())
selected_stat_name = st.sidebar.selectbox("Κατάσταση", stat_options)

selected_cat_id = None
if selected_cat_name != "Όλες":
    selected_cat_id = next(k for k, v in cat_dict.items() if v == selected_cat_name)

selected_stat_id = None
if selected_stat_name != "Όλες":
    selected_stat_id = next(k for k, v in stat_dict.items() if v == selected_stat_name)

raw_problems = get_problems(category_id=selected_cat_id, status_id=selected_stat_id)

if raw_problems:
    df = pd.DataFrame(raw_problems)
    df['Κατηγορία'] = df['category_id'].map(cat_dict)
    df['Κατάσταση'] = df['status_id'].map(stat_dict)
else:
    df = pd.DataFrame()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Διαχείριση Αναφορών",
    "📊 Στατιστικά & Χάρτης",
    "🤖 Υποσύστημα AI",
    "🌍 Εξωτερικά APIs",    
    "📷 Προβολή Φωτογραφιών"
])

with tab1:
    if not df.empty:
        render_tab_manage(df)
    else:
        st.info("ℹ️ Δεν βρέθηκαν αναφορές με αυτά τα φίλτρα.")

with tab2:
    render_tab_analytics(df)

with tab3:
    render_tab_ai(df)

with tab4:
    render_tab_external(df)
    
with tab5:
    render_tab_photo(df)