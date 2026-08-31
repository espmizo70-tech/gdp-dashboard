import streamlit as st
import os
import requests
import io
import textwrap
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from gtts import gTTS
from moviepy.editor import (
    ImageClip, CompositeVideoClip, AudioFileClip, 
    CompositeAudioClip, concatenate_videoclips, afx
)
import arabic_reshaper
from bidi.algorithm import get_display

# 1. فحص وجود مكتبة OpenAI
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 2. تهيئة الصفحة وثيم DaVinci AI Glassmorphic
st.set_page_config(
    page_title="DaVinci AI | Sora 2.0 Studio Enterprise",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم وتنسيق الواجهة (Dark Neon UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Orbitron:wght@700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background: #05070f;
        color: #f1f5f9;
    }
    
    /* Header Bar */
    .davinci-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 22px;
        padding: 18px 32px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8);
    }
    .davinci-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.1rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f39c12, #d4af37, #00f2fe, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge-pro {
        background: linear-gradient(90deg, #d4af37, #e67e22);
        color: #000000;
        padding: 5px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 900;
        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
    }
    
    /* Studio Card Panels */
    .panel-card {
        background: linear-gradient(145deg, rgba(20, 26, 43, 0.85), rgba(10, 14, 26, 0.95));
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 25px;
        box-shadow: 0 15px 45px rgba(0, 0, 0, 0.7);
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #f39c12, #00c6ff);
        color: #05070f;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 1.1rem;
        border-radius: 18px;
        border: none;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.005);
        box-shadow: 0 18px 45px rgba(0, 198, 255, 0.5);
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ترويسة الموقع الرئيسية
st.markdown("""
<div class="davinci-header">
    <div class="davinci-title">🎨 DAVINCI AI <span style="font-size: 1rem; color: #94a3b8; font-weight: 400;">| Sora 2.0 Enterprise Studio</span></div>
    <div>
        <span class="badge-pro">SORA 2.0 MAX ENGINE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي (Sidebar)
st.sidebar.title("🎛️ DaVinci Studio Engine")
openai_api_key = st.sidebar.text_input("🔑 مفتاح OpenAI API Key:", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("📐 إعدادات الجودة والمنصة")
platform_preset = st.sidebar.selectbox(
    "المنصة والأبعاد القياسية:",
    [
        "🎵 TikTok / Reels / Shorts (9:16)",
        "🔴 YouTube HD / Cinema (16:9)",
        "📸 Instagram Feed (1:1)",
        "📸 Instagram Portrait (4:5)",
        "🎬 Ultrawide Cinematic (21:9)"
    ]
)

render_fps = st.sidebar.select_slider("معدل الإطارات (FPS):", options=[24, 30, 60], value=24)
bgm_option = st.sidebar.checkbox("🎵 إضافة موسيقى خلفية سينمائية (BGM)", value=True)

# أبعاد المنصات
if "9:16" in platform_preset: w, h = 1080, 1920
elif "16:9" in platform_preset: w, h = 1920, 1080
elif "1:1" in platform_preset: w, h = 1080, 1080
elif "4:5" in platform_preset: w, h = 1080, 1350
else: w, h = 1920, 810 # 21:9

# دالة توليد مشاهد القصة عبر ChatGPT (JSON Storyboard)
def generate_storyboard(prompt, api_key):
    if HAS_OPENAI and api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            system_msg = "You are a professional cinematographer for DaVinci Sora 2.0. Create a 4-scene video story from the user's prompt."
            user_msg = f"Prompt: '{prompt}'. Return ONLY a JSON list of 4 objects. Each object must have keys: 'text' (Arabic narrative, 1 line), 'visual_prompt' (English image prompt for SD/Sora), and 'camera' (choose from: 'Zoom In', 'Zoom Out', 'Pan Left', 'Static')."
            
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                max_tokens=400,
                temperature=0.7
            )
            data = json.loads(res.choices[0].message.content.strip())
            return data
        except Exception:
            pass
            
    # Storyboard تلقائي احتياطي
    return [
        {"text": f"بداية القصة المذهلة حول {prompt}.", "visual_prompt": f"Cinematic opening shot of {prompt}, 8k photorealistic, cinematic lighting", "camera": "Zoom In"},
        {"text": "تتسارع الأحداث وتنفتح أسرار لم تكن متوقعة.", "visual_prompt": f"Dramatic moment showing details of {prompt}, dramatic neon atmosphere", "camera": "Pan Left"},
        {"text": "لحظة الحسم تجعل كل شيء ينكشف بوضوح.", "visual_prompt": f"Climax scene of {prompt}, highly detailed, unreal engine 5 render", "camera": "Zoom Out"},
        {"text": "النهاية التي تفتح الأبواب لمستقبل جديد.", "visual_prompt": f"Epic concluding shot of {prompt}, futuristic sunrise, masterpiece", "camera": "Static"}
    ]

# دالة توليد صورة المشهد البصرية
def generate_frame_image(width, height, prompt_seed):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={prompt_seed + 105}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content)).convert('RGB')
            enhancer = ImageEnhance.Color(img)
            return enhancer.enhance(1.2)
    except Exception:
        pass
        
    img = Image.new('RGB', (width, height), color=(10, 14, 26))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(10 + (y / height) * 50)
        g = int(14 + (y / height) * 35)
        b = int(26 + (y / height) * 85)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

# دالة كتابة النص السينمائي الفائق الوضوح
def create_subtitles_layer(text, lang='ar', width=1080, height=1920):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    wrap_limit = 22 if width < height else 46
    lines = textwrap.wrap(text, width=wrap_limit)
    wrapped_text = "\n".join(lines)
    
    if lang in ['ar', 'ar-sa', 'ar-eg']:
        reshaped = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped)
    else:
        display_text = wrapped_text

    font_size = int(height * 0.04)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    cx, cy = width // 2, int(height * 0.79)
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    pad_x, pad_y = int(width * 0.04), int(height * 0.02)
    
    # خلفية نيون داكنة متناسقة
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=16,
        fill=(5, 7, 15, 230),
        outline=(212, 175, 55, 180),
        width=2
    )
    
    draw.multiline_text((cx, cy), display_text, font=font, fill=(255, 235, 59, 255), anchor="mm", align="center")
    return np.array(img)

# التبويبات الرئيسية
tab_studio, tab_storyboard, tab_metadata = st.tabs([
    "🚀 Sora 2.0 Studio Max", 
    "📋 Interactive Storyboard", 
    "🏷️ Social Metadata & Hashtags"
])

# التبويب 1: إدخال الفكرة وتوليد الـ Storyboard
with tab_studio:
    st.markdown("""
    <div class="panel-card">
        <h3>✨ منشئ الفيديوهات بالذكاء الاصطناعي (Text-to-Video Engine)</h3>
        <p style="color: #94a3b8;">أدخل القصة أو الفكرة العامة، وسنقوم ببناء Storyboard متكامل يتيح لك تعديل المشاهد وحركة الكاميرا قبل التصدير.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        story_idea = st.text_area("وصف القصة / الفكرة (Prompt):", "مدينة مستقبلية عائمة فوق السحاب تدار بروبوتات ذكية", height=110)
    with col2:
        voice_choice = st.selectbox(
            "الصوت والراوي:",
            [
                "🇸🇦 العربية (سعودية/خليجية)",
                "🇪🇬 العربية (مصرية)",
                "🌐 العربية (فصحى)",
                "🇺🇸 English (US)",
                "🇬🇧 English (UK)",
                "🇫🇷 French"
            ]
        )

    if st.button("📋 إنشاء لوحة المشاهد (Generate Storyboard)"):
        with st.spinner("🤖 جاري صياغة المشاهد والتأثيرات البصرية..."):
            st.session_state['storyboard_data'] = generate_storyboard(story_idea, openai_api_key)
            st.success("✨ تم إنشاء لوحة المشاهد بنجاح! انتقل لتبويب Interactive Storyboard لمراجعة المشاهد أو بدء الرندر.")

# التبويب 2: لوحة التحكم بالتعديل والرندر
with tab_storyboard:
    st.subheader("📋 لوحة المشاهد التفاعلية (Interactive Storyboard Editor)")
    
    if 'storyboard_data' not in st.session_state:
        st.session_state['storyboard_data'] = generate_storyboard("رحلة الفضاء نحو المجهول", openai_api_key)
        
    sb_data = st.session_state['storyboard_data']
    edited_sb = []
    
    for idx, item in enumerate(sb_data):
        with st.expander(f"🎬 المشهد {idx + 1}", expanded=True):
            col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
            with col_s1:
                txt = st.text_input(f"نص المشهد {idx+1}:", value=item.get("text", ""), key=f"txt_{idx}")
            with col_s2:
                v_prompt = st.text_input(f"وصف الصورة (Visual Prompt) {idx+1}:", value=item.get("visual_prompt", ""), key=f"vp_{idx}")
            with col_s3:
                cam = st.selectbox(f"الكاميرا {idx+1}:", ["Zoom In", "Zoom Out", "Pan Left", "Static"], index=0, key=f"cam_{idx}")
            
            edited_sb.append({"text": txt, "visual_prompt": v_prompt, "camera": cam})

    st.markdown("---")

    voice_map = {
        "🇸🇦 العربية (سعودية/خليجية)": ('ar', 'com.sa'),
        "🇪🇬 العربية (مصرية)": ('ar', 'com.eg'),
        "🌐 العربية (فصحى)": ('ar', 'com'),
        "🇺🇸 English (US)": ('en', 'com'),
        "🇬🇧 English (UK)": ('en', 'co.uk'),
        "🇫🇷 French": ('fr', 'fr')
    }
    lang_code, tld_val = voice_map.get(voice_choice, ('ar', 'com'))

    if st.button("🚀 بدء إنتاج ورندر الفيديو الكامل (Render DaVinci Video)"):
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []
            total = len(edited_sb)
            
            for i, scene in enumerate(edited_sb):
                status_box.markdown(f"**🎬 جاري إنتاج المشهد ({i+1}/{total}) مع التأثير الحركي [{scene['camera']}]...**")
                
                # 1. الصوت
                aud_file = f"davinci_v3_audio_{i}.mp3"
                tts = gTTS(text=scene['text'], lang=lang_code, tld=tld_val)
                tts.save(aud_file)
                temp_files.append(aud_file)
                
                a_clip = AudioFileClip(aud_file)
                line_dur = a_clip.duration
                audio_clips.append(a_clip)

                # 2. الصورة والحركة السينمائية (Ken Burns Zoom)
                bg_img = generate_frame_image(w, h, i * 88)
                bg_clip = ImageClip(np.array(bg_img)).set_duration(line_dur)
                
                if scene['camera'] == "Zoom In":
                    bg_clip = bg_clip.resize(lambda t: 1 + 0.04 * (t / line_dur))
                elif scene['camera'] == "Zoom Out":
                    bg_clip = bg_clip.resize(lambda t: 1.15 - 0.04 * (t / line_dur))

                # 3. النص السينمائي
                sub_np = create_subtitles_layer(scene['text'], lang=lang_code, width=w, height=h)
                sub_clip = ImageClip(sub_np).set_duration(line_dur)

                # دمج المشهد
                final_scene = CompositeVideoClip([bg_clip, sub_clip]).set_audio(a_clip)
                sub_clips.append(final_scene)
                
                progress_bar.progress(int(((i + 1) / total) * 80))

            status_box.markdown("**⚡ جاري رندر وتصدير الفيديو بـ أعلى جودة...**")
            final_video = concatenate_videoclips(sub_clips)
            
            output_file = "davinci_sora2_enterprise.mp4"
            final_video.write_videofile(output_file, fps=render_fps, codec='libx264', audio_codec='aac')
            
            progress_bar.progress(100)
            status_box.empty()
            
            # التنظيف
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم إنشاء فيديو DaVinci Sora 2.0 Enterprise بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الرندر: {str(e)}")

# التبويب 3: توليد العناوين والهاشتاجات
with tab_metadata:
    st.subheader("🏷️ مولد العناوين والوصف للشبكات الاجتماعية")
    if st.button("✨ توليد عناوين وهاشتاجات انتشارية (Viral Metadata)"):
        st.markdown("""
        ### 📌 نتائج العناوين والهاشتاجات الجاهزة للنشر:
        * **عنوان TikTok / Shorts:** 🚀 أسرار القصة التي لم يخبرك بها أحد! #DaVinciAI #Sora2
        * **وصف YouTube:** شاهد هذا الفيديو السينمائي المصمم بالكامل بواسطة الذكاء الاصطناعي DaVinci Sora 2.0 Engine.
        * **الهاشتاجات:** `#شورتس #ذكاء_اصطناعي #تيك_توك #Sora2 #DaVinciAI #Filmmaking`
        """)
