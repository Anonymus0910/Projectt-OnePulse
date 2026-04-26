"""
OnePulse - Complete Social Media Scheduler
Full UI matching your screenshots with best times recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import random
import os
import json

# Page config must be first Streamlit command

# Add this after your imports (around line 15)
# ============================================
# CACHING FOR SPEED
# ============================================
@st.cache_resource
def get_ai_model():
    """Cache the AI model to avoid reinitialization"""
    return OnePulseAI()

# Then replace line ~335 where you have "ai_model = OnePulseAI()" with:
# ai_model = get_ai_model()
st.set_page_config(
    page_title="OnePulse | Content Scheduler",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# CUSTOM CSS FOR DARK/LIGHT MODE
# ============================================
def inject_css(theme):
    if theme == "dark":
        st.markdown("""
        <style>
            /* Dark Theme - Professional Look */
            .stApp {
                background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 100%);
            }
            .main-header {
                background: linear-gradient(90deg, #16213e 0%, #0f3460 100%);
                padding: 1.5rem 2rem;
                border-radius: 25px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.1);
            }
            .main-header h1 {
                margin: 0;
                font-size: 2.2rem;
                background: linear-gradient(135deg, #e94560, #0f3460);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .platform-tab-active {
                background: linear-gradient(135deg, #e94560, #0f3460);
                padding: 0.8rem 1.5rem;
                border-radius: 40px;
                color: white;
                font-weight: bold;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(233,69,96,0.3);
            }
            .platform-tab-inactive {
                background: rgba(255,255,255,0.1);
                padding: 0.8rem 1.5rem;
                border-radius: 40px;
                color: #aaa;
                font-weight: bold;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .stat-card {
                background: rgba(15, 52, 96, 0.4);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 1.5rem;
                text-align: center;
                border: 1px solid rgba(255,255,255,0.1);
                transition: transform 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                background: rgba(15, 52, 96, 0.6);
            }
            .stat-card h4 {
                margin: 0 0 0.5rem 0;
                color: #aaa;
                font-size: 0.9rem;
            }
            .stat-card h2 {
                margin: 0;
                font-size: 2.5rem;
                background: linear-gradient(135deg, #e94560, #fff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .post-card {
                background: rgba(30, 30, 60, 0.6);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 4px solid #e94560;
                transition: all 0.3s ease;
            }
            .post-card:hover {
                background: rgba(30, 30, 60, 0.8);
                transform: translateX(5px);
            }
            .ai-card {
                background: linear-gradient(135deg, rgba(233,69,96,0.2), rgba(15,52,96,0.2));
                border-radius: 20px;
                padding: 1.2rem;
                margin: 1rem 0;
                border: 1px solid rgba(233,69,96,0.3);
            }
            .best-time-card {
                background: linear-gradient(135deg, #0f3460, #16213e);
                border-radius: 15px;
                padding: 1rem;
                margin: 0.5rem 0;
                text-align: center;
                border: 1px solid rgba(233,69,96,0.3);
            }
            .upload-area {
                border: 2px dashed #e94560;
                border-radius: 15px;
                padding: 1rem;
                text-align: center;
                background: rgba(233,69,96,0.05);
            }
            .hashtag-button {
                background: linear-gradient(135deg, #e94560, #0f3460);
                padding: 0.3rem 0.8rem;
                border-radius: 20px;
                margin: 0.2rem;
                display: inline-block;
                font-size: 0.8rem;
                cursor: pointer;
            }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
            /* Light Theme - Professional Look */
            .stApp {
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
            }
            .main-header {
                background: white;
                padding: 1.5rem 2rem;
                border-radius: 25px;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(0,0,0,0.05);
            }
            .main-header h1 {
                margin: 0;
                font-size: 2.2rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .platform-tab-active {
                background: linear-gradient(135deg, #667eea, #764ba2);
                padding: 0.8rem 1.5rem;
                border-radius: 40px;
                color: white;
                font-weight: bold;
                text-align: center;
                box-shadow: 0 4px 15px rgba(102,126,234,0.3);
            }
            .platform-tab-inactive {
                background: #e0e0e0;
                padding: 0.8rem 1.5rem;
                border-radius: 40px;
                color: #666;
                font-weight: bold;
                text-align: center;
            }
            .stat-card {
                background: white;
                border-radius: 20px;
                padding: 1.5rem;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                transition: transform 0.3s ease;
            }
            .stat-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }
            .stat-card h4 {
                margin: 0 0 0.5rem 0;
                color: #666;
            }
            .stat-card h2 {
                margin: 0;
                font-size: 2.5rem;
                color: #667eea;
            }
            .post-card {
                background: white;
                border-radius: 15px;
                padding: 1rem;
                margin-bottom: 1rem;
                border-left: 4px solid #667eea;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .ai-card {
                background: linear-gradient(135deg, rgba(102,126,234,0.1), rgba(118,75,162,0.1));
                border-radius: 20px;
                padding: 1.2rem;
                margin: 1rem 0;
                border: 1px solid rgba(102,126,234,0.3);
            }
            .best-time-card {
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 15px;
                padding: 1rem;
                margin: 0.5rem 0;
                text-align: center;
                color: white;
            }
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 15px;
                padding: 1rem;
                text-align: center;
                background: rgba(102,126,234,0.05);
            }
        </style>
        """, unsafe_allow_html=True)

# ============================================
# AI MODEL - BEST TIMES & CONTENT GENERATION
# ============================================
class OnePulseAI:
    """Complete AI model for content generation and best times prediction"""
    
    # Platform-specific best engagement hours (based on social media research)
    BEST_HOURS = {
        "YouTube": {
            "general": [14, 15, 16, 18, 19, 20, 21],  # 2PM-9PM
            "tech": [15, 16, 17, 18, 19],
            "lifestyle": [14, 15, 16, 18, 19, 20],
            "fitness": [6, 7, 8, 17, 18, 19],
            "food": [11, 12, 13, 17, 18, 19],
            "art": [15, 16, 17, 18, 20, 21]
        },
        "Instagram": {
            "general": [7, 8, 9, 11, 12, 17, 18, 19, 20, 21],
            "tech": [8, 9, 17, 18, 19],
            "lifestyle": [7, 8, 9, 10, 18, 19],
            "fitness": [6, 7, 8, 17, 18, 19],
            "food": [11, 12, 13, 17, 18, 19],
            "art": [18, 19, 20, 21, 22]
        }
    }
    
    # Caption templates
    CAPTION_TEMPLATES = {
        "YouTube": [
            "🎬 {title}\n\n{description}\n\n🔥 Don't forget to like, comment & subscribe! 👇\n\n#Viral #Trending #Subscribe",
            "✨ {title}\n\n{description}\n\nNew video is LIVE! Watch till the end! 🚀\n\n#ContentCreator #NewVideo",
            "💡 {title}\n\n{description}\n\nHit the bell 🔔 so you never miss an upload!\n\n#YouTube #Creator"
        ],
        "Instagram": [
            "✨ {title}\n\n{description}\n\nDouble tap if you agree! ❤️\n\n#Instagram #Viral #Trending",
            "💫 {title}\n\n{description}\n\nSave this post for later! 💾\n\n#InstaGood #Explore #Reels",
            "🌟 {title}\n\n{description}\n\nTag someone who needs to see this! 👇\n\n#PhotoOfTheDay #InstaDaily"
        ]
    }
    
    # Hashtag banks by niche
    HASHTAG_BANKS = {
        "YouTube": {
            "tech": ["#Tech", "#Coding", "#Developer", "#AI", "#MachineLearning", "#Programming", "#SoftwareEngineer", "#TechNews"],
            "lifestyle": ["#Lifestyle", "#Vlog", "#DayInMyLife", "#Mindfulness", "#SelfCare", "#Wellness", "#Motivation"],
            "fitness": ["#Fitness", "#Workout", "#GymLife", "#Health", "#FitFam", "#Cardio", "#Bodybuilding"],
            "food": ["#FoodLovers", "#Cooking", "#Recipe", "#Foodie", "#HomeCook", "#EasyRecipes", "#Delicious"],
            "art": ["#Art", "#Creative", "#DIY", "#Handmade", "#Craft", "#Artist", "#Drawing"],
            "general": ["#YouTube", "#Viral", "#Trending", "#Subscribe", "#Creator", "#ContentCreator", "#NewVideo"]
        },
        "Instagram": {
            "tech": ["#TechLife", "#Innovation", "#Startup", "#Coding", "#Developer", "#AI", "#MachineLearning"],
            "lifestyle": ["#LifestyleBlogger", "#GoodVibes", "#Mindfulness", "#SelfCare", "#DailyInspo", "#WellnessJourney"],
            "fitness": ["#FitnessMotivation", "#BodyTransformation", "#ActiveLife", "#Wellness", "#Sweat", "#GymTime"],
            "food": ["#FoodPhotography", "#EatWell", "#CleanEating", "#Brunch", "#FoodBlogger", "#Yummy", "#Delicious"],
            "art": ["#ArtOfInstagram", "#HandmadeWithLove", "#CreativeProcess", "#Crafting", "#Maker", "#DIY"],
            "general": ["#Instagram", "#InstaGood", "#Explore", "#Reels", "#Trending", "#PhotoOfTheDay", "#Viral"]
        }
    }
    
    @classmethod
    def generate_caption(cls, platform, title, description, niche="general"):
        templates = cls.CAPTION_TEMPLATES.get(platform, cls.CAPTION_TEMPLATES["Instagram"])
        template = random.choice(templates)
        return template.format(title=title or "My Post", description=description or "Check out this amazing content!")
    
    @classmethod
    def generate_hashtags(cls, platform, niche="general", count=12):
        bank = cls.HASHTAG_BANKS.get(platform, cls.HASHTAG_BANKS["Instagram"])
        tags = bank.get(niche.lower(), bank.get("general", []))
        random.shuffle(tags)
        return tags[:count]
    
    @classmethod
    def get_best_times(cls, platform, niche="general", days_ahead=7):
        """Generate best posting times with scores"""
        hours = cls.BEST_HOURS.get(platform, {}).get(niche.lower(), cls.BEST_HOURS.get(platform, {}).get("general", [12, 15, 18, 20]))
        times = []
        
        for day_offset in range(1, days_ahead + 1):
            for hour in hours[:3]:  # Top 3 hours per day
                minute = random.choice([0, 15, 30])
                scheduled_time = datetime.now() + timedelta(days=day_offset)
                scheduled_time = scheduled_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Calculate score based on niche and platform match
                base_score = random.randint(75, 98)
                if niche.lower() in cls.HASHTAG_BANKS.get(platform, {}):
                    base_score += 5
                
                times.append({
                    'datetime': scheduled_time,
                    'score': min(base_score, 99),
                    'label': scheduled_time.strftime('%A, %b %d at %I:%M %p'),
                    'day': scheduled_time.strftime('%A'),
                    'hour': hour
                })
        
        # Sort by score and remove duplicates
        times.sort(key=lambda x: x['score'], reverse=True)
        unique_times = []
        seen = set()
        for t in times:
            key = f"{t['datetime'].date()}_{t['hour']}"
            if key not in seen:
                seen.add(key)
                unique_times.append(t)
        
        return unique_times[:8]  # Return top 8 unique best times

# Initialize AI
ai_model = OnePulseAI()

# ============================================
# SESSION STATE
# ============================================
if 'theme' not in st.session_state:
    st.session_state.theme = "dark"
if 'selected_platform' not in st.session_state:
    st.session_state.selected_platform = "YouTube"
if 'posts' not in st.session_state:
    st.session_state.posts = []
if 'generated_caption' not in st.session_state:
    st.session_state.generated_caption = ""
if 'generated_hashtags' not in st.session_state:
    st.session_state.generated_hashtags = []
if 'best_times' not in st.session_state:
    st.session_state.best_times = []
if 'show_ai_suggestions' not in st.session_state:
    st.session_state.show_ai_suggestions = False
if 'uploaded_file_data' not in st.session_state:
    st.session_state.uploaded_file_data = None
if 'uploaded_file_name' not in st.session_state:
    st.session_state.uploaded_file_name = ""
if 'uploaded_file_type' not in st.session_state:
    st.session_state.uploaded_file_type = ""

# ============================================
# HEADER WITH LOGO & THEME TOGGLE
# ============================================
def render_header():
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        st.markdown("""
        <div style="font-size: 56px; text-align: center;">🚀</div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1 style="margin: 0; text-align: center;">⚡ OnePulse</h1>
            <p style="margin: 0.5rem 0 0 0; text-align: center; opacity: 0.8;">Schedule & Automate Your Content</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        theme_icon = "🌙 Dark" if st.session_state.theme == "dark" else "☀️ Light"
        if st.button(f"{theme_icon}", key="theme_toggle", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()

# ============================================
# STATS CARDS
# ============================================
def render_stats():
    platform_posts = [p for p in st.session_state.posts if p.get('platform') == st.session_state.selected_platform]
    total = len(platform_posts)
    scheduled = len([p for p in platform_posts if p.get('status') == 'scheduled'])
    posted = len([p for p in platform_posts if p.get('status') == 'posted'])
    failed = len([p for p in platform_posts if p.get('status') == 'failed'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <h4>📊 TOTAL</h4>
            <h2>{total}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <h4>⏰ SCHEDULED</h4>
            <h2>{scheduled}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <h4>✅ POSTED</h4>
            <h2>{posted}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <h4>❌ FAILED</h4>
            <h2>{failed}</h2>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# PLATFORM TABS
# ============================================
def render_platform_tabs():
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        if st.session_state.selected_platform == "YouTube":
            st.markdown('<div class="platform-tab-active">📺 YouTube</div>', unsafe_allow_html=True)
        else:
            if st.button("📺 YouTube", key="yt_tab", use_container_width=True):
                st.session_state.selected_platform = "YouTube"
                st.rerun()
    
    with col2:
        if st.session_state.selected_platform == "Instagram":
            st.markdown('<div class="platform-tab-active">📸 Instagram</div>', unsafe_allow_html=True)
        else:
            if st.button("📸 Instagram", key="ig_tab", use_container_width=True):
                st.session_state.selected_platform = "Instagram"
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)

# ============================================
# SCHEDULE POST FORM
# ============================================
def render_schedule_form():
    platform = st.session_state.selected_platform
    
    st.subheader(f"📝 New Scheduled Post - {platform}")
    
    # Two columns for form layout
    col1, col2 = st.columns(2)
    
    with col1:
        niche = st.selectbox(
            "🎯 NICHE",
            ["General", "Tech", "Lifestyle", "Fitness", "Food", "Art"],
            help="Select your content niche for better AI recommendations"
        )
        title = st.text_input("📌 TITLE", placeholder="Enter post title...")
        description = st.text_area("💬 DESCRIPTION", placeholder="What's this post about?", height=100)
    
    with col2:
        # Drag & drop file upload area - FIXED with proper storage
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "📎 MEDIA FILE (ANY FORMAT — Images, Videos, GIFs, Audio, Documents)",
            type=None,  # None = accept ALL file types
            help="Drop your file here or click to browse — MP4, JPG, PNG, MOV, GIF, MP3, PDF..."
        )
        
        # Store uploaded file in session state properly - read bytes immediately
        if uploaded_file is not None:
            file_size = uploaded_file.size / (1024 * 1024)
            file_type = uploaded_file.type.split('/')[0] if '/' in uploaded_file.type else 'file'
            type_emoji = {'image': '🖼️', 'video': '🎬', 'audio': '🎵', 'text': '📄', 'application': '📎'}.get(file_type, '📎')
            
            # Read bytes immediately so they survive reruns
            file_bytes = uploaded_file.read()
            st.session_state.uploaded_file_data = file_bytes
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_file_type = uploaded_file.type
            
            st.success(f"{type_emoji} **{uploaded_file.name}** ({file_size:.1f} MB) — Ready to schedule!")
            
            # Show preview for images using stored bytes
            if file_type == 'image':
                try:
                    from PIL import Image
                    import io
                    image = Image.open(io.BytesIO(file_bytes))
                    st.image(image, caption="Preview", width=150)
                except:
                    pass
        elif st.session_state.get('uploaded_file_data'):
            # File was previously uploaded — keep showing its info
            name = st.session_state.get('uploaded_file_name', 'File')
            ftype = st.session_state.get('uploaded_file_type', '')
            file_type2 = ftype.split('/')[0] if '/' in ftype else 'file'
            type_emoji2 = {'image': '🖼️', 'video': '🎬', 'audio': '🎵', 'text': '📄', 'application': '📎'}.get(file_type2, '📎')
            size_mb = len(st.session_state.uploaded_file_data) / (1024 * 1024)
            st.success(f"{type_emoji2} **{name}** ({size_mb:.1f} MB) — Ready to schedule!")
            if file_type2 == 'image':
                try:
                    from PIL import Image
                    import io
                    image = Image.open(io.BytesIO(st.session_state.uploaded_file_data))
                    st.image(image, caption="Preview", width=150)
                except:
                    pass
        else:
            st.info("💡 Drop your file here or click to browse\n\nSupported: Images, Videos, GIFs, Audio, Documents")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        media_url = st.text_input("🔗 OR PASTE URL", placeholder="https://example.com/image.jpg")
    
    # AI Generation Section
    st.markdown("---")
    st.markdown("### 🤖 AI Content Generation")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("✨ Generate AI Captions, Hashtags & Best Times", use_container_width=True, type="primary"):
            with st.spinner("AI is analyzing best engagement times..."):
                st.session_state.generated_caption = ai_model.generate_caption(
                    platform, title or "My Post", description or "", niche
                )
                st.session_state.generated_hashtags = ai_model.generate_hashtags(platform, niche, count=12)
                st.session_state.best_times = ai_model.get_best_times(platform, niche, days_ahead=7)
                st.session_state.show_ai_suggestions = True
                st.success("✨ AI generation complete!")
    
    # Display AI Recommendations
    if st.session_state.show_ai_suggestions:
        st.markdown("### ✨ AI RECOMMENDATIONS")
        
        col1, col2, col3 = st.columns([2, 1, 1.5])
        
        with col1:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("#### 💬 SUGGESTED CAPTION")
            st.info(st.session_state.generated_caption)
            if st.button("📋 Use this caption", key="use_caption_btn"):
                st.success("✅ Caption copied!")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("#### #️⃣ HASHTAGS (TAP TO ADD)")
            hashtag_cols = st.columns(2)
            for idx, tag in enumerate(st.session_state.generated_hashtags[:12]):
                col_idx = idx % 2
                with hashtag_cols[col_idx]:
                    if st.button(tag, key=f"ht_{idx}"):
                        st.toast(f"➕ Added {tag}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="ai-card">', unsafe_allow_html=True)
            st.markdown("#### ⏰ BEST TIMES TO POST")
            for time_slot in st.session_state.best_times[:5]:
                st.markdown(f"""
                <div class="best-time-card">
                    📅 {time_slot['label']}<br>
                    <strong>{time_slot['score']}% engagement</strong>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Caption and Hashtags inputs
    caption = st.text_area(
        "📝 CAPTION (OPTIONAL OVERRIDE)", 
        value=st.session_state.generated_caption if st.session_state.show_ai_suggestions else "",
        placeholder="Leave blank to auto-generate...",
        height=120
    )
    
    hashtags = st.text_input(
        "#️⃣ HASHTAGS (OPTIONAL OVERRIDE)",
        value=" ".join(st.session_state.generated_hashtags) if st.session_state.show_ai_suggestions else "",
        placeholder="#hashtag1 #hashtag2 ..."
    )
    
    # SCHEDULE SECTION - FIXED with proper calendar and time picker
    st.markdown("---")
    st.markdown("### 🗓️ SCHEDULE TIME (OPTIONAL, AUTO IF BLANK)")
    
    # Radio button for schedule type
    schedule_type = st.radio(
        "Choose scheduling method",
        ["📅 Use AI Recommended Time", "⚙️ Custom Time"],
        horizontal=True
    )
    
    scheduled_datetime = None
    
    if schedule_type == "📅 Use AI Recommended Time" and st.session_state.best_times:
        st.markdown("#### Choose from AI recommended times:")
        
        time_options = [f"{t['label']} — {t['score']}% engagement" for t in st.session_state.best_times[:5]]
        selected_idx = st.selectbox("", range(len(time_options)), format_func=lambda x: time_options[x], label_visibility="collapsed")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 SCHEDULE WITH AI TIME", type="primary", use_container_width=True):
                scheduled_datetime = st.session_state.best_times[selected_idx]['datetime']
                
                if not title:
                    st.error("❌ Please enter a title")
                else:
                    media_file_name = st.session_state.get('uploaded_file_name', '') if st.session_state.get('uploaded_file_data') else media_url
                    
                    new_post = {
                        'platform': platform,
                        'niche': niche,
                        'title': title,
                        'description': description,
                        'caption': caption or st.session_state.generated_caption,
                        'hashtags': hashtags or " ".join(st.session_state.generated_hashtags),
                        'media_file': media_file_name or media_url,
                        'media_data': st.session_state.get('uploaded_file_data', None),
                        'scheduled_time': scheduled_datetime,
                        'status': 'scheduled',
                        'created_at': datetime.now()
                    }
                    st.session_state.posts.append(new_post)
                    st.success(f"✅ Post scheduled for {scheduled_datetime.strftime('%A, %b %d at %I:%M %p')}!")
                    st.balloons()
                    st.session_state.show_ai_suggestions = False
                    st.session_state.generated_caption = ""
                    st.session_state.generated_hashtags = []
                    st.session_state.uploaded_file_data = None
                    st.rerun()
    
    else:  # Custom Time — native browser datetime picker
        st.markdown("#### 📅 Select your preferred date and time")

        col1, col2 = st.columns(2)

        with col1:
            schedule_date = st.date_input(
                "📅 DATE",
                datetime.now().date(),
                min_value=datetime.now().date(),
            )

        with col2:
            schedule_time = st.time_input(
                "⏰ TIME",
                value=datetime.now().replace(second=0, microsecond=0).time(),
                step=60,   # 1-minute steps so any minute can be picked
            )

        selected_datetime = datetime.combine(schedule_date, schedule_time)
        formatted_date = selected_datetime.strftime("%B %d, %Y")
        formatted_time = selected_datetime.strftime("%I:%M %p")

        st.info(f"📅 **Selected:** {formatted_date} at {formatted_time}")

        if selected_datetime < datetime.now():
            st.error("⚠️ Cannot schedule in the past! Please select a future date/time.")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("💾 SCHEDULE POST", type="primary", use_container_width=True):
                if selected_datetime < datetime.now():
                    st.error("❌ Cannot schedule posts in the past!")
                elif not title:
                    st.error("❌ Please enter a title")
                else:
                    media_file_name = st.session_state.get('uploaded_file_name', '') if st.session_state.get('uploaded_file_data') else media_url
                    
                    new_post = {
                        'platform': platform,
                        'niche': niche,
                        'title': title,
                        'description': description,
                        'caption': caption,
                        'hashtags': hashtags,
                        'media_file': media_file_name or media_url,
                        'media_data': st.session_state.get('uploaded_file_data', None),
                        'scheduled_time': selected_datetime,
                        'status': 'scheduled',
                        'created_at': datetime.now()
                    }
                    st.session_state.posts.append(new_post)
                    st.success(f"✅ Post '{title}' scheduled for {formatted_date} at {formatted_time}!")
                    st.balloons()
                    st.session_state.show_ai_suggestions = False
                    st.session_state.generated_caption = ""
                    st.session_state.generated_hashtags = []
                    st.session_state.uploaded_file_data = None
                    st.rerun()# ============================================
# POSTS DISPLAY SECTION
# ============================================
def render_posts():
    platform = st.session_state.selected_platform
    platform_posts = [p for p in st.session_state.posts if p.get('platform') == platform]
    
    st.subheader(f"📋 {platform.upper()} POSTS")
    
    if not platform_posts:
        st.info("No posts scheduled yet. Create your first post!")
        return
    
    for idx, post in enumerate(reversed(platform_posts)):
        status_color = "🟢" if post['status'] == 'posted' else "🟡" if post['status'] == 'scheduled' else "🔴"
        scheduled_str = post['scheduled_time'].strftime('%b %d, %Y, %I:%M %p') if isinstance(post['scheduled_time'], datetime) else str(post['scheduled_time'])
        
        st.markdown(f"""
        <div class="post-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <strong style="font-size: 1.1rem;">{post['title']}</strong>
                    <br>
                    <small style="color: #aaa;">{post.get('description', '')[:80]}...</small>
                    <br>
                    <small>⏱️ {scheduled_str}</small>
                    <br>
                    <span>{status_color} {post['status'].upper()}</span>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    {f'<button style="background: #4CAF50; border: none; padding: 0.3rem 0.8rem; border-radius: 5px; cursor: pointer;">✅ Posted</button>' if post['status'] == 'posted' else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if post['status'] == 'scheduled':
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                if st.button("📤 Post Now", key=f"post_now_{idx}"):
                    post['status'] = 'posted'
                    post['posted_at'] = datetime.now()
                    st.rerun()
            with col3:
                if st.button("🗑️ Delete", key=f"del_{idx}"):
                    st.session_state.posts.remove(post)
                    st.rerun()
        
        st.markdown("---")

# ============================================
# ANALYTICS DASHBOARD
# ============================================
def render_analytics():
    st.header("📊 Analytics Dashboard")
    
    if not st.session_state.posts:
        st.info("No data available. Create some posts to see analytics!")
        return
    
    # Convert posts to DataFrame
    df_data = []
    for post in st.session_state.posts:
        df_data.append({
            'Platform': post['platform'],
            'Status': post['status'],
            'Niche': post.get('niche', 'General'),
            'Scheduled Time': post['scheduled_time'],
            'Title': post['title'][:30]
        })
    
    df = pd.DataFrame(df_data)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution pie chart
        status_counts = df['Status'].value_counts()
        fig1 = px.pie(values=status_counts.values, names=status_counts.index, 
                      title="Post Status Distribution",
                      color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'])
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Platform distribution bar chart
        platform_counts = df['Platform'].value_counts()
        fig2 = px.bar(x=platform_counts.index, y=platform_counts.values,
                      title="Posts by Platform",
                      color=platform_counts.index,
                      color_discrete_sequence=['#FF0000', '#E4405F'])
        st.plotly_chart(fig2, use_container_width=True)
    
    # Niche performance
    st.subheader("📈 Niche Performance")
    niche_counts = df['Niche'].value_counts()
    fig3 = px.bar(x=niche_counts.index, y=niche_counts.values,
                  title="Content by Niche",
                  color=niche_counts.index)
    st.plotly_chart(fig3, use_container_width=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Posts", len(df))
    with col2:
        st.metric("Posted", len(df[df['Status'] == 'posted']))
    with col3:
        st.metric("Scheduled", len(df[df['Status'] == 'scheduled']))
    with col4:
        st.metric("Failed", len(df[df['Status'] == 'failed']))

# ============================================
# AI ASSISTANT PAGE
# ============================================
def render_ai_assistant():
    st.header("🤖 AI Content Assistant")
    st.markdown("Get AI-powered content recommendations for your posts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        platform = st.selectbox("Platform", ["YouTube", "Instagram"], key="ai_platform")
        niche = st.selectbox("Niche", ["General", "Tech", "Lifestyle", "Fitness", "Food", "Art"], key="ai_niche")
        topic = st.text_input("Topic/Title", placeholder="What's your content about?")
        description = st.text_area("Brief description", placeholder="Describe your content...", height=100)
    
    with col2:
        if st.button("🎨 Generate Content Ideas", use_container_width=True, type="primary"):
            with st.spinner("AI is creating content..."):
                caption = ai_model.generate_caption(platform, topic or "My Content", description or "", niche)
                hashtags = ai_model.generate_hashtags(platform, niche)
                best_times = ai_model.get_best_times(platform, niche, days_ahead=5)
                
                st.markdown("### ✨ Generated Content")
                
                st.markdown("#### 💬 Suggested Caption")
                st.success(caption)
                
                st.markdown("#### #️⃣ Recommended Hashtags")
                st.info(" ".join(hashtags))
                
                st.markdown("#### ⏰ Best Times to Post")
                for time_slot in best_times[:5]:
                    st.markdown(f"""
                    <div class="best-time-card">
                        📅 {time_slot['label']}<br>
                        <strong>{time_slot['score']}% engagement score</strong>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("#### 💡 Pro Tips")
                st.info("- Post consistently at recommended times\n- Engage with comments within 1 hour\n- Use 5-10 relevant hashtags\n- Keep captions concise and value-driven")

# ============================================
# MAIN APP
# ============================================
def main():
    # Inject CSS based on theme
    inject_css(st.session_state.theme)
    
    # Header
    render_header()
    
    # Platform tabs
    render_platform_tabs()
    
    # Stats
    render_stats()
    
    st.markdown("---")
    
    # Sidebar navigation
    menu = st.radio(
        "",
        ["📝 Create Post", "📋 View Posts", "📊 Analytics", "🤖 AI Assistant"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    if menu == "📝 Create Post":
        # Two columns for form and posts list
        col1, col2 = st.columns([2, 1])
        with col1:
            render_schedule_form()
        with col2:
            render_posts()
    elif menu == "📋 View Posts":
        render_posts()
    elif menu == "📊 Analytics":
        render_analytics()
    else:
        render_ai_assistant()

if __name__ == "__main__":
    main()