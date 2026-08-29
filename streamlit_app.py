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

# 1. إعداد الصفحة والأنماط التفاعلية
st.set_page_config(page_title="Studio Shorts AI Pro", page_icon="✨", layout="wide")

# تصميم الواجهة بـ Custom CSS (حركات غلاس، أنيميشن، درجات ألوان سينمائية)
st.markdown("""
<style>
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%); }
    .stApp { color: #f8fafc; }
    
    /* تصميم بطاقة البداية والرسوم المتحركة */
    .hero-container {
        text-align: center;
        padding: 2.5rem 1rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(16px);
        border-radius: 24px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 50px rgba(0,0,0,0.4);
        margin-bottom: 2rem;
        animation: fadeIn 1.2s ease-in-out;
    }
    
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    /* زر التوليد البارز */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899);
        color: white;
        font-weight: bold;
        font-size: 1.2rem;
        padding: 0.8rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 25px rgba(168, 85, 247, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(168, 85, 247, 0.6);
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# ترويسة الموقع التفاعلية
st.markdown("""
<div class="hero-container">
    <div class="hero-title">✨ منصة صناعة الفيديوهات الخارقة V7 Ultra</div>
    <p style="color: #94a3b8; font-size: 1.1rem;">اصنع فيديوهات قصيرة بنمط سينمائي احترافي، صور ذكاء اصطناعي، ونصوص متحركة متزامنة بدقة عالية.</p>
</div>
""", unsafe_allow_html=True)

# دالة توليد صورة خلفية ذكاء اصطناعي أو جلب صورة حسب النمط
def fetch_ai_background(prompt_keyword, width=1080, height=1920):
    try:
        url = f"https://picsum.photos/{width}/{height}?blur=2"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content))
    except:
        pass
    # صورة افتراضية في حال تعذر الاتصال
    return Image.new('RGB', (width, height), color=(15, 23, 42))

# دالة رسم النصوص المحسنة
def create_styled_text_image(text, size=(1080, 1920), font_color="yellow", has_shadow=True):
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color_rgb = (255, 230, 0, 255) if font_color == "yellow" else (255, 255, 255, 255)
    
    # إضافة تظليل أسود خلف النص لجعل القراءة سهلة فوق الصور
    if has_shadow:
        draw.multiline_text((size[0]//2 + 3, size[1]//2 + 3), bidi_text, fill=(0, 0, 0, 200), anchor="mm", align="center")
        
    draw.multiline_text((size[0]//2, size[1]//2), bidi_text, fill=color_rgb, anchor="mm", align="center")
    return np.array(img)

# تقسيم الشاشة إلى لوحة تحكم ومعاينة
col_settings, col_preview = st.columns([1.2, 1])

with col_settings:
    st.subheader("🎨 1. نمط الفيديو والخلفيات البصرية")
    
    bg_style = st.selectbox(
        "اختر الخلفية البصرية للمشاهد:",
        ["🌆 صور طبيعية وسينمائية داكنة", "🌌 فضاء وغموض (Dark Sci-Fi)", "🖤 لون كحلي سينمائي موحد"]
    )

    col_a, col_b = st.columns(2)
    with col_a:
        text_color_choice = st.selectbox("لون الكتابة المتحركة:", ["yellow", "white"])
    with col_b:
        aspect_ratio = st.selectbox("أبعاد الفيديو:", ["Shorts / TikTok (9:16)", "Instagram Post (4:5)"])

    st.subheader("📝 2. سكريبت القصة والكلمات")
    default_text = "في أعماق الغابة السحرية، كان هناك سر محبوس.\nرحلة تبحث عن الإجابات المنتظرة.\nاكتشف الحقيقة قبل فوات الأوان."
    user_script = st.text_area("أدخل جمل السكريبت (كل جملة في سطر منفصل):", value=default_text, height=140)

with col_preview:
    st.subheader("📱 معاينة شاشة الفيديو")
    st.info("💡 سيتولى المحرك مزامنة النص تلقائياً مع نطق الصوت وصور الخلفية السينمائية لكل مشهد.")

st.markdown("---")

# 3. محرك الإنتاج والرندر
if st.button("🚀 بدء صناعة الفيديو السينمائي الخرافي"):
    lines = [line.strip() for line in user_script.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى كتابة نص السكريبت أولاً!")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []

            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                status_text.text(f"🎬 جاري معالجة المشهد ({i+1}/{total_lines})...")
                
                # أ) الصوت
                audio_filename = f"temp_voice_{i}.mp3"
                tts = gTTS(text=line, lang='ar')
                tts.save(audio_filename)
                temp_files.append(audio_filename)
                
                audio_clip = AudioFileClip(audio_filename)
                line_duration = audio_clip.duration
                audio_clips.append(audio_clip)

                # ب) الخلفية البصرية
                if "صور" in bg_style or "فضاء" in bg_style:
                    bg_pil = fetch_ai_background(line, 1080, 1920)
                    bg_clip = ImageClip(np.array(bg_pil)).set_duration(line_duration)
                else:
                    bg_clip = ColorClip(size=(1080, 1920), color=(15, 23, 42), duration=line_duration)

                # ج) النص المتراكب والمزامنة
                text_np = create_styled_text_image(line, font_color=text_color_choice)
                txt_clip = ImageClip(text_np).set_position('center').set_duration(line_duration)
                
                scene_clip = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
                sub_clips.append(scene_clip)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 80))

            status_text.text("⚡ جاري تجميع كافة المشاهد ورندر الفيديو النهائي...")
            final_video = concatenate_videoclips(sub_clips)
            output_path = "final_ultra_short.mp4"
            final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status_text.text("✅ التكتمال بنجاح!")
            
            # تنظيف الملفات
            for clip in audio_clips:
                clip.close()
            for file_path in temp_files:
                if os.path.exists(file_path):
                    os.remove(file_path)

            st.balloons()
            st.success("🎉 تم إنشاء الفيديو بالكامل!")
            st.video(output_path)

        except Exception as e:
            st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")
