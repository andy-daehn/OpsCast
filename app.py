import streamlit as st
import yaml
import os
from datetime import datetime
import folium
from streamlit_folium import st_folium

# Set full width layout and dark theme
st.set_page_config(layout="wide", page_title="OpsCast Brief", page_icon="🌍")

# ---------- CONFIG ---------- #
BRIEFS_DIR = "briefs"
DEFAULT_BRIEF = None  # Disable index.yaml default fallback

# ---------- LOAD BRIEF ---------- #
def load_brief(date_str):
    file_path = os.path.join(BRIEFS_DIR, f"{date_str}.yaml")
    if not os.path.exists(file_path):
        st.error(f"No brief found for {date_str}.")
        return None
    with open(file_path, 'r') as f:
        return yaml.safe_load(f)

# ---------- SIDEBAR ---------- #
brief_files = sorted([f for f in os.listdir(BRIEFS_DIR) if f.endswith(".yaml")])
date_options = [f.replace(".yaml", "") for f in brief_files]

today_str = datetime.today().strftime("%Y-%m-%d")

if DEFAULT_BRIEF and DEFAULT_BRIEF in brief_files:
    default_date = DEFAULT_BRIEF.replace(".yaml", "")
elif today_str in date_options:
    default_date = today_str
else:
    default_date = max(date_options)

selected_date = st.sidebar.selectbox("Select Briefing Date", options=date_options, index=date_options.index(default_date))
brief = load_brief(selected_date)

# ---------- PAGE ---------- #
if brief:
    st.markdown("""
        <style>
            body, .stApp {
                background-color: #111;
                color: #f0f0f0;
            }
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
                color: #ffffff;
            }
            .right-align {
                display: flex;
                justify-content: flex-end;
                margin-bottom: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title(f"OpsCast Brief – {brief['date']}")
    st.caption(f"Last updated: {brief['updated']} | Sources: {', '.join(brief['sources']) if brief['sources'] else 'None listed'}")

    st.markdown(
        f"""
        <div style="background-color: #1f1f1f;
                    border-left: 5px solid #d62728;
                    padding: 16px 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0px 0px 6px rgba(0,0,0,0.4);">
            <div style="font-size: 22px; font-weight: bold; color: #f8f8f8; margin-bottom: 10px;">
                🚨 {brief['headline']}
            </div>
            <div style="font-size: 16px; line-height: 1.6; color: #dddddd;">
                {brief['summary']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )





    left_col, right_col = st.columns([7, 5], gap="small")

    with right_col:
        if brief.get('related_news'):
            st.markdown("\n")
            st.markdown("### 📰 Related News")
            for item in brief['related_news']:
                st.markdown(f"- [{item['title']}]({item['url']})")

        st.markdown("### 🗺️ Crisis Map Overview")

        # 🧭 Inline map legend
        st.markdown(
            """
            <div style="background-color: #222; color: white; padding: 10px; border-radius: 8px; width: 200px; font-size: 14px; margin-bottom: 10px;">
                <b>Legend</b><br>
                🔥 Wildfire<br>
                🌊 Flood<br>
                🌪️ Storm/Tornado<br>
                🦠 Health/Outbreak<br>
                ⚠️ Other
            </div>
            """,
            unsafe_allow_html=True
        )

        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
        lat_lon_pairs = []

        for event in brief.get('events', []):
            if 'latitude' in event and 'longitude' in event:
                lat_lon = (event['latitude'], event['longitude'])
                lat_lon_pairs.append(lat_lon)

                incident_type = event['type'].lower()
                if 'fire' in incident_type:
                    icon_emoji = '🔥'
                elif 'flood' in incident_type:
                    icon_emoji = '🌊'
                elif 'storm' in incident_type or 'tornado' in incident_type:
                    icon_emoji = '🌪️'
                elif 'outbreak' in incident_type or 'health' in incident_type:
                    icon_emoji = '🦠'
                else:
                    icon_emoji = '⚠️'

                popup_text = f"""
                <strong>{event['title']}</strong><br>
                {event['region']}<br>
                {event['type']}<br>
                {event['notes']}
                """.strip()

                tooltip_text = f"{event['title']} ({event['region']})"

                folium.Marker(
                    location=lat_lon,
                    popup=popup_text,
                    tooltip=tooltip_text,
                    icon=folium.DivIcon(html=f"<div style='font-size: 20px;'>{icon_emoji}</div>")
                ).add_to(m)

        if lat_lon_pairs:
            m.fit_bounds(lat_lon_pairs)

        st_folium(m, use_container_width=True, height=500)

        st.markdown(
            """
            <div style="margin-top: 10px;"></div>
            """,
            unsafe_allow_html=True
        )


        with right_col:
            if brief.get('collabops'):
                st.markdown("\n")
                st.markdown("### 🔭 Collaboration Operations")
                for item in brief['collabops']:
                    st.markdown(f"- [{item['title']}]({item['url']})")
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;↪️ {item['notes']}", unsafe_allow_html=True)
                    st.markdown("\n")




    with left_col:

        st.markdown("\n")
        st.markdown("### 🗂️ Top Incidents")
        for event in brief['events']:
            with st.container():
                st.subheader(event['title'])
                st.write(f"**Location:** {event['region']}  |  **Type:** {event['type']}")
                st.write(event['notes'])
                if event.get('link'):
                    st.markdown(f"[More Info]({event['link']})")

        st.markdown("\n")
        st.markdown("### 📊 Key Stats")
        for stat in brief['stats']:
            st.markdown(f"<div class='right-align'>", unsafe_allow_html=True)
            st.metric(label=stat['label'], value=stat['value'])
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("\n---\n")
    st.markdown(f"*Built by Crisis Forge Labs*")
