import streamlit as st
import os
import requests
import io
import textwrap
import numpy as np
from PIL import Image, ImageDraw
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="Studio Shorts 60s AI", page_icon="🎬", layout="wide")

# تصميم الواجهة الزجاجية التفاعلية
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% 0%, #0f172a 0%, #020617 100%);
        color: #f8fafc;
    }
    
    .hero-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 2.5rem 1rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #ec4899);
        color: white;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 1rem;
        border-radius: 18px;
        border: none;
        box-shadow: 0 10px 25px rgba(124, 58, 237, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(236, 72, 153, 0.6);
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-card">
    <div class="hero-title">🎬 استوديو القصص والفيديوهات السينمائية V10</div>
    <p style="color: #94a3b8; font-size: 1.15rem; margin-top: 8px;">
        صمّم قصصاً سينمائية مدتها 60 ثانية بكتابة فائقة الوضوح فوق الصور مباشرة وأصوات متعددة اللغات.
    </p>
</div>
""", unsafe_allow_html=True)

# دالة جلب الصور عالي الدقة
def fetch_story_image(width, height, scene_id):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={scene_id}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        pass
    return Image.new('RGB', (width, height), color=(15, 23, 42))

# دالة رسم النص فوق الصورة بشكل واضح جداً
def render_text_overlay(text, lang='ar', width=1080, height=1920, font_color="yellow"):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    wrap_limit = 28 if width < height else 50
    lines = textwrap.wrap(text, width=wrap_limit)
    wrapped_text = "\n".join(lines)
    
    if lang == 'ar':
        reshaped = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped)
    else:
        display_text = wrapped_text

    color_rgb = (255, 235, 59, 255) if font_color == "yellow" else (255, 255, 255, 255)
    cx, cy = width // 2, int(height * 0.75) # تراكب الكلمات في الأسفل السينمائي
    
    bbox = draw.multiline_textbbox((cx, cy), display_text, anchor="mm", align="center")
    padding = int(width * 0.035)
    
    # مربع داكن شفاف يحمي الكلام ويجعله واضحاً 100% فوق أي صورة
    draw.rounded_rectangle(
        [bbox[0]-padding, bbox[1]-padding, bbox[2]+padding, bbox[3]+padding],
        radius=20,
        fill=(0, 0, 0, 210),
        outline=(255, 255, 255, 70),
        width=2
    )

    # ظلال النص والكتلة الرئيسية
    draw.multiline_text((cx + 3, cy + 3), display_text, fill=(0, 0, 0, 255), anchor="mm", align="center")
    draw.multiline_text((cx, cy), display_text, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# تقسيم الواجهة إلى 3 أعمدة خيارات
col_platform, col_voice, col_story = st.columns([1, 1, 1.2])

with col_platform:
    st.subheader("📐 1. أبعاد المنصة")
    platform = st.selectbox(
        "اختر مقاس الفيديو والموقع:",
        [
            "🎵 TikTok / Shorts / Reels (9:16 - عمودي)",
            "🔴 YouTube Video (16:9 - أفقي)",
            "📸 Instagram Post (1:1 - مربع)",
            "📸 Instagram Story (4:5 - بورتريه)"
        ]
    )
    
    if "9:16" in platform: width, height = 1080, 1920
    elif "16:9" in platform: width, height = 1920, 1080
    elif "1:1" in platform: width, height = 1080, 1080
    else: width, height = 1080, 1350

    text_color = st.selectbox("لون كتابة النص:", ["yellow", "white"])

with col_voice:
    st.subheader("🎙️ 2. أصوات التعليق")
    voice_choice = st.selectbox(
        "اختر الصوت واللغة:",
        [
            "🇸🇦 العربية - لهجة سعودية / خليجية",
            "🇪🇬 العربية - لهجة مصرية",
            "🌐 العربية - الفصحى القياسية",
            "🇺🇸 English - US Male/Female (أمريكي)",
            "🇬🇧 English - UK British (بريطاني)",
            "🇨🇦 English - Canadian (كندي)"
        ]
    )
    
    # خريطة إصلاح الصوت الإنجليزي والعربي
    voice_config = {
        "🇸🇦 العربية - لهجة سعودية / خليجية": ('ar', 'com.sa'),
        "🇪🇬 العربية - لهجة مصرية": ('ar', 'com.eg'),
        "🌐 العربية - الفصحى القياسية": ('ar', 'com'),
        "🇺🇸 English - US Male/Female (أمريكي)": ('en', 'com'),
        "🇬🇧 English - UK British (بريطاني)": ('en', 'co.uk'),
        "🇨🇦 English - Canadian (كندي)": ('en', 'ca')
    }
    lang_code, tld_val = voice_config[voice_choice]

with col_story:
    st.subheader("📜 3. نماذج القصة (60 ثانية)")
    story_preset = st.selectbox(
        "اختر قصة جاهزة أو اكتب قصتك:",
        [
            "✍️ كتابة قصة خاصة",
            "🌌 قصة الرحلة إلى الفضاء والمستقبل (60 ثانية)",
            "⚔️ قصة السر المحبوس في الغابة (60 ثانية)",
            "🕵️ English Story: The Mysterious Kingdom (60s)"
        ]
    )
    
    presets_text = {
        "🌌 قصة الرحلة إلى الفضاء والمستقبل (60 ثانية)": "في عام 2050، فتحت البشرية أبواب المحيط الرقمي.\nسفن تنطلق نحو مجرات لم يطأها إنسان من قبل.\nأسرار كونية تنتظر من يفك شفرتها.\nرحلة لا عودة فيها نحو المستقبل.\nهل أنت مستعد لاكتشاف الحقيقة؟",
        "⚔️ قصة السر المحبوس في الغابة (60 ثانية)": "كانت الغابة تطوي سرها بين الأشجار الكثيفة.\nصوت غريب ينادي من بين الضباب.\nكل خطوة تقربنا من الكنز المفقود.\nرحلة مليئة بالغموض والإثارة.\nاكتشف السر قبل فوات الأوان.",
        "🕵️ English Story: The Mysterious Kingdom (60s)": "Deep within the ancient forest lies an unseen kingdom.\nLegends speak of a forgotten treasure hidden in time.\nEvery step brings us closer to the dark mystery.\nAre you brave enough to uncover the truth?"
    }

    if story_preset in presets_text:
        script_val = presets_text[story_preset]
    else:
        script_val = "أدخل الجمل هنا.\nكل جملة في سطر مستقل لتكوين مشاهد القصة الكاملة."

    user_script = st.text_area("نص السكريبت (كل جملة تصنع مشهداً وصوراً متزامنة):", value=script_val, height=140)

st.markdown("---")

# زر البدء والرندر
if st.button("🚀 إنشاء قصة الفيديو السينمائية (60s) الآن"):
    lines = [l.strip() for l in user_script.split("\n") if l.strip()]
    
    if not lines:
        st.error("يرجى كتابة نص السكريبت أولاً!")
    else:
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                status_box.markdown(f"**🎨 جاري تركيب المشهد والكلام على الصورة ({i+1}/{total_lines})...**")
                
                # 1. توليد الصوت باللغة المختارة
                audio_file = f"voice_v10_{i}.mp3"
                tts = gTTS(text=line, lang=lang_code, tld=tld_val)
                tts.save(audio_file)
                temp_files.append(audio_file)
                
                a_clip = AudioFileClip(audio_file)
                line_duration = a_clip.duration
                audio_clips.append(a_clip)

                # 2. جلب صورة المشهد عالي الوضوح
                bg_img = fetch_story_image(width, height, i+300)
                bg_clip = ImageClip(np.array(bg_img)).set_duration(line_duration)

                # 3. تراكب الكلام فوق الصورة مباشرة (Text-on-Image Layering)
                txt_np = render_text_overlay(line, lang=lang_code, width=width, height=height, font_color=text_color)
                txt_clip = ImageClip(txt_np).set_position('center').set_duration(line_duration)

                # دمج الصورة مع الكلام النازل فوقها والصوت
                scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(a_clip)
                sub_clips.append(scene)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 85))

            status_box.markdown("**⚡ جاري رندر وتصدير قصة الـ 60 ثانية بالكامل...**")
            final_video = concatenate_videoclips(sub_clips)
            output_file = "final_story_video.mp4"
            final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status_box.empty()
            
            # تنظيف الملفات المؤقتة
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم إنشاء الفيديو وقصة الـ 60 ثانية بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء التوليد: {str(e)}")
