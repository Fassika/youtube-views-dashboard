import streamlit as st
import yt_dlp
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import re
from urllib.parse import urlparse, parse_qs

# ====================== CONFIG ======================
st.set_page_config(
    page_title="YouTube Multi-Video Live Views Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sleek dark custom styling (exactly like the original beautiful dashboard)
st.markdown("""
<style>
    .main {background: linear-gradient(180deg, #0f0f17 0%, #1a1a2e 100%);}
    .stPlotlyChart {background: #111827; border-radius: 20px; padding: 10px;}
    .big-number {
        font-size: 5.8rem !important;
        font-weight: 700;
        color: #00ff9d;
        text-shadow: 0 0 30px #00ff9d, 0 0 60px #00ff9d;
        line-height: 1;
        letter-spacing: -6px;
    }
    .live-badge {
        background: #00ff9d;
        color: #000;
        padding: 8px 32px;
        border-radius: 9999px;
        font-weight: 700;
        font-size: 1.35rem;
        display: inline-block;
        box-shadow: 0 0 30px #00ff9d;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.7; } }
    .video-card {
        background: rgba(17, 24, 39, 0.8);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(0, 255, 157, 0.2);
    }
</style>
""", unsafe_allow_html=True)

st.title("📈 Multi-Video YouTube Real-Time Views Dashboard")
st.caption("Track unlimited YouTube videos • Live total count • Auto-updates every 10 minutes • Beautiful dark design")

# ====================== HELPERS ======================
def extract_video_id(url: str):
    """Extract YouTube video ID from any URL format"""
    if not url:
        return None
    # youtu.be format
    if "youtu.be" in url:
        return url.split("/")[-1].split("?")[0]
    # youtube.com/watch?v= format
    parsed = urlparse(url)
    if parsed.query:
        return parse_qs(parsed.query).get("v", [None])[0]
    return None

@st.cache_data(ttl=600)  # 10-minute cache – perfect for live updates
def fetch_video_data(video_id: str):
    """Fetch current views, title & channel using yt-dlp (no API key needed)"""
    if not video_id:
        return None, None, None
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            return (
                info.get("view_count", 0),
                info.get("title", "Unknown Title"),
                info.get("channel", "Unknown Channel")
            )
    except Exception:
        return None, None, None

# ====================== SESSION STATE ======================
if "videos" not in st.session_state:
    st.session_state.videos = {}          # video_id → {title, channel, history: list of dicts}
if "video_order" not in st.session_state:
    st.session_state.video_order = []     # preserves order of addition

# ====================== SIDEBAR – Manage Videos ======================
with st.sidebar:
    st.subheader("➕ Add New Video")
    new_url = st.text_input("YouTube Video URL", placeholder="https://youtu.be/PA2aWF37Ljk")
    
    if st.button("➕ Add Video", type="primary", use_container_width=True):
        if new_url:
            vid = extract_video_id(new_url)
            if vid and vid not in st.session_state.videos:
                views, title, channel = fetch_video_data(vid)
                if views is not None:
                    st.session_state.videos[vid] = {
                        "title": title or "Unknown",
                        "channel": channel or "Unknown",
                        "history": [{"timestamp": datetime.now(), "views": views}]
                    }
                    st.session_state.video_order.append(vid)
                    st.success(f"✅ Added: {title[:40]}")
                    st.rerun()
                else:
                    st.error("❌ Could not fetch video data")
            elif vid in st.session_state.videos:
                st.warning("⚠️ Video already added")
            else:
                st.error("Invalid YouTube URL")
        else:
            st.warning("Enter a URL first")

    st.divider()
    st.subheader(f"📋 Tracked Videos ({len(st.session_state.video_order)})")

    if st.session_state.video_order:
        for i, vid in enumerate(st.session_state.video_order[:]):
            data = st.session_state.videos[vid]
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(f"**{data['title'][:38]}**" if len(data['title']) > 38 else f"**{data['title']}**")
            with col2:
                if st.button("🗑", key=f"del_{vid}"):
                    del st.session_state.videos[vid]
                    st.session_state.video_order.pop(i)
                    st.rerun()
    else:
        st.info("No videos yet – add one above!")

    st.divider()
    if st.button("🧹 Clear All Videos", type="secondary"):
        st.session_state.videos = {}
        st.session_state.video_order = []
        st.rerun()

    st.caption("💡 All data is stored only in your browser session.\nAuto-updates every 10 minutes.")

# ====================== MAIN DASHBOARD ======================
if not st.session_state.video_order:
    st.info("👆 Start by adding YouTube videos in the sidebar.\n\nYou can track as many as you want – the total count will sum all views in real time!")
    st.stop()

# Fetch latest data + update history for ALL videos
current_data = {}
now = datetime.now()
cutoff = now - timedelta(hours=24)

for vid in st.session_state.video_order:
    views, title, channel = fetch_video_data(vid)
    if views is not None:
        # Update metadata
        st.session_state.videos[vid]["title"] = title or st.session_state.videos[vid]["title"]
        st.session_state.videos[vid]["channel"] = channel or st.session_state.videos[vid]["channel"]
        
        # Add new data point
        st.session_state.videos[vid]["history"].append({"timestamp": now, "views": views})
        
        # Trim to last 24h
        st.session_state.videos[vid]["history"] = [
            h for h in st.session_state.videos[vid]["history"] 
            if h["timestamp"] > cutoff
        ]
        
        current_data[vid] = {
            "views": views,
            "title": st.session_state.videos[vid]["title"],
            "channel": st.session_state.videos[vid]["channel"]
        }

# ====================== TOTAL COUNT ======================
total_views = sum(item["views"] for item in current_data.values()) if current_data else 0

now = datetime.now(ZoneInfo("UTC"))   # ← UTC time

st.markdown(f"""
<div style="text-align:center; margin-bottom:30px;">
    <h2 style="color:#e2e8f0; margin-bottom:8px;">TOTAL VIEWS ACROSS ALL VIDEOS</h2>
    <h1 class="big-number">{total_views:,}</h1>
    <span class="live-badge">LIVE UPDATING</span>
    <p style="color:#64748b; margin-top:12px; font-size:1.1rem;">
        Tracking <strong>{len(current_data)}</strong> videos • 
        Last checked: {now.strftime("%b %d, %I:%M %p")} <strong>UTC</strong>
    </p>
</div>
""", unsafe_allow_html=True)


# ====================== TABS: Overview + Individual Videos ======================
tab_titles = ["🌐 Overview"] + [st.session_state.videos[vid]["title"][:32] + "..." for vid in st.session_state.video_order]
tabs = st.tabs(tab_titles)

# ----- TAB 0: OVERVIEW -----
with tabs[0]:
    st.subheader("Combined View Growth (Last 24 Hours)")
    
    if len(current_data) > 0:
        fig = go.Figure()
        colors = ["#00ff9d", "#00d4ff", "#ff00aa", "#ffd000", "#aaff00", "#ff8800", "#00ffcc"]
        
        for i, vid in enumerate(st.session_state.video_order):
            history = st.session_state.videos[vid]["history"]
            if len(history) >= 2:
                df = pd.DataFrame(history)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                fig.add_trace(go.Scatter(
                    x=df["timestamp"],
                    y=df["views"],
                    mode="lines+markers",
                    name=st.session_state.videos[vid]["title"][:25],
                    line=dict(color=colors[i % len(colors)], width=5),
                    marker=dict(size=6)
                ))
        
        fig.update_layout(
            title="",
            xaxis_title="Time (UTC)",                    # ← Simple & safe way
            yaxis_title="Total Views",
            template="plotly_dark",
            height=560,
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="#111827",
            paper_bgcolor="#111827",
            font=dict(family="Inter, sans-serif", size=14, color="#e2e8f0"),
            yaxis=dict(tickformat=",d", gridcolor="#334155"),
            xaxis=dict(
                gridcolor="#334155",
                tickformat="%I:%M %p"
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary table
        st.subheader("📊 Current View Counts")
        summary_df = pd.DataFrame([
            {
                "Video": current_data[vid]["title"][:45],
                "Channel": current_data[vid]["channel"],
                "Views": f"{current_data[vid]['views']:,}"
            }
            for vid in st.session_state.video_order
        ])
        st.dataframe(summary_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No data yet – refresh or wait 10 minutes")

# ----- INDIVIDUAL VIDEO TABS -----
for idx, vid in enumerate(st.session_state.video_order, start=1):
    with tabs[idx]:
        data = st.session_state.videos[vid]
        latest = data["history"][-1]["views"] if data["history"] else 0
        
        # Single-video header 
        now = datetime.now(ZoneInfo("UTC"))
        
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <div style="display:flex; align-items:center; justify-content:center; gap:12px; margin-bottom:16px;">
                <div style="background:#ff0000; color:white; width:38px; height:26px; border-radius:4px; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:18px;">▶</div>
                <h2 style="margin:0; font-size:1.5rem; font-weight:600;">{data['title']}</h2>
            </div>
            <h1 class="big-number">{latest:,}</h1>
            <span class="live-badge">LIVE UPDATING</span>
            <p style="color:#64748b; margin-top:12px;">
                by <strong>{data['channel']}</strong> •Last checked: {now.strftime("%b %d, %I:%M %p")} <strong>UTC</strong>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        
        # Individual chart
        if len(data["history"]) >= 2:
            df = pd.DataFrame(data["history"])
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["timestamp"],
                y=df["views"],
                mode="lines+markers",
                line=dict(color="#00ff9d", width=5),
                marker=dict(size=7, color="#00ff9d"),
                fill="tozeroy",
                fillcolor="rgba(0, 255, 157, 0.15)"
            ))
            fig.update_layout(
                title="View Count Growth • Last 24 Hours",
                xaxis_title="Time (UTC)",                    
                yaxis_title="Total Views",
                template="plotly_dark",
                height=460,
                margin=dict(l=20, r=20, t=50, b=20),
                plot_bgcolor="#111827",
                paper_bgcolor="#111827",
                font=dict(family="Inter, sans-serif", size=14),
                yaxis=dict(tickformat=",d", gridcolor="#334155"),
                xaxis=dict(
                    gridcolor="#334155",
                    tickformat="%I:%M %p"
                )
            )
            
                        
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Waiting for more data points...")

# ====================== AUTO REFRESH ======================
st.caption("🚀 Dashboard auto-refreshes every 10 minutes (uses streamlit-autorefresh)")
try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=600000, limit=10000, key="multi_refresh")  # 10 minutes
except ImportError:
    st.warning("⚠️ For automatic updates, run: `pip install streamlit-autorefresh`")
    if st.button("🔄 Manual Refresh Now"):
        st.rerun()

# ====================== INSTALL & RUN ======================
st.sidebar.markdown("---")
st.sidebar.caption("**Installation (one time)**")
st.sidebar.code("pip install streamlit yt-dlp pandas plotly streamlit-autorefresh", language="bash")
st.sidebar.caption("**Run the app**")
st.sidebar.code("streamlit run app.py", language="bash")
