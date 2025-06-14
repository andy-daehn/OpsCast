import streamlit as st
import yaml
import os
from datetime import datetime
import folium
from streamlit_folium import st_folium

# ---------- CONFIG ---------- #
BRIEFS_DIR = "briefs"
DEFAULT_BRIEF = "index.yaml"

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
default_date = date_options[-1] if DEFAULT_BRIEF not in brief_files else DEFAULT_BRIEF.replace(".yaml", "")

selected_date = st.sidebar.selectbox("Select Briefing Date", options=date_options, index=date_options.index(default_date))
brief = load_brief(selected_date)

# ---------- PAGE ---------- #
if brief:
    st.title(f"CrisisCast Brief – {brief['date']}")
    st.caption(f"Last updated: {brief['updated']} | Sources: {', '.join(brief['sources'])}")

    st.markdown(f"### {brief['headline']}")
    st.write(brief['summary'])

    # Top layout: map on right, summary on left
    col1, col2 = st.columns([2, 3])

    with col2:
        st.markdown("### 🗺️ Crisis Map Overview")
        m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)

        for event in brief.get('events', []):
            if 'latitude' in event and 'longitude' in event:
                popup_text = f"<strong>{event['title']}</strong><br>{event['region']}<br>{event['type']}<br>{event['notes']}"
                folium.Marker(
                    location=[event['latitude'], event['longitude']],
                    popup=popup_text,
                    tooltip=event['title']
                ).add_to(m)

        st_folium(m, width=500, height=350)

    with col1:
        st.markdown("### Key Stats")
        for stat in brief['stats']:
            st.metric(label=stat['label'], value=stat['value'])

    st.markdown("---")

    # Events
    st.markdown("### Top Incidents")
    for event in brief['events']:
        with st.container():
            st.subheader(event['title'])
            st.write(f"**Location:** {event['region']}  |  **Type:** {event['type']}")
            st.write(event['notes'])
            if event.get('link'):
                st.markdown(f"[More Info]({event['link']})")

    # Podcast Embed
    if brief.get('podcast_link'):
        st.markdown("### 🎙️ Listen to Today's CrisisCast")
        st.audio(brief['podcast_link'])

    # Related News
    if brief.get('related_news'):
        st.markdown("### 📰 Related News")
        for item in brief['related_news']:
            st.markdown(f"- [{item['title']}]({item['url']})")

    st.markdown("---")
    st.markdown(f"*Built by CrisisCast Labs · Powered by Streamlit*")
