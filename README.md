📈 YouTube Multi-Video Live Views Dashboard

A beautiful, real-time dashboard that tracks **multiple YouTube videos** simultaneously and shows a **combined total view count**.

Built with **Streamlit**, `yt-dlp`, Plotly, and `streamlit-autorefresh`. Perfect for content creators, artists, and music labels who want to monitor view growth live.

<img width="2947" height="1102" alt="image" src="https://github.com/user-attachments/assets/e3d03092-f2f6-4ef8-89d9-a8d548e85d10" />


✨ Features

- Track **unlimited** YouTube videos at once
- **Live Total Views** – sums views from all added videos
- Beautiful dark-themed UI with glowing numbers (matches professional analytics tools)
- Individual video tabs + combined overview chart
- Auto-updates **every 10 minutes**
- 24-hour rolling history with smooth gradient charts
- No YouTube API key required (uses yt-dlp)
- Fully responsive and mobile-friendly

🚀 Live Demo

https://youtube-views.streamlit.app/

🛠️ How to Run Locally

```bash
# 1. Clone the repository
git clone https://github.com/Fassika/youtube-views-dashboard.git
cd youtube-views-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py

📋 Requirements

Python 3.10+
Streamlit
yt-dlp
pandas
plotly
streamlit-autorefresh

See requirements.txt for exact versions.

📱 How to Use

Open the app
In the sidebar, paste any YouTube video URL and click "Add Video"
Repeat for as many videos as you want (e.g. Teddy Afro - Jember, other tracks, etc.)
Watch the Total Views and individual charts update live every 10 minutes

📊 Example Use Case
Great for tracking:

New music video releases
Multiple tracks from the same artist
Live streams + VODs together
Competitor videos

🌐 Deployed on Streamlit Community Cloud
This app is deployed for free on Streamlit Community Cloud> https://youtube-views.streamlit.app/

🔧 Tech Stack

Frontend: Streamlit + Plotly + Custom CSS
Data: yt-dlp (real-time YouTube scraping)
Deployment: Streamlit Community Cloud (free)

📝 License
Free to use and modify. Feel free to fork and customize!

Made with ❤️ for Ethiopian music creators & fans
If you like this dashboard, feel free to star the repo ⭐ and share it!
