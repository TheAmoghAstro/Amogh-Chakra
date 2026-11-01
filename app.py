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

    ramc = float(obs.sidereal_time())
    eps = math.radians(23.4392911 - 0.0130042 * t)
    lat_r = math.radians(lat)
    
    sin_ramc = math.sin(ramc)
    cos_ramc = math.cos(ramc)
    tan_lat = math.tan(lat_r)
    sin_eps = math.sin(eps)
    cos_eps = math.cos(eps)
    
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

    d = jd - 2451545.0
    omega = (125.04452 - 1934.136261 * (d / 36525.0)) % 360.0
    natal["Rahu"] = to_nirayana(omega)
    natal["Ketu"] = to_nirayana((omega + 180.0) % 360.0)

    return natal

st.title("Amogh Chakra System")
st.caption("100% Automatic Ephemeris Engine • Parashari BAV/SAV • Mega Transits • Timeline")

st.sidebar.header("1. Birth Details (Automatic)")
st.sidebar.header("1. Birth Details (Automatic)")

# Simple Day, Month, Year Selection (1900 to 2050)
c_day, c_month, c_year = st.sidebar.columns([1, 1, 1.2])
with c_day:
    day_val = st.selectbox("Day", range(1, 32), index=15) # Default 16
with c_month:
    month_val = st.selectbox("Month", range(1, 13), index=10) # Default 11 (Nov)
with c_year:
    year_val = st.selectbox("Year", range(1900, 2051), index=76) # Default 1976

dob_val = datetime.date(year_val, month_val, day_val)

tob_val = st.sidebar.time_input("Time of Birth", datetime.time(12, 50))city_coords = {
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
labels = {
    "Lagna": "Lagna", "Sun": "Surya", "Moon": "Chandra", "Mars": "Mangal",
    "Mercury": "Budh", "Jupiter": "Guru", "Venus": "Shukra", "Saturn": "Shani",
    "Rahu": "Rahu", "Ketu": "Ketu"
}

for idx, p in enumerate(planet_order):
    c = cols[idx % 5]
    with c:
        p_data = natal[p]
        st.metric(label=labels[p], value=f"{p_data['sign_name']} ({p_data['sign']})", delta=f"{p_data['deg']}° {p_data['min']}'")

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

st.subheader("3. 60:30:10 Weightage & Timeline Predictions")
tab_daily, tab_monthly, tab_yearly = st.tabs(["Daily Prediction", "Monthly Prediction", "Annual / Yearly Prediction"])

with tab_daily:
    m_s = g_moon - 1
    m_bav = sum(bav_matrices["Moon"][k][m_s] for k in KAKSHYAS)
    m_sav = sav_scores[m_s]
    daily_chancha = ((m_bav / 8.0) * 50) + (max(0, min(50, ((m_sav - 18) / 22.0) * 50)))
    daily_dasha = 72.0
    daily_vedha = 100.0
    daily_net = (daily_chancha * 0.60) + (daily_dasha * 0.30) + (daily_vedha * 0.10)

    st.markdown(f"*Chandra Gochar Sthiti:* {RASHI_NAMES[m_s]} (BAV: {m_bav}/8, SAV: {m_sav})")
    dc1, dc2, dc3, dc4 = st.columns(4)
    dc1.metric("60% Chancha Score", f"{daily_chancha:.1f} / 100")
    dc2.metric("30% Dasha Score", f"{daily_dasha:.1f} / 100")
    dc3.metric("10% Vedha/Kakshya", f"{daily_vedha:.0f} / 100")
    dc4.metric("Daily Net Score", f"{daily_net:.1f}", delta="Shubh" if daily_net >= 65 else "Samanya")

with tab_monthly:
    fast_signs = [g_sun - 1, g_mercury - 1, g_venus - 1, g_mars - 1]
    fast_planets = ["Sun", "Mercury", "Venus", "Mars"]
    sum_b = sum(sum(bav_matrices[p][k][s] for k in KAKSHYAS) for p, s in zip(fast_planets, fast_signs))
    avg_b = sum_b / 4.0
    monthly_chancha = (avg_b / 8.0) * 100
    monthly_net = (monthly_chancha * 0.60) + (72.0 * 0.30) + (100.0 * 0.10)

    st.markdown(f"*Surya-Budh-Shukra-Mangal Sareti BAV:* {avg_b:.1f} / 8")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("60% Chancha Score", f"{monthly_chancha:.1f} / 100")
    mc2.metric("30% Dasha Score", "72.0 / 100")
    mc3.metric("10% Vedha/Kakshya", "100 / 100")
    mc4.metric("Monthly Net Score", f"{monthly_net:.1f}", delta="Shubh" if monthly_net >= 65 else "Samanya")

with tab_yearly:
    sat_s = g_saturn - 1
    jup_s = g_jupiter - 1
    yearly_sav_avg = (sav_scores[sat_s] + sav_scores[jup_s]) / 2.0
    yearly_chancha = max(0, min(100, ((yearly_sav_avg - 18) / 22.0) * 100))
    yearly_net = (yearly_chancha * 0.60) + (72.0 * 0.30) + (100.0 * 0.10)

    st.markdown(f"*Shani & Guru SAV Average:* {yearly_sav_avg:.1f} / 48")
    yc1, yc2, yc3, yc4 = st.columns(4)
    yc1.metric("60% Chancha Score", f"{yearly_chancha:.1f} / 100")
    yc2.metric("30% Dasha Score", "72.0 / 100")
    yc3.metric("10% Vedha/Kakshya", "100 / 100")
    yc4.metric("Annual Net Score", f"{yearly_net:.1f}", delta="Shubh" if yearly_net >= 65 else "Samanya")

st.divider()

st.subheader("4. Shani & Guru Mega Transits Dashboard")
col_sat, col_jup = st.columns(2)

with col_sat:
    sat_bav_val = sum(bav_matrices["Saturn"][k][g_saturn - 1] for k in KAKSHYAS)
    sat_sav_val = sav_scores[g_saturn - 1]
    st.markdown(f"*Shani Gochar: {RASHI_NAMES[g_saturn - 1]} (SAV: {sat_sav_val})*")
    if sat_bav_val >= 4 and sat_sav_val >= 28:
        st.success(f"Anukul BAV: {sat_bav_val}/8 — Shani Maharaj jameen, makan, property ke career ma sthayi faydo karavshe.")
    else:
        st.error(f"Savcheti BAV: {sat_bav_val}/8 — Arogya ane financial nirnayo ma savadhani rakhvi.")

with col_jup:
    jup_bav_val = sum(bav_matrices["Jupiter"][k][g_jupiter - 1] for k in KAKSHYAS)
    jup_sav_val = sav_scores[g_jupiter - 1]
    prob_j = min(98, max(25, int(((jup_bav_val * 5 + jup_sav_val) / 78.0) * 100)))
    st.markdown(f"*Guru Gochar: {RASHI_NAMES[g_jupiter - 1]} (SAV: {jup_sav_val})*")
    st.write(f"Bhagyodaya Sambhavna: *{prob_j}%* (BAV: {jup_bav_val}/8)")
    st.progress(prob_j / 100.0)

st.divider()

st.subheader("5. Bhinnashtakavarga (BAV) Table")
sel_planet = st.selectbox("Select Planet for BAV", main_planets, index=0)

rows = []
for k in KAKSHYAS:
    row_data = [KAKSHYA_LABELS[k]] + bav_matrices[sel_planet][k]
    rows.append(row_data)

col_headers = ["Kakshya"] + [f"{i+1}. {RASHI_NAMES[i].split()[0]}" for i in range(12)]
df = pd.DataFrame(rows, columns=col_headers)

bav_sums = ["BAV Total"]
for s in range(12):
    bav_sums.append(sum(bav_matrices[sel_planet][k][s] for k in KAKSHYAS))
df.loc[len(df)] = bav_sums

st.dataframe(df, use_container_width=True, hide_index=True)
st.caption(f"Sarvashtakavarga (SAV) Total Bindus: {sum(sav_scores)} / 337")
