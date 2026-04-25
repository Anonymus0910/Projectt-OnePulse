"""
OnePulse - Streamlit Version
All functionality preserved from Flask version
"""

import streamlit as st
import sqlite3
import os
import pickle
import random
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

# ─────────────────────────────────────────────
# APP CONFIGURATION
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="OnePulse Content Updater",
    page_icon="🚀",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'onepulse.db')
MODEL_PATH = os.path.join(BASE_DIR, 'model.pkl')

# ─────────────────────────────────────────────
# DATABASE FUNCTIONS
# ─────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS posts (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            platform       TEXT    NOT NULL,
            title          TEXT    NOT NULL,
            description    TEXT,
            hashtags       TEXT,
            caption        TEXT,
            image_url      TEXT,
            niche          TEXT    DEFAULT 'general',
            scheduled_time TEXT,
            status         TEXT    DEFAULT 'scheduled',
            created_at     TEXT    DEFAULT CURRENT_TIMESTAMP,
            posted_at      TEXT
        );
    ''')
    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# ML MODEL (Same as before)
# ─────────────────────────────────────────────
class OnePulseModel:
    HASHTAG_BANK = {
        'youtube': {
            'general': ['#YouTube', '#Viral', '#Trending', '#Subscribe', '#Creator'],
            'tech': ['#Tech', '#Coding', '#Developer', '#AI', '#MachineLearning'],
            'fitness': ['#Fitness', '#Workout', '#GymLife', '#Health', '#FitFam'],
        },
        'instagram': {
            'general': ['#Instagram', '#InstaGood', '#Explore', '#Reels', '#Trending'],
            'tech': ['#TechLife', '#Innovation', '#Coding', '#SoftwareEngineer'],
            'fitness': ['#FitnessMotivation', '#BodyTransformation', '#ActiveLife', '#Wellness'],
        }
    }
    
    CAPTION_TEMPLATES = {
        'youtube': ["🎬 {title}\n\n{description}\n\nSubscribe for more! 👇"],
        'instagram': ["✨ {title}\n\n{description}\n\nDouble tap if you agree! ❤️"]
    }
    
    BEST_HOURS = {'youtube': [14, 15, 16, 18, 19, 20], 'instagram': [7, 8, 11, 12, 17, 18, 19, 21]}
    
    def generate_caption(self, platform, title, description, niche='general'):
        templates = self.CAPTION_TEMPLATES.get(platform, self.CAPTION_TEMPLATES['instagram'])
        template = random.choice(templates)
        return template.format(title=title, description=description or title)
    
    def generate_hashtags(self, platform, niche='general', count=5):
        bank = self.HASHTAG_BANK.get(platform, {})
        tags = bank.get(niche, bank.get('general', []))
        return random.sample(tags, min(count, len(tags)))

def load_model():
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except:
        m = OnePulseModel()
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(m, f)
        return m

# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────
def main():
    st.title("🚀 OnePulse Content Updater")
    st.markdown("---")
    
    # Initialize database and model
    init_db()
    model = load_model()
    
    # Sidebar navigation
    menu = st.sidebar.radio("Navigation", ["Create Post", "View Posts", "Analytics", "AI Assistant"])
    
    if menu == "Create Post":
        st.header("📝 Create New Post")
        
        col1, col2 = st.columns(2)
        
        with col1:
            platform = st.selectbox("Platform", ["instagram", "youtube"])
            title = st.text_input("Title")
            description = st.text_area("Description")
            niche = st.selectbox("Niche", ["general", "tech", "fitness", "lifestyle", "food", "art"])
        
        with col2:
            image_url = st.text_input("Image URL (optional)")
            scheduled_date = st.date_input("Schedule Date", datetime.now())
            scheduled_time = st.time_input("Schedule Time", datetime.now().time())
            
            if st.button("✨ Generate AI Caption & Hashtags", use_container_width=True):
                with st.spinner("Generating..."):
                    caption = model.generate_caption(platform, title, description, niche)
                    hashtags = model.generate_hashtags(platform, niche)
                    st.session_state['generated_caption'] = caption
                    st.session_state['generated_hashtags'] = ' '.join(hashtags)
                    st.success("Generated!")
        
        caption = st.text_area("Caption", value=st.session_state.get('generated_caption', ''))
        hashtags = st.text_input("Hashtags", value=st.session_state.get('generated_hashtags', ''))
        
        if st.button("💾 Save Post", type="primary", use_container_width=True):
            if not title:
                st.error("Title is required")
            else:
                scheduled_datetime = datetime.combine(scheduled_date, scheduled_time)
                conn = get_db()
                conn.execute(
                    '''INSERT INTO posts (platform, title, description, hashtags, caption, image_url, niche, scheduled_time, status)
                       VALUES (?,?,?,?,?,?,?,?,'scheduled')''',
                    (platform, title, description, hashtags, caption, image_url, niche, scheduled_datetime.isoformat())
                )
                conn.commit()
                conn.close()
                st.success("✅ Post saved successfully!")
                st.balloons()
    
    elif menu == "View Posts":
        st.header("📋 All Posts")
        
        conn = get_db()
        posts = conn.execute("SELECT * FROM posts ORDER BY scheduled_time DESC").fetchall()
        conn.close()
        
        if not posts:
            st.info("No posts yet. Create your first post!")
        else:
            for post in posts:
                with st.expander(f"{post['title']} - {post['platform']} ({post['status']})"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Description:** {post['description']}")
                        st.write(f"**Caption:** {post['caption'][:100]}...")
                    with col2:
                        st.write(f"**Scheduled:** {post['scheduled_time']}")
                        st.write(f"**Hashtags:** {post['hashtags']}")
                        st.write(f"**Status:** {post['status']}")
    
    elif menu == "Analytics":
        st.header("📊 Analytics Dashboard")
        
        conn = get_db()
        posts = conn.execute("SELECT * FROM posts").fetchall()
        conn.close()
        
        if posts:
            df = pd.DataFrame([dict(p) for p in posts])
            status_counts = df['status'].value_counts()
            platform_counts = df['platform'].value_counts()
            
            col1, col2 = st.columns(2)
            with col1:
                fig1 = px.pie(values=status_counts.values, names=status_counts.index, title="Post Status")
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                fig2 = px.bar(x=platform_counts.index, y=platform_counts.values, title="Posts by Platform")
                st.plotly_chart(fig2, use_container_width=True)
            
            st.metric("Total Posts", len(df))
    
    else:  # AI Assistant
        st.header("🤖 AI Content Assistant")
        
        col1, col2 = st.columns(2)
        
        with col1:
            platform = st.selectbox("Platform", ["instagram", "youtube"], key="ai_platform")
            niche = st.selectbox("Niche", ["general", "tech", "fitness", "lifestyle", "food", "art"], key="ai_niche")
            topic = st.text_input("Topic/Title")
            description = st.text_area("Brief description")
        
        with col2:
            if st.button("🎨 Generate Content", use_container_width=True):
                with st.spinner("Creating content..."):
                    caption = model.generate_caption(platform, topic, description, niche)
                    hashtags = model.generate_hashtags(platform, niche)
                    
                    st.markdown("### ✨ Generated Content")
                    st.success(f"**Caption:**\n{caption}")
                    st.info(f"**Hashtags:**\n{' '.join(hashtags)}")
                    
                    # Generate schedule suggestions
                    st.markdown("### 📅 Suggested Schedule")
                    for hour in model.BEST_HOURS.get(platform, [12, 18]):
                        st.write(f"- {hour}:00 - Good engagement time")

if __name__ == "__main__":
    main()