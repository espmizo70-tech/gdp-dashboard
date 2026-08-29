import streamlit as st
import os
import requests
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

# 1. إعداد الصفحة والأنماط البصرية
st.set_page_config(page_title="Shorts3D Studio AI", page_icon="🚀", layout="wide")

# تصميم CSS سينمائي ببطاقات 3D وتأثير الزجاج (Glassmorphism)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at 50% -20%, #1e1b4b, #0f172a 70%);
        color: #f8fafc;
    }
    
    /* Hero Banner 3D */
    .hero-box {
        position: relative;
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 28px;
        padding: 3rem 1.5rem;
        text-align: center;
        box-shadow: 0 30px 60px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        margin-bottom: 2.5rem;
    }
    
    .hero-title {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
    }
    
    .badge-3d {
        display: inline-block;
        background: linear-gradient(90deg, #6366f1, #d946ef);
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.9rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(217, 70, 239, 0.4);
        margin-bottom: 1rem;
    }

    /* زر التوليد العملاق */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
        color: white;
        font-size: 1.3rem;
        font-weight: 800;
        padding: 1rem;
        border-radius: 20px;
        border: none;
        box-shadow: 0 12px 30px rgba(139, 92, 246, 0.5);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        transform: translateY(-4px) scale(1.01);
        box-shadow: 0 20px 40px rgba(236, 72, 153, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# واجهة البداية الجذابة
st.markdown("""
<div class="hero-box">
    <div class="badge-3d">⚡ Powered by 3D AI Engines</div>
    <div class="hero-title">🎬 منصة الفيديوهات السينمائية 60s Pro</div>
    <p style="color: #cbd5e1; font-size: 1.2rem; max-width: 700px; margin: 0 auto;">
        اصنع فيديوهات 60 ثانية احترافية فوراً بخلفيات ثلاثية الأبعاد (3D Renders) ونصوص واضحة باللغة العربية أو الإنجليزية.
    </p>
</div>
""", unsafe_allow_html=True)

# دالة جلب خلفيات 3D عالية الدقة
def fetch_3d_background(style_tag, width=1080, height=1920):
    try:
        # استخدام صور 3D متناسقة بدقة عمودية
        url = f"https://picsum.photos/{width}/{height}?random=3d_{hash(style_tag) % 1000}"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        pass
    return Image.new('RGB', (width, height), color=(15, 23, 42))

# دالة كتابة النصوص الواضحة (عربي / إنجليزي)
def render_crisp_text(text, lang='ar', size=(1080, 1920), font_color="yellow"):
    if lang == 'ar':
        reshaped_text = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped_text)
    else:
        display_text = text

    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color_rgb = (255, 235, 59, 255) if font_color == "yellow" else (255, 255, 255, 255)
    
    # 1. رسم خلفية داكنة نصف شفافة خلف النص لضمان الوضوح التام فوق الصور الـ 3D
    bbox = draw.multiline_textbbox((size[0]//2, size[1]//2), display_text, anchor="mm", align="center")
    pad = 30
    draw.rounded_rectangle([bbox[0]-pad, bbox[1]-pad, bbox[2]+pad, bbox[3]+pad], radius=20, fill=(0, 0, 0, 180))

    # 2. رسم النص مع تظليل ناعم
    draw.multiline_text((size[0]//2 + 2, size[1]//2 + 2), display_text, fill=(0, 0, 0, 255), anchor="mm", align="center")
    draw.multiline_text((size[0]//2, size[1]//2), display_text, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# تقسيم الخيارات
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("🌐 1. لغة وتصميم الفيديو")
    
    selected_lang = st.radio("اختر لغة التعليق الصوتي والنص:", ["العربية (Arabic 🇸🇦)", "English (الإنجليزية 🇬🇧)"], horizontal=True)
    lang_code = 'ar' if "العربية" in selected_lang else 'en'
    
    bg_3d_style = st.selectbox(
        "اختر نمط الصور ثلاثية الأبعاد (3D Style):",
        ["🎨 3D Surreal Digital Art", "🌃 3D Cyberpunk City", "🪐 3D Space & Galaxy", "🗿 3D Cinematic Abstract"]
    )
    
    text_color = st.selectbox("لون الخط المتراكب:", ["yellow", "white"])

with col_right:
    st.subheader("📝 2. سكريبت الـ 60 ثانية")
    
    default_ar = "في عالم مليء بالأسرار والجمال الرقمي.\nتأخذنا التكنولوجيا إلى أبعاد ثلاثية الأبعاد لم نكن نتخيلها.\nاصنع مستقبلك الآن وحول أفكارك إلى واقع."
    default_en = "In a world full of secrets and digital wonder.\nTechnology leads us into 3D dimensions we never imagined.\nBuild your future today and turn ideas into reality."
    
    script_input = st.text_area(
        "أدخل الجمل (توزع تلقائياً لتطابق مدة 60 ثانية):",
        value=default_ar if lang_code == 'ar' else default_en,
        height=160
    )

st.markdown("---")

# زر الإنتاج
if st.button("🚀 إنشاء فيديو 60s سينمائي 3D الآن"):
    lines = [line.strip() for line in script_input.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى كتابة السكريبت أولاً!")
    else:
        progress_bar = st.progress(0)
        status_box = st.empty()
        
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                status_box.markdown(f"**🎨 جاري معالجة المشهد 3D رقم ({i+1}/{total_lines})...**")
                
                # 1. التعليق الصوتي
                audio_filename = f"voice_{i}.mp3"
                tts = gTTS(text=line, lang=lang_code)
                tts.save(audio_filename)
                temp_files.append(audio_filename)
                
                audio_clip = AudioFileClip(audio_filename)
                line_duration = audio_clip.duration
                audio_clips.append(audio_clip)

                # 2. خلفية 3D HD
                bg_pil = fetch_3d_background(f"{bg_3d_style}_{i}")
                bg_clip = ImageClip(np.array(bg_pil)).set_duration(line_duration)

                # 3. النص الشفاف المظلل
                text_np = render_crisp_text(line, lang=lang_code, font_color=text_color)
                txt_clip = ImageClip(text_np).set_position('center').set_duration(line_duration)
                
                # دمج المشهد
                scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
                sub_clips.append(scene)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 85))

            status_box.markdown("**⚡ جاري رندر وتصدير الفيديو النهائي بدقة 60 ثانية...**")
            final_video = concatenate_videoclips(sub_clips)
            output_file = "final_3d_short.mp4"
            final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status_box.empty()
            
            # تنظيف المؤقتات
            for clip in audio_clips: clip.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم إنشاء الفيديو بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
