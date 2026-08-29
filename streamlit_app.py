import streamlit as st
import os
import requests
import io
import textwrap
import numpy as np
from PIL import Image, ImageDraw
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Studio Shorts & Video AI Pro", page_icon="🎬", layout="wide")

# تصميم CSS سينمائي حديث زجاجي متجاوب
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 75%);
        color: #f8fafc;
    }
    
    .hero-box {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 24px;
        padding: 2.5rem 1.5rem;
        text-align: center;
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.6);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #db2777);
        color: white;
        font-size: 1.3rem;
        font-weight: bold;
        padding: 0.9rem;
        border-radius: 18px;
        border: none;
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.5);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(219, 39, 119, 0.6);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-box">
    <div class="hero-title">🚀 استوديو صناعة الفيديوهات الاحترافي V9</div>
    <p style="color: #cbd5e1; font-size: 1.15rem; margin-top: 8px;">
        صمّم مقاطع فيديو عالية الوضوح لـ TikTok, YouTube, Instagram بأصوات متعددة وتأطير تلقائي ممتاز.
    </p>
</div>
""", unsafe_allow_html=True)

# دالة جلب الصور عالية الوضوح
def fetch_hd_background(width, height, seed_id):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={seed_id}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        pass
    return Image.new('RGB', (width, height), color=(15, 23, 42))

# دالة كتابة النصوص الفائقة الوضوح مع المحاذاة التلقائية حسب المنصة
def render_ultra_crisp_text(text, lang='ar', width=1080, height=1920, font_color="yellow"):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # التفاف النص تلقائياً بناءً على عرض الشاشة
    wrap_width = 30 if width < height else 50
    lines = textwrap.wrap(text, width=wrap_width)
    wrapped_text = "\n".join(lines)
    
    if lang == 'ar':
        reshaped_text = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped_text)
    else:
        display_text = wrapped_text

    color_rgb = (255, 235, 59, 255) if font_color == "yellow" else (255, 255, 255, 255)
    center_x, center_y = width // 2, height // 2
    
    # حساب أبعاد النص لرسم صندوق خلفية متكيف
    bbox = draw.multiline_textbbox((center_x, center_y), display_text, anchor="mm", align="center")
    pad = int(width * 0.03)
    
    # 1. طبقة خلفية داكنة منحنية للوضوح التام
    draw.rounded_rectangle(
        [bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad],
        radius=16,
        fill=(0, 0, 0, 200)
    )

    # 2. حدود مضيئة متناسقة
    draw.rounded_rectangle(
        [bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad],
        radius=16,
        outline=(255, 255, 255, 60),
        width=2
    )

    # 3. النص الرئيسي مع الظل
    draw.multiline_text((center_x + 3, center_y + 3), display_text, fill=(0, 0, 0, 255), anchor="mm", align="center")
    draw.multiline_text((center_x, center_y), display_text, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# تقسيم واجهة الإعدادات
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ 1. منصة الفيديو والمقاسات")
    platform = st.selectbox(
        "اختر المنصة والنسق البصري:",
        [
            "📱 TikTok / Shorts / Reels (9:16 - عمودي)",
            "🎬 YouTube Landscape (16:9 - أفقي)",
            "📸 Instagram Post / Square (1:1 - مربع)",
            "🖼️ Instagram Feed (4:5 - بورتريه)"
        ]
    )
    
    # تحديد أبعاد الكانفاس
    if "9:16" in platform: width, height = 1080, 1920
    elif "16:9" in platform: width, height = 1920, 1080
    elif "1:1" in platform: width, height = 1080, 1080
    else: width, height = 1080, 1350

    target_duration = st.slider("⏱️ مدة الفيديو المستهدفة (ثانية):", min_value=20, max_value=60, value=30, step=5)
    text_color = st.selectbox("لون الخط:", ["yellow", "white"])

with col2:
    st.subheader("🎙️ 2. اختيار صوت التعليق")
    
    voice_option = st.selectbox(
        "اختر الصوت اللهجة/اللغة:",
        [
            "🇸🇦 عربي - لهجة خليجية / سعودية",
            "🇪🇬 عربي - لهجة مصري / فصحى",
            "🌐 عربي - فصحى قياسية",
            "🇺🇸 English - US Male/Female Accent",
            "🇬🇧 English - British Accent"
        ]
    )
    
    # خريطة إعدادات الصوت
    voice_map = {
        "🇸🇦 عربي - لهجة خليجية / سعودية": ('ar', 'com.sa'),
        "🇪🇬 عربي - لهجة مصري / فصحى": ('ar', 'com.eg'),
        "🌐 عربي - فصحى قياسية": ('ar', 'com'),
        "🇺🇸 English - US Male/Female Accent": ('en', 'com'),
        "🇬🇧 English - British Accent": ('en', 'co.uk')
    }
    lang_code, tld_val = voice_map[voice_option]

    st.subheader("📝 3. سكريبت الفيديو")
    default_script = "مرحباً بك في عالم صناعة المحتوى الذكي.\nيمكنك الآن تصدير فيديوهات احترافية بدقة عالية لكافة المنصات.\nاختر المقاس والأصوات المفضلة وابدأ بالنشر فوراً."
    script_text = st.text_area("أدخل السكريبت (كل جملة في سطر منفصل):", value=default_script, height=120)

st.markdown("---")

# زر البدء
if st.button("🚀 إنشاء الفيديو الاحترافي الآن"):
    lines = [line.strip() for line in script_text.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى كتابة السكريبت أولاً!")
    else:
        progress_bar = st.progress(0)
        status = st.empty()
        
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                status.markdown(f"**🎬 جاري بناء المشهد ({i+1}/{total_lines})...**")
                
                # توليد الصوت
                audio_file = f"voice_v9_{i}.mp3"
                tts = gTTS(text=line, lang=lang_code, tld=tld_val)
                tts.save(audio_file)
                temp_files.append(audio_file)
                
                a_clip = AudioFileClip(audio_file)
                line_dur = a_clip.duration
                audio_clips.append(a_clip)

                # الصورة المخصصة بالمقاس المطلوب
                bg_pil = fetch_hd_background(width, height, i+100)
                bg_clip = ImageClip(np.array(bg_pil)).set_duration(line_dur)

                # رسم النص الملاءم للمقاس
                txt_np = render_ultra_crisp_text(line, lang=lang_code, width=width, height=height, font_color=text_color)
                txt_clip = ImageClip(txt_np).set_position('center').set_duration(line_dur)

                # الدمج
                scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(a_clip)
                sub_clips.append(scene)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 85))

            status.markdown("**⚡ جاري رندر ومعالجة الأبعاد النهائية...**")
            final_video = concatenate_videoclips(sub_clips)
            output_file = "final_pro_video.mp4"
            final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status.empty()
            
            # تنظيف الملفات
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم إنشاء الفيديو بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
