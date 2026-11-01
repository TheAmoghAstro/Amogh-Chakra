import streamlit as st
import swisseph as swe
import pandas as pd
import datetime

# Page configuration
st.set_page_config(page_title="અમોઘ ચક્ર • Swiss Ephemeris", layout="wide")

# Set Lahiri Chitra Paksha Ayanamsha
swe.set_sid_mode(swe.SIDM_LAHIRI)

RASHI_NAMES = [
    "મેષ", "વૃષભ", "મિથુન", "કર્ક", "સિંહ", "કન્યા",
    "તુલા", "વૃશ્ચિક", "ધન", "મકર", "કુંભ", "મીન"
]

KAKSHYAS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
KAKSHYA_LABELS = {
    "Saturn": "શનિ", "Jupiter": "ગુરુ", "Mars": "મંગળ", "Sun": "સૂર્ય",
    "Venus": "શુક્ર", "Mercury": "બુધ", "Moon": "ચંદ્ર", "Lagna": "લગ્ન"
}

# Parashari Benefic House rules
BAV_RULES = {
    "Sun": {
        "Sun": [1,2,4,7,8,9,10,11], "Moon": [3,6,10,11], "Mars": [1,2,4,7,8,9,10,11],
        "Mercury": [3,5,6,9,10,11,12], "Jupiter": [5,6,9,11], "Venus": [6,7,12],
        "Saturn": [1,2,4,7,8,9,10,11], "Lagna": [3,4,6,10,11,12]
    },
    "Moon": {
        "Sun": [3,6,7,8,10,11], "Moon": [1,3,6,7,10,11], "Mars": [2,3,5,6,9,10,11],
        "Mercury": [1,3,4,5,7,8,10,11], "Jupiter": [1,4,7,8,10,11,12], "Venus": [3,4,5,7,9,10,11],
        "Saturn": [3,5,6,11], "Lagna": [3,6,10,11]
    },
    "Mars": {
        "Sun": [3,5,6,10,11], "Moon": [3,6,11], "Mars": [1,2,4,7,8,10,11],
        "Mercury": [3,5,6,11], "Jupiter": [6,10,11,12], "Venus": [6,8,11,12],
        "Saturn": [1,4,7,8,9,10,11], "Lagna": [1,3,6,10,11]
    },
    "Mercury": {
        "Sun": [5,6,9,11,12], "Moon": [2,4,6,8,10,11], "Mars": [1,2,4,7,8,9,10,11],
        "Mercury": [1,3,5,6,9,10,11,12], "Jupiter": [6,8,11,12], "Venus": [1,2,3,4,5,8,9,11],
        "Saturn": [1,2,4,7,8,9,10,11], "Lagna": [1,2,4,6,8,10,11]
    },
    "Jupiter": {
        "Sun": [1,2,3,4,7,8,9,10,11], "Moon": [2,5,7,9,11], "Mars": [1,2,4,7,8,10,11],
        "Mercury": [1,2,4,5,6,9,10,11], "Jupiter": [1,2,3,4,7,8,10,11], "Venus": [2,5,6,9,10,11],
        "Saturn": [3,5,6,12], "Lagna": [1,2,4,5,6,7,9,10,11]
    },
    "Venus": {
        "Sun": [8,11,12], "Moon": [1,2,3,4,5,8,9,11,12], "Mars": [3,5,6,9,11,12],
        "Mercury": [3,5,6,9,11], "Jupiter": [5,8,9,10,11], "Venus": [1,2,3,4,5,8,9,10,11],
        "Saturn": [3,4,5,8,9,10,11], "Lagna": [1,2,3,4,5,8,9,11]
    },
    "Saturn": {
        "Sun": [1,2,4,7,8,10,11], "Moon": [3,6,11], "Mars": [3,5,6,10,11,12],
        "Mercury": [6,8,9,10,11,12], "Jupiter": [5,6,11,12], "Venus": [6,11,12],
        "Saturn": [3,5,6,11], "Lagna": [1,3,4,6,10,11]
    }
}

def format_coord(deg):
    deg_norm = deg % 360.0
    sign_idx = int(deg_norm // 30) + 1
    rem = deg_norm % 30.0
    deg_val = int(rem)
    min_val = int((rem - deg_val) * 60)
    return {
        "sign": sign_idx,
        "sign_name": RASHI_NAMES[sign_idx - 1],
        "deg": deg_val,
        "min": min_val,
        "total_deg": deg_norm
    }

def get_swiss_ephemeris(dob, tob, lat, lon):
    ut_hour = (tob.hour + tob.minute / 60.0) - 5.5
    jd_ut = swe.julday(dob.year, dob.month, dob.day, ut_hour)

    # 1. Lagna
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', swe.FLG_SIDEREAL)
    natal = {"Lagna": format_coord(ascmc[0])}

    planets_map = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    for p_name, p_id in planets_map.items():
        res, _ = swe.calc_ut(jd_ut, p_id, swe.FLG_SIDEREAL)
        natal[p_name] = format_coord(res[0])

    ketu_total = (natal["Rahu"]["total_deg"] + 180.0) % 360.0
    natal["Ketu"] = format_coord(ketu_total)
    return natal

# Header
st.title("અમોઘ ચક્ર (Amogh Chakra System)")
st.caption("Powered by Swiss Ephemeris • 60% Chancha + 30% Dasha + 10% Kakshya")

# Sidebar - Inputs
st.sidebar.header("૧. જન્મ વિગતો")
dob_input = st.sidebar.date_input("જન્મ તારીખ", datetime.date(1971, 10, 23))
tob_input = st.sidebar.time_input("જન્મ સમય", datetime.time(7, 55))

city_coords = {
    "Vadodara": (22.3072, 73.1812),
    "Ahmedabad": (23.0225, 72.5714),
    "Surat": (21.1702, 72.8311),
    "Rajkot": (22.3039, 70.8022),
    "Bhavnagar": (21.7645, 72.1519),
    "Mumbai": (19.0760, 72.8777)
}
selected_city = st.sidebar.selectbox("જન્મ સ્થળ", list(city_coords.keys()), index=0)
lat, lon = city_coords[selected_city]

# Calculate Natal via Swiss Ephemeris
natal = get_swiss_ephemeris(dob_input, tob_input, lat, lon)

# Display Natal Planets
st.subheader("જન્મ સ્પષ્ટ ગ્રહો (Swiss Ephemeris Accurate)")
cols = st.columns(5)
planet_order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
labels = {"Lagna":"લગ્ન", "Sun":"સૂર્ય", "Moon":"ચંદ્ર", "Mars":"મંગળ", "Mercury":"બુધ", "Jupiter":"ગુરુ", "Venus":"શુક્ર", "Saturn":"શનિ", "Rahu":"રાહુ", "Ketu":"કેતુ"}

for idx, p in enumerate(planet_order):
    c = cols[idx % 5]
    with c:
        p_data = natal[p]
        st.metric(label=labels[p], value=f"{p_data['sign_name']} ({p_data['sign']})", delta=f"{p_data['deg']}° {p_data['min']}'")

# Compute BAV & SAV
bav_matrices = {}
main_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

for target in main_planets:
    matrix = {k: [0]*12 for k in KAKSHYAS}
    for donor in KAKSHYAS:
        donor_sign = natal[donor]["sign"]
        benefic_houses = BAV_RULES[target][donor]
        for h in benefic_houses:
            matrix[donor][((donor_sign - 1) + (h - 1)) % 12] = 1
    bav_matrices[target] = matrix

sav_scores = [0] * 12
for s in range(12):
    s_sum = 0
    for p in main_planets:
        for k in KAKSHYAS:
            s_sum += bav_matrices[p][k][s]
    sav_scores[s] = s_sum

st.divider()

# Mega Transits & Timeline Section
st.subheader("૨. શનિ-ગુરુ મેગા ટ્રાન્ઝિટ્સ (Mega Transits)")
m_col1, m_col2 = st.columns(2)

with m_col1:
    sat_sign = 11 # Default Kumbha
    sat_bav = sum(bav_matrices["Saturn"][k][sat_sign-1] for k in KAKSHYAS)
    sat_sav = sav_scores[sat_sign-1]
    st.markdown(f"*🪐 શનિ ગોચર: કુંભ રાશિ (SAV: {sat_sav})*")
    if sat_bav >= 4 and sat_sav >= 28:
        st.success(f"અનુકૂળ BAV: {sat_bav}/8 — શનિ મહારાજ આ ૨.૫ વર્ષ દરમિયાન જમીન, મકાન કે કરિયરમાં મોટો સ્થાયી ફાયદો કરાવશે.")
    else:
        st.error(f"સાવચેતી BAV: {sat_bav}/8 — આરોગ્ય અને નાણાકીય નિર્ણયોમાં વિશેષ સાવધાની રાખવી.")

with m_col2:
    jup_sign = 2 # Default Vrishabha
    jup_bav = sum(bav_matrices["Jupiter"][k][jup_sign-1] for k in KAKSHYAS)
    jup_sav = sav_scores[jup_sign-1]
    prob = min(98, max(25, int(((jup_bav * 5 + jup_sav) / 78.0) * 100)))
    st.markdown(f"*✨ ગુરુ ગોચર: વૃષભ રાશિ (SAV: {jup_sav})*")
    st.write(f"ભાગ્યોદય & માંગલિક સુખ સંભાવના: *{prob}%* (BAV: {jup_bav}/8)")
    st.progress(prob / 100.0)

st.divider()

# 60:30:10 Weightage Calculator
st.subheader("૩. વેઇટેજ સિસ્ટમ (૬૦% + ૩૦% + ૧૦%)")
t_tab1, t_tab2, t_tab3 = st.tabs(["Daily (રોજિંદું)", "Monthly (માસિક)", "Annual (વાર્ષિક)"])

with t_tab1:
    moon_bav = sum(bav_matrices["Moon"][k][7] for k in KAKSHYAS) # Vrishchik
    chancha_score = ((moon_bav / 8.0) * 50) + (max(0, min(50, ((sav_scores[7] - 18) / 22.0) * 50)))
    dasha_score = 72.0
    vedha_score = 100.0
    net_score = (chancha_score * 0.60) + (dasha_score * 0.30) + (vedha_score * 0.10)
    
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    w_col1.metric("૬૦% ચંચા ચક્ર (BAV/SAV)", f"{chancha_score:.1f} / 100")
    w_col2.metric("૩૦% વિંશોત્તરી દશા", f"{dasha_score:.1f} / 100")
    w_col3.metric("૧૦% વેધ / કક્ષા", f"{vedha_score:.0f} / 100")
    w_col4.metric("Net Life Score", f"{net_score:.1f}", delta="શુભ પરિણામ")

# BAV Table
st.divider()
st.subheader("૪. ભિન્નાષ્ટકવર્ગ (BAV) કોષ્ટક")
selected_p = st.selectbox("ગ્રહ પસંદ કરો", main_planets, index=0)
bav_df = pd.DataFrame(bav_matrices[selected_p], index=[KAKSHYA_LABELS[k] for k in KAKSHYAS])
bav_df.columns = [f"{i+1}. {RASHI_NAMES[i]}" for i in range(12)]
bav_df.loc["BAV સ્કોર"] = bav_df.sum()
st.dataframe(bav_df, use_container_width=True)
st.caption(f"સર્વાષ્ટકવર્ગ (SAV) કુલ પોઈન્ટ્સ: {sum(sav_scores)} / 337")
