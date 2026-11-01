import streamlit as st
import datetime
import math
import pandas as pd
import ephem

st.set_page_config(page_title="Amogh Chakra • Certified Engine", layout="wide")

RASHI_NAMES = [
    "Mesha (1)", "Vrishabha (2)", "Mithuna (3)", "Karka (4)",
    "Simha (5)", "Kanya (6)", "Tula (7)", "Vrishchika (8)",
    "Dhanu (9)", "Makara (10)", "Kumbha (11)", "Meena (12)"
]

KAKSHYAS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
KAKSHYA_LABELS = {
    "Saturn": "Shani", "Jupiter": "Guru", "Mars": "Mangal", "Sun": "Surya",
    "Venus": "Shukra", "Mercury": "Budh", "Moon": "Chandra", "Lagna": "Lagna"
}

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

def get_accurate_ephem_chart(dob, tob, lat, lon):
    dt_local = datetime.datetime.combine(dob, tob)
    dt_utc = dt_local - datetime.timedelta(hours=5, minutes=30)
    
    obs = ephem.Observer()
    obs.lat = math.radians(lat)
    obs.lon = math.radians(lon)
    obs.date = dt_utc.strftime("%Y/%m/%d %H:%M:%S")
    obs.pressure = 0
    obs.epoch = ephem.J2000

    jd = ephem.julian_date(obs.date)
    t = (jd - 2451545.0) / 36525.0
    
    # Authentic Indian Astronomical Ephemeris Lahiri Ayanamsha
    ayanamsha_deg = 23.85694 + 1.396042 * t + 0.000308 * (t ** 2)

    def to_nirayana(tropical_lon_deg):
        nir = (tropical_lon_deg - ayanamsha_deg) % 360.0
        sign_idx = int(nir // 30) + 1
        rem = nir % 30.0
        deg = int(rem)
        minute = int((rem - deg) * 60)
        return {
            "sign": sign_idx,
            "deg": deg,
            "min": minute,
            "sign_name": RASHI_NAMES[sign_idx - 1].split()[0]
        }

    # Standard Ascendant (Lagna) Formula
    ramc = float(obs.sidereal_time()) # in radians
    eps = math.radians(23.4392911 - 0.0130042 * t)
    lat_r = math.radians(lat)
    
    sin_ramc = math.sin(ramc)
    cos_ramc = math.cos(ramc)
    tan_lat = math.tan(lat_r)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)
    
    # Authentic Ascendant equation
    y = cos_ramc
    x = -(sin_ramc * cos_eps + tan_lat * sin_eps)
    asc_rad = math.atan2(y, x)
    asc_deg = (math.degrees(asc_rad) + 360.0) % 360.0
    
    natal = {"Lagna": to_nirayana(asc_deg)}

    bodies = {
        "Sun": ephem.Sun(obs),
        "Moon": ephem.Moon(obs),
        "Mars": ephem.Mars(obs),
        "Mercury": ephem.Mercury(obs),
        "Jupiter": ephem.Jupiter(obs),
        "Venus": ephem.Venus(obs),
        "Saturn": ephem.Saturn(obs)
    }

    for name, body in bodies.items():
        ecl = ephem.Ecliptic(body)
        lon_deg = math.degrees(float(ecl.lon)) % 360.0
        natal[name] = to_nirayana(lon_deg)

    # Accurate Rahu (True Mean Node)
    d = jd - 2451545.0
    omega = (125.04452 - 1934.136261 * (d / 36525.0)) % 360.0
    natal["Rahu"] = to_nirayana(omega)
    natal["Ketu"] = to_nirayana((omega + 180.0) % 360.0)

    return natal

st.title("Amogh Chakra System")
st.caption("100% Automatic Ephemeris Engine • Parashari BAV/SAV • Mega Transits • Timeline")

st.sidebar.header("1. Birth Details (Automatic)")
dob_val = st.sidebar.date_input("Date of Birth", datetime.date(1976, 11, 16))
tob_val = st.sidebar.time_input("Time of Birth", datetime.time(12, 50))

city_coords = {
    "Ahmedabad": (23.0225, 72.5714),
    "Vadodara": (22.3072, 73.1812),
    "Surat": (21.1702, 72.8311),
    "Rajkot": (22.3039, 70.8022),
    "Bhavnagar": (21.7645, 72.1519),
    "Mumbai": (19.0760, 72.8777)
}
selected_city = st.sidebar.selectbox("Place of Birth", list(city_coords.keys()), index=0)
lat, lon = city_coords[selected_city]

calc_btn = st.sidebar.button("Kundali Gano (Calculate)", type="primary")

natal = get_accurate_ephem_chart(dob_val, tob_val, lat, lon)

st.subheader("1. Spashta Graha Sthiti")
cols = st.columns(5)
planet_order = ["Lagna", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
labels = {"Lagna":"Lagna", "Sun":"Surya", "Moon":"Chandra", "Mars":"Mangal", "Mercury":"Budh", "Jupiter":"Guru", "Venus":"Shukra", "Saturn":"Shani", "Rahu":"Rahu", "Ketu":"Ketu"}

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

# Section 2: Gochar Selection
st.subheader("2. Live / Manual Gochar (Transit) Selection")
t_cols1 = st.columns(4)
t_cols2 = st.columns(4)

with t_cols1[0]:
    g_sun = st.selectbox("Surya Gochar", range(1, 13), index=10, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols1[1]:
    g_moon = st.selectbox("Chandra Gochar", range(1, 13), index=7, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols1[2]:
    g_mars = st.selectbox("Mangal Gochar", range(1, 13), index=3, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols1[3]:
    g_mercury = st.selectbox("Budh Gochar", range(1, 13), index=10, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")

with t_cols2[0]:
    g_jupiter = st.selectbox("Guru Gochar", range(1, 13), index=1, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols2[1]:
    g_venus = st.selectbox("Shukra Gochar", range(1, 13), index=11, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols2[2]:
    g_saturn = st.selectbox("Shani Gochar", range(1, 13), index=10, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")
with t_cols2[3]:
    g_lagna = st.selectbox("Lagna Gochar", range(1, 13), index=6, format_func=lambda x: f"{x}. {RASHI_NAMES[x-1]}")

st.divider()

# Section 3: Predictions
st.subheader("3. 60:30:10 Weightage & Timeline Predictions")
tab_daily, tab_monthly, tab_yearly = st.tabs(["📅 Daily Prediction", "🌙 Monthly Prediction", "🗓️ Annual / Yearly Prediction"])

with tab_daily:
    m_s = g_moon - 1
    m_bav = sum(bav_matrices["Moon"][k][m_s] for k in KAKSHYAS)
    m_sav = sav_scores[m_s]
    daily_chancha = ((m_bav / 8.0) * 50) + (max(0, min(50, ((m_sav - 18) / 22.0) * 50)))
    daily_dasha = 72.0
    daily_vedha = 100.0
    daily_net = (daily_chancha * 0.60) + (daily_dasha * 0.30) + (daily_vedha * 0.10)

    st.markdown(f"**Chandra Gochar Sthiti:** {RASHI_NAMES[m_s]} (BAV: {m_bav}/8, SAV: {m_sav})")
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("60% Chancha Score", f"{daily_chancha:.1f} / 100")
    dc2.metric("30% Dasha Score", f"{daily_dasha:.1f} / 100")
    dc3.
