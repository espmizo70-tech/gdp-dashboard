import streamlit as st
import os
import requests
import io
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

# إعداد الصفحة بنمط منصة Lumina AI
st.set_page_config(page_title="Lumina AI Video Studio", page_icon="⚡", layout="wide")

# CSS سينمائي فاخر يحاكي منصات BytePlus / Lumina AI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;800;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background-color: #070a12;
        color: #f1f5f9;
    }
    
    /* Navbar Top Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px 24px;
        margin-bottom: 20px;
    }
    .brand-logo {
        font-size: 1.6rem;
        font-weight: 900;
        background: linear-gradient(90deg, #38bdf8, #a855f7, #f43f5e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Hero Section Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 24px;
        padding: 30px;
        text-align: right;
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 1.1rem;
    }
    
    /* Feature Badge */
    .badge-vip {
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb, #7c3aed, #d946ef);
        color: white;
        font-size: 1.25rem;
        font-weight: 900;
        padding: 0.9rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(217, 70, 239, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# الشريط العلوي للموقع
st.markdown("""
<div class="top-nav">
    <div class="brand-logo">⚡ LUMINA AI STUDIO PRO</div>
    <div><span class="badge-vip">VIP Seedance 2.5 Engine</span></div>
</div>
""", unsafe_allow_html=True)

# البانر الرئيسي
st.markdown("""
<div class="hero-banner">
    <div class="badge-vip">🔥 LIMITED TIME EXCLUSIVE</div>
    <div class="hero-title">منصة توليد القصص والفيديوهات السينمائية AI</div>
    <div class="hero-sub">أنشئ فيديوهات 60 ثانية احترافية بخلفيات متناسقة ونصوص فائقة الوضوح لجميع المنصات.</div>
</div>
""", unsafe_allow_html=True)

# دالة توليد الخلفية السينمائية المضمونة (تمنع الشاشة السوداء)
def get_cinematic_background(width, height, seed):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={seed + 80}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content)).convert('RGB')
    except:
        pass
    
    # خلفية تدرج سينمائي احتياطية في حال انقطاع الشبكة
    img = Image.new('RGB', (width, height), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(10 + (y / height) * 45)
        g = int(15 + (y / height) * 25)
        b = int(40 + (y / height) * 70)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

# دالة رسم النصوص الواضحة جداً الكبيرة (PIL Direct - تجنب ImageMagick)
def render_crisp_subtitles(text, lang='ar', width=1080, height=1920, text_color="yellow"):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # ضبط التفاف الكلمات بحسب مقاس الشاشة
    wrap_limit = 22 if width < height else 45
    lines = textwrap.wrap(text, width=wrap_limit)
    wrapped_text = "\n".join(lines)
    
    if lang == 'ar':
        reshaped = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped)
    else:
        display_text = wrapped_text

    # تكبير الخط ليكون واضحاً جداً في الثلث السفلي
    font_size = int(height * 0.042)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    cx = width // 2
    cy = int(height * 0.75) # وضع الكلمات في الثلث السفلي
    
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    padding_x = int(width * 0.05)
    padding_y = int(height * 0.02)
    
    # 1. إطار خلفية اسود شفاف مائل للانحناء لحماية النص
    draw.rounded_rectangle(
        [bbox[0]-padding_x, bbox[1]-padding_y, bbox[2]+padding_x, bbox[3]+padding_y],
        radius=16,
        fill=(0, 0, 0, 220),
        outline=(255, 255, 255, 80),
        width=2
    )

    color_rgb = (255, 235, 59, 255) if text_color == "yellow" else (255, 255, 255, 255)
    
    # 2. رسم النص بخط واضح وعريض
    draw.multiline_text((cx, cy), display_text, font=font, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# تقسيم الخيارات إلى 3 أجزاء
col_platform, col_voice, col_content = st.columns([1, 1, 1.2])

with col_platform:
    st.subheader("📐 1. أبعاد المنصة والمقاسات")
    platform = st.selectbox(
        "اختر مقاس الفيديو والأبعاد:",
        [
            "🎵 TikTok / Shorts / Reels (9:16 - عمودي)",
            "🔴 YouTube Video (16:9 - أفقي)",
            "📸 Instagram Feed (1:1 - مربع)",
            "📸 Instagram Story (4:5 - بورتريه)"
        ]
    )
    
    if "9:16" in platform: width, height = 1080, 1920
    elif "16:9" in platform: width, height = 1920, 1080
    elif "1:1" in platform: width, height = 1080, 1080
    else: width, height = 1080, 1350

    text_color = st.selectbox("لون كتابة النص:", ["yellow", "white"])

with col_voice:
    st.subheader("🎙️ 2. اختيار الصوت واللغة")
    voice_choice = st.selectbox(
        "اختر التعليق الصوتي المفضل:",
        [
            "🇸🇦 العربية - لهجة سعودية / خليجية",
            "🇪🇬 العربية - لهجة مصري / فصحى",
            "🌐 العربية - الفصحى القياسية",
            "🇺🇸 English - US Voice (أمريكي)",
            "🇬🇧 English - UK Voice ( بريطاني)"
        ]
    )
    
    voice_config = {
        "🇸🇦 العربية - لهجة سعودية / خليجية": ('ar', 'com.sa'),
        "🇪🇬 العربية - لهجة مصري / فصحى": ('ar', 'com.eg'),
        "🌐 العربية - الفصحى القياسية": ('ar', 'com'),
        "🇺🇸 English - US Voice (أمريكي)": ('en', 'com'),
        "🇬🇧 English - UK Voice ( بريطاني)": ('en', 'co.uk')
    }
    lang_code, tld_val = voice_config[voice_choice]

with col_content:
    st.subheader("📜 3. نماذج قصص الـ 60 ثانية")
    story_template = st.selectbox(
        "اختر قصة جاهزة أو اكتب قصتك:",
        [
            "✍️ كتابة قصة خاصة",
            "🌌 قصة الرحلة الكونية المذهلة (60 ثانية)",
            "⚔️ قصة الأسرار المفقودة (60 ثانية)",
            "🕵️ English Story: The Hidden Legacy (60s)"
        ]
    )
    
    templates = {
        "🌌 قصة الرحلة الكونية المذهلة (60 ثانية)": "في عام 2050، فتحت البشرية أبواب المحيط الرقمي.\nسفن تنطلق نحو مجرات لم يطأها إنسان من قبل.\nأسرار كونية تنتظر من يفك شفرتها.\nرحلة لا عودة فيها نحو المستقبل.\nهل أنت مستعد لاكتشاف الحقيقة؟",
        "⚔️ قصة الأسرار المفقودة (60 ثانية)": "كانت الغابة تطوي سرها بين الأشجار الكثيفة.\nصوت غريب ينادي من بين الضباب.\nكل خطوة تقربنا من الكنز المفقود.\nرحلة مليئة بالغموض والإثارة.\nاكتشف السر قبل فوات الأوان.",
        "🕵️ English Story: The Hidden Legacy (60s)": "Deep inside the ancient mountains lies a forgotten secret.\nEvery step closer reveals a mysterious story.\nLegends speak of a power hidden in plain sight.\nAre you ready to uncover the truth?"
    }

    script_val = templates.get(story_template, "أدخل الجمل هنا.\nكل جملة في سطر مستقل لتصنع مشهداً وصوراً متزامنة.")
    user_script = st.text_area("نص السكريبت:", value=script_val, height=140)

st.markdown("---")

# زر الإنتاج
if st.button("🚀 إنشاء فيديو Lumina AI السينمائي الآن"):
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
                status_box.markdown(f"**🎬 جاري بناء المشهد وترتيب الكلام على الصورة ({i+1}/{total_lines})...**")
                
                # 1. الصوت
                audio_file = f"voice_lumina_{i}.mp3"
                tts = gTTS(text=line, lang=lang_code, tld=tld_val)
                tts.save(audio_file)
                temp_files.append(audio_file)
                
                a_clip = AudioFileClip(audio_file)
                line_dur = a_clip.duration
                audio_clips.append(a_clip)

                # 2. الصورة
                bg_img = get_cinematic_background(width, height, i)
                bg_clip = ImageClip(np.array(bg_img)).set_duration(line_dur)

                # 3. النص العريض والواضح
                txt_np = render_crisp_subtitles(line, lang=lang_code, width=width, height=height, text_color=text_color)
                txt_clip = ImageClip(txt_np).set_duration(line_dur)

                # الدمج
                scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(a_clip)
                sub_clips.append(scene)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 85))

            status_box.markdown("**⚡ جاري رندر ومعالجة الأبعاد النهائية...**")
            final_video = concatenate_videoclips(sub_clips)
            output_file = "lumina_final_video.mp4"
            final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status_box.empty()
            
            # تنظيف
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم إنشاء الفيديو وقصة الـ 60 ثانية بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
