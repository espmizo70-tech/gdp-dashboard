import streamlit as st
import os
import requests
import io
import textwrap
import asyncio
import urllib.parse
import numpy as np
import csv
from datetime import datetime

# 🛠️ حل مشكلة Pillow/ANTIALIAS لضمان أقصى استقرار
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="Lumina AI Studio | Masterpiece Edition",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم SaaS زجاجي مع أيقونات شبكات التواصل
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Orbitron:wght@700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background: #030712;
        color: #f9fafb;
    }
    
    /* Top Bar */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(17, 24, 39, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.3);
        border-radius: 20px;
        padding: 18px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
    }
    
    .app-brand {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f59e0b, #d4af37, #06b6d4, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Platform Logos SVG */
    .platform-card {
        background: rgba(31, 41, 55, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        margin-bottom: 15px;
        transition: all 0.3s ease;
    }
    .platform-card:hover {
        border-color: #d4af37;
        transform: translateY(-3px);
    }

    /* Auth Box */
    .auth-card {
        max-width: 550px;
        margin: 40px auto;
        background: rgba(17, 24, 39, 0.9);
        border: 2px solid rgba(212, 175, 55, 0.4);
        border-radius: 24px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 20px 50px rgba(0,0,0,0.9);
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #f59e0b, #06b6d4);
        color: #000000;
        font-size: 1.2rem;
        font-weight: 900;
        padding: 0.85rem;
        border-radius: 14px;
        border: none;
        box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);
    }
    .stButton>button:hover {
        color: #ffffff;
        box-shadow: 0 12px 35px rgba(6, 182, 212, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# قاعدة بيانات زوار الموقع
LEADS_FILE = "registered_leads.csv"
def save_lead(name, email):
    file_exists = os.path.isfile(LEADS_FILE)
    with open(LEADS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Email"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email])

if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# بوابة تسجيل دخول الزوار
if not st.session_state["user_email"]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
        <h1 style="color: #fff; margin-bottom: 10px;">⚡ استوديو LUMINA AI الاحترافي</h1>
        <p style="color: #9ca3af; font-size: 1.05rem; margin-bottom: 20px;">
            أنشئ فيديوهات سينمائية عالية الجودة بأصوات بشرية وصور فائقة الدقة مخصصة لجميع شبكات التواصل الاجتماعي.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        input_name = st.text_input("👤 الاسم الكامل / Name:", placeholder="أحمد علي")
        input_email = st.text_input("📧 البريد الإلكتروني / Gmail:", placeholder="example@gmail.com")
        
        if st.button("🔓 دخول وتجربة الاستوديو مجاناً"):
            if not input_email.strip() or "@" not in input_email or "." not in input_email:
                st.error("⚠️ يرجى أدخال بريد إلكتروني صحيح للدخول!")
            else:
                save_lead(input_name, input_email)
                st.session_state["user_email"] = input_email
                st.session_state["user_name"] = input_name if input_name else "زائر"
                st.rerun()
    st.stop()

# الهيدر العلوي
st.markdown(f"""
<div class="app-header">
    <div class="app-brand">⚡ LUMINA AI <span style="font-size: 0.9rem; color: #9ca3af;">V7.0 ULTRA</span></div>
    <div>
        <span style="background: rgba(212,175,55,0.2); border: 1px solid #d4af37; color: #f59e0b; padding: 6px 16px; border-radius: 50px; font-weight: 700;">
            👤 {st.session_state['user_name']} ({st.session_state['user_email']})
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.sidebar.button("🚪 تسجيل الخروج"):
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")
openai_key = st.sidebar.text_input("🔑 مفتاح OpenAI (اختياري):", type="password")

ARABIC_VOICES = {
    "👨‍💼 رجل سعودي - وثائقي فخم": "ar-SA-HamedNeural",
    "👩‍💼 امرأة سعودية - ناعم واحترافي": "ar-SA-ZariyahNeural",
    "🎙️ رجل مصري - إخباري وغموض": "ar-EG-ShakirNeural",
    "👩 امرأة مصرية - إعلاني وتفاعلي": "ar-EG-SalmaNeural",
    "🇦🇪 رجل إماراتي - سينمائي هادئ": "ar-AE-HamdanNeural",
    "👧 فتاة شابة (شامي) - حكايات وأنيميشن": "ar-SY-AmanyNeural",
    "👦 شاب كويتي - حماسي وسريع": "ar-KW-FahedNeural",
    "🇺🇸 Christopher - English Cinematic": "en-US-ChristopherNeural"
}

# ---------------------------------------------------------
# دالة معالجة الصور والتأكد من عدم وجود شاشة سوداء
# ---------------------------------------------------------
def fetch_solid_ai_image(prompt_text, width, height, seed_num):
    clean_p = urllib.parse.quote(f"cinematic scene, photorealistic 8k, detailed, {prompt_text}")
    url = f"https://image.pollinations.ai/prompt/{clean_p}?width={width}&height={height}&seed={seed_num}&nologo=true"
    
    try:
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content)).convert('RGB')
            return img
    except Exception:
        pass
        
    # صورة احتياطية دافئة ملونة في حال انقطاع الإنترنيت (تمنع الشاشة السوداء)
    base = Image.new('RGB', (width, height), color=(15, 23, 42))
    draw = ImageDraw.Draw(base)
    draw.rectangle([0, 0, width, height], fill=(20, 30, 50))
    return base

# دالة طباعة الكتابة العربية بدقة عالية
def create_subtitle_frame(text, width, height):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    lines = textwrap.wrap(text, width=22 if width < height else 45)
    wrapped = "\n".join(lines)
    
    reshaped = arabic_reshaper.reshape(wrapped)
    display_text = get_display(reshaped)

    font_size = int(height * 0.04)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    cx, cy = width // 2, int(height * 0.78)
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    
    # خلفية زجاجية مع توهج ذهبي حول النص
    pad_x, pad_y = int(width * 0.04), int(height * 0.02)
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=16,
        fill=(10, 15, 28, 220),
        outline=(212, 175, 55, 255),
        width=3
    )
    
    draw.multiline_text((cx, cy), display_text, font=font, fill=(255, 255, 255, 255), anchor="mm", align="center")
    return np.array(img)

# ---------------------------------------------------------
# الواجهة الرئيسية بالتبويبات ومعرض المعاينة
# ---------------------------------------------------------
tab_studio, tab_gallery, tab_images, tab_audio = st.tabs([
    "🎬 استوديو إنتاج الفيديوهات", 
    "📺 معرض الفيديوهات الإشهارية", 
    "🎨 توليد الصور AI", 
    "🎙️ تحويل النص لصوت"
])

# 1. قسم صانع الفيديوهات
with tab_studio:
    st.subheader("🎯 اختر مقاس الشاشة والمنصة المطلوبة:")
    
    # خيارات المقاسات مع أيقونات الشبكات والإنيميشن
    col_p1, col_p2, col_p3 = st.columns(3)
    
    with col_p1:
        st.markdown("""
        <div class="platform-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#00f2fe"><path d="M19.589 6.686a4.793 4.793 0 0 1-3.77-4.245V2h-3.445v13.672a2.896 2.896 0 0 1-5.201 1.743l-.002-.001.002.001a2.895 2.895 0 0 1 3.183-4.51v-3.5a6.329 6.329 0 0 0-5.394 2.217 6.27 6.27 0 0 0-1.42 4.195 6.335 6.335 0 0 0 10.82 4.417 6.3 6.3 0 0 0 1.83-4.48V8.835a8.236 8.236 0 0 0 4.887 1.583V6.973a4.838 4.838 0 0 1-1.49-.287z"/></svg>
            <h4 style="margin:5px 0;">TikTok / Reels / Shorts</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">مقاس طولي 9:16 (1080x1920) ممتاز للهواتف</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_p2:
        st.markdown("""
        <div class="platform-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#ff0000"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
            <h4 style="margin:5px 0;">YouTube HD / Cinema</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">مقاس أفقي 16:9 (1920x1080) للشاشات الكبيرة</p>
        </div>
        """, unsafe_allow_html=True)

    with col_p3:
        st.markdown("""
        <div class="platform-card">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#e1306c"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            <h4 style="margin:5px 0;">Instagram Post</h4>
            <p style="color:#9ca3af; font-size:0.85rem;">مقاس مربع 1:1 (1080x1080) للبوستات</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_in1, col_in2 = st.columns([2, 1])
    with col_in1:
        v_topic = st.text_input("💡 فكرة الفيديو أو القصة السينمائية:", "رحلة مستكشف داخل مدينة مفقودة تحت الأرض")
        v_ratio = st.selectbox("📐 اختر القياس الدقيق لمنصتك:", [
            "🎵 TikTok / Shorts / Reels (9:16)", 
            "🔴 YouTube HD / Cinema (16:9)", 
            "📸 Instagram Post (1:1)"
        ])
        
    with col_in2:
        v_voice_label = st.selectbox("🎙️ صوت الراوي المفضل:", list(ARABIC_VOICES.keys()))
        v_voice_id = ARABIC_VOICES[v_voice_label]

    if "9:16" in v_ratio: vw, vh = 1080, 1920
    elif "16:9" in v_ratio: vw, vh = 1920, 1080
    else: vw, vh = 1080, 1080

    if st.button("🚀 إنشاء وتوليد الفيديو الفائق الآن"):
        if not v_topic.strip():
            st.error("يرجى كتابة عنوان القصة أولاً!")
        else:
            status = st.empty()
            pbar = st.progress(0)
            
            try:
                status.markdown("**🧠 Phase 1: كتابة أسطر القصة والتناسق الصوتي...**")
                
                # أسطر القصة السينمائية المتناسقة
                lines = [
                    f"في مكان لم تطأه قدم بشرية من قبل، تبدأ أسطورة {v_topic}.",
                    "جدران تحكي أسراراً غامضة من طيات الماضي المنسي.",
                    "كل خطوة للإمام تكشف حقائق لم يتوقعها أحد.",
                    "استعد للغوص في هذه التجربة الفريدة والشيقة!"
                ]
                
                sub_clips = []
                audio_clips = []
                temp_files = []
                total = len(lines)

                for i, line in enumerate(lines):
                    status.markdown(f"**🎨 Phase 2: توليد الصورة المتقاربة والصوت البشري ({i+1}/{total})...**")
                    
                    # 1. توليد وتثبيت الصوت
                    aud_file = f"temp_v_{i}.mp3"
                    asyncio.run(edge_tts.Communicate(line, v_voice_id).save(aud_file)) if HAS_EDGE_TTS else None
                    temp_files.append(aud_file)
                    
                    aclip = AudioFileClip(aud_file)
                    dur = aclip.duration
                    audio_clips.append(aclip)

                    # 2. توليد صورة AI مطابقة تماماً للمشهد والمقاس
                    img_obj = fetch_solid_ai_image(f"{v_topic}, {line}", vw, vh, seed_num=(i+1)*123)
                    
                    # تحويل الصورة إلى Mpy Clip ثابت بأبعاد مضبوطة يمنع الشاشة السوداء
                    bg_clip = ImageClip(np.array(img_obj)).set_duration(dur)
                    
                    # 3. كتابة النص باللغة العربية بدقة عالية
                    sub_np = create_subtitle_frame(line, vw, vh)
                    sub_clip = ImageClip(sub_np).set_duration(dur)

                    # 4. دمج الطبقات بحجم شاشة دقيق (size=(vw, vh))
                    scene = CompositeVideoClip([bg_clip, sub_clip], size=(vw, vh)).set_audio(aclip)
                    sub_clips.append(scene)
                    
                    pbar.progress(int(((i + 1) / total) * 80))

                status.markdown("**⚡ Phase 3: تجميع مقاطع المشاهد وإخراج الفيديو بدقة 30 FPS...**")
                
                # دمج كافة المقاطع وتحديد معدل الإطارات لتجنب أي تذبذب
                final_video = concatenate_videoclips(sub_clips, method="compose")
                out_path = "lumina_masterpiece_v7.mp4"
                
                final_video.write_videofile(
                    out_path, 
                    fps=30, 
                    codec='libx264', 
                    audio_codec='aac',
                    preset='ultrafast'
                )
                
                pbar.progress(100)
                status.empty()
                st.balloons()
                st.success("🎉 تم إنتاج الفيديو السينمائي بنجاح وبأقصى جودة!")
                st.video(out_path)

                # تنظيف الملفات المؤقتة
                for c in audio_clips: c.close()
                for f in temp_files:
                    if os.path.exists(f): os.remove(f)

            except Exception as e:
                st.error(f"حدث خطأ أثناء المعالجة: {str(e)}")

# 2. قسم معرض الفيديوهات الإشهارية النماذج
with tab_gallery:
    st.subheader("📺 معرض الفيديوهات الإشهارية وتجارب الموقع الجاهزة:")
    st.write("استعرض نماذج للفيديوهات والقصص التي تم إنتاجها بالكامل عبر منصة LUMINA AI:")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.markdown("##### 🎬 نموذج فيديو وثائقي رعب (9:16 TikTok)")
        st.info("💡 تم توليده باستخدام صوت 'حمزة' مع نمط صور الرعب الداكنة.")
    with col_g2:
        st.markdown("##### 🏛️ نموذج فيديو تاريخي (16:9 YouTube)")
        st.info("💡 تم توليده بصوت 'شاكر الوثائقي' ونمط الصور الزيتية.")

# 3. قسم صور الذكاء الاصطناعي
with tab_images:
    st.subheader("🎨 مولد الصور السينمائية فائقة الدقة")
    prompt_in = st.text_area("أدخل الوصف باللغة العربية أو الإنجليزية:", "تنين أسطوري ذهبي يطير فوق قلعة كلاسيكية في وقت الغروب")
    if st.button("✨ توليد الصورة الآن"):
        if prompt_in:
            with st.spinner("جاري الرسم والتوليد..."):
                gen_img = fetch_solid_ai_image(prompt_in, 1024, 1024, np.random.randint(1, 9999))
                st.image(gen_img, caption="الصورة المولدة", use_column_width=True)

# 4. قسم تحويل النص لصوت
with tab_audio:
    st.subheader("🎙️ تحويل النص إلى صوت بشري احترافي")
    text_in = st.text_area("النص المطلوب نطقة:", "أهلاً بكم في موقعنا الاحترافي لإنتاج الفيديوهات بالذكاء الاصطناعي")
    v_sel = st.selectbox("اختر الصوت:", list(ARABIC_VOICES.keys()), key="aud_tab")
    
    if st.button("🔊 استخراج الملف الصوتي"):
        if text_in:
            out_aud = "speech.mp3"
            asyncio.run(edge_tts.Communicate(text_in, ARABIC_VOICES[v_sel]).save(out_aud))
            st.audio(out_aud)
