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

# 1. إعداد الصفحة والأنماط البصرية لمنصة Lumina AI
st.set_page_config(page_title="Lumina AI Studio | BytePlus", page_icon="⚡", layout="wide")

# CSS سينمائي أسود زجاجي مطابق لمنصة BytePlus Lumina
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background-color: #060913;
        color: #f8fafc;
    }
    
    /* Navbar Lumina Top Header */
    .lumina-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 14px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .lumina-logo {
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00c6ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .badge-lumina {
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        color: white;
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 800;
        box-shadow: 0 0 15px rgba(236, 72, 153, 0.4);
    }
    
    /* Lumina Hero Card */
    .hero-lumina {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.8) 0%, rgba(15, 23, 42, 0.95) 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 26px;
        padding: 32px 24px;
        text-align: right;
        margin-bottom: 28px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7);
    }
    .hero-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 8px;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 1.15rem;
    }

    /* Model Cards Grid UI */
    .model-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .model-card:hover {
        border-color: #38bdf8;
        transform: translateY(-4px);
        box-shadow: 0 15px 35px rgba(56, 189, 248, 0.2);
    }

    /* Styled Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00c6ff, #0072ff, #a855f7);
        color: white;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 1rem;
        border-radius: 18px;
        border: none;
        box-shadow: 0 12px 30px rgba(0, 114, 255, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.005);
        box-shadow: 0 18px 40px rgba(168, 85, 247, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# الشريط العلوي
st.markdown("""
<div class="lumina-nav">
    <div class="lumina-logo">⚡ Lumina AI <span style="font-size: 0.9rem; color: #94a3b8; font-weight: normal;">by BytePlus</span></div>
    <div>
        <span class="badge-lumina">🔥 Seedance 2.5 & Seedream 5.0 Powered</span>
    </div>
</div>
""", unsafe_allow_html=True)

# البانر الرئيسي
st.markdown("""
<div class="hero-banner hero-lumina">
    <div class="badge-lumina">LIMITED TIME VIP OFFER</div>
    <div class="hero-title">منصة Lumina AI لصناعة الفيديوهات والقصص 60s</div>
    <div class="hero-desc">استخدم أحدث محركات الذكاء الاصطناعي المباشرة (Text-to-Video & Multimodal) مع إمكانية ضبط المقاسات لـ TikTok، YouTube، وInstagram بأصوات فائقة الوضوح.</div>
</div>
""", unsafe_allow_html=True)

# دالة توليد خلفية سينمائية فائقة الوضوح
def fetch_lumina_background(width, height, seed):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={seed + 500}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content)).convert('RGB')
    except:
        pass
    
    # خلفية سينمائية احتياطية تضمن التوليد دائماً
    img = Image.new('RGB', (width, height), color=(10, 15, 30))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(10 + (y / height) * 50)
        g = int(15 + (y / height) * 30)
        b = int(45 + (y / height) * 80)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

# دالة رسم النصوص السينمائية الواضحة جداً فوق الصورة
def render_lumina_text(text, lang='ar', width=1080, height=1920, font_color="yellow"):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    wrap_limit = 24 if width < height else 48
    lines = textwrap.wrap(text, width=wrap_limit)
    wrapped_text = "\n".join(lines)
    
    if lang == 'ar':
        reshaped = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped)
    else:
        display_text = wrapped_text

    font_size = int(height * 0.04)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    cx, cy = width // 2, int(height * 0.78) # موضع الكلمات في الثلث السفلي
    
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    pad_x = int(width * 0.04)
    pad_y = int(height * 0.02)
    
    # 1. صندوق حماية خلفي شبه شفاف عالي الوضوح
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=18,
        fill=(0, 0, 0, 220),
        outline=(56, 189, 248, 100),
        width=2
    )

    color_rgb = (255, 235, 59, 255) if font_color == "yellow" else (255, 255, 255, 255)
    
    # 2. كتابة النص عالي الدقة
    draw.multiline_text((cx, cy), display_text, font=font, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# قائمة التبويبات المماثلة لمنصة BytePlus Lumina
tab_video, tab_image, tab_avatar, tab_pricing = st.tabs([
    "🎬 Seedance 2.5 (Video Generator)",
    "🖼️ Seedream 5.0 (Image AI)",
    "🗣️ OmniHuman 1.5 (AI Avatar)",
    "💳 Plans & Pricing"
])

with tab_video:
    col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1.2])

    with col_nav1:
        st.subheader("📐 1. أبعاد المنصة")
        platform = st.selectbox(
            "اختر منصتك والمقاس القياسي:",
            [
                "🎵 TikTok / Shorts / Reels (9:16 - عمودي)",
                "🔴 YouTube HD (16:9 - أفقي)",
                "📸 Instagram Post (1:1 - مربع)",
                "📸 Instagram Feed (4:5 - بورتريه)"
            ]
        )
        
        if "9:16" in platform: width, height = 1080, 1920
        elif "16:9" in platform: width, height = 1920, 1080
        elif "1:1" in platform: width, height = 1080, 1080
        else: width, height = 1080, 1350

        text_color = st.selectbox("لون كتابة النص السينمائي:", ["yellow", "white"])

    with col_nav2:
        st.subheader("🎙️ 2. محرك التعليق الصوتي")
        voice_choice = st.selectbox(
            "اختر صوت الراوي والنطق:",
            [
                "🇸🇦 العربية - لهجة سعودية / خليجية",
                "🇪🇬 العربية - لهجة مصرية",
                "🌐 العربية - الفصحى القياسية",
                "🇺🇸 English - US Male/Female",
                "🇬🇧 English - UK British"
            ]
        )
        
        voice_map = {
            "🇸🇦 العربية - لهجة سعودية / خليجية": ('ar', 'com.sa'),
            "🇪🇬 العربية - لهجة مصرية": ('ar', 'com.eg'),
            "🌐 العربية - الفصحى القياسية": ('ar', 'com'),
            "🇺🇸 English - US Male/Female": ('en', 'com'),
            "🇬🇧 English - UK British": ('en', 'co.uk')
        }
        lang_code, tld_val = voice_map[voice_choice]

    with col_nav3:
        st.subheader("📜 3. سكريبت القصة (60 ثانية)")
        story_preset = st.selectbox(
            "اختر سيناريو جاهز أو اكتب قصتك:",
            [
                "✍️ قصة خاصة مخصصة",
                "🌌 Lumina Sci-Fi: رحلة المستقبل (60 ثانية)",
                "⚔️ Lumina Mystery: أسرار القلعة (60 ثانية)",
                "🕵️ English Narrative: Cyberpunk 2050 (60s)"
            ]
        )
        
        presets = {
            "🌌 Lumina Sci-Fi: رحلة المستقبل (60 ثانية)": "في عام 2050، فتحت البشرية أبواب المحيط الرقمي.\nسفن تنطلق نحو مجرات لم يطأها إنسان من قبل.\nأسرار كونية تنتظر من يفك شفرتها.\nرحلة لا عودة فيها نحو المستقبل.\nهل أنت مستعد لاكتشاف الحقيقة؟",
            "⚔️ Lumina Mystery: أسرار القلعة (60 ثانية)": "كانت الغابة تطوي سرها بين الأشجار الكثيفة.\nصوت غريب ينادي من بين الضباب.\nكل خطوة تقربنا من الكنز المفقود.\nرحلة مليئة بالغموض والإثارة.\nاكتشف السر قبل فوات الأوان.",
            "🕵️ English Narrative: Cyberpunk 2050 (60s)": "Deep inside the digital metropolis lies a secret code.\nEvery generation holds a unique power.\nStep into the future of artificial intelligence.\nAre you ready to unlock the ultimate journey?"
        }

        default_text = presets.get(story_preset, "أدخل الجمل هنا.\nكل جملة في سطر تصنع مشهداً سينمائياً جديداً.")
        script_input = st.text_area("نص السكريبت:", value=default_text, height=140)

    st.markdown("---")

    if st.button("⚡ توليد فيديو Seedance 2.5 (60s Lumina Video)"):
        lines = [l.strip() for l in script_input.split("\n") if l.strip()]
        
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
                    status_box.markdown(f"**🎬 جاري بناء المشهد السينمائي ({i+1}/{total_lines}) بمحرك Lumina...**")
                    
                    # الصوت
                    audio_file = f"voice_lumina_{i}.mp3"
                    tts = gTTS(text=line, lang=lang_code, tld=tld_val)
                    tts.save(audio_file)
                    temp_files.append(audio_file)
                    
                    a_clip = AudioFileClip(audio_file)
                    line_duration = a_clip.duration
                    audio_clips.append(a_clip)

                    # الخلفية
                    bg_img = fetch_lumina_background(width, height, i)
                    bg_clip = ImageClip(np.array(bg_img)).set_duration(line_duration)

                    # النص السينمائي المتراكب فوق الصورة
                    txt_np = render_lumina_text(line, lang=lang_code, width=width, height=height, font_color=text_color)
                    txt_clip = ImageClip(txt_np).set_duration(line_duration)

                    # التركيب
                    scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(a_clip)
                    sub_clips.append(scene)
                    
                    progress_bar.progress(int(((i + 1) / total_lines) * 85))

                status_box.markdown("**⚡ جاري رندر ومعالجة أبعاد الفيديو النهائية...**")
                final_video = concatenate_videoclips(sub_clips)
                output_file = "lumina_seedance_output.mp4"
                final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

                progress_bar.progress(100)
                status_box.empty()
                
                for c in audio_clips: c.close()
                for f in temp_files:
                    if os.path.exists(f): os.remove(f)

                st.balloons()
                st.success("✨ تم إنشاء الفيديو وقصة الـ 60 ثانية بنجاح!")
                st.video(output_file)

            except Exception as e:
                st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")

with tab_image:
    st.subheader("🖼️ Seedream 5.0 Pro - محرك توليد الصور السينمائية")
    st.info("مولد الصور عالي الدقة المدمج للتصاميم والرسم الرقمي")
    img_prompt = st.text_input("أدخل وصف الصورة (Prompt):", "A cyberpunk futuristic cityscape at night, cinematic lighting, 8k render")
    img_ratio = st.radio("نسبة الأبعاد:", ["9:16", "16:9", "1:1"], horizontal=True)
    
    if st.button("✨ توليد الصورة باستخدام Seedream 5.0"):
        w, h = (1080, 1920) if img_ratio == "9:16" else (1920, 1080) if img_ratio == "16:9" else (1080, 1080)
        generated_img = fetch_lumina_background(w, h, seed=999)
        st.image(generated_img, caption="نتيجة Seedream 5.0 Pro", use_container_width=True)

with tab_avatar:
    st.subheader("🗣️ OmniHuman 1.5 - صنع المتحدث الرقمي الذكي")
    st.write("قم بتثبيت صور الأبطال والشخصيات للتعليق الصوتي التلقائي.")
    st.file_uploader("ارفع صورة الشخصية (JPG/PNG):", type=["jpg", "png", "jpeg"])
    st.text_area("نص كلام الشخصية الرقمية:")

with tab_pricing:
    st.subheader("💳 خطط الاشتراكات والأسعار (Lumina Pro Pricing)")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown("""
        <div class="model-card">
            <h3>Starter</h3>
            <h2>$0 <span style="font-size: 1rem;">/ شهر</span></h2>
            <p>7 دقائق تجريبية شهرياً</p>
            <p>دقة 480p / 720p</p>
        </div>
        """, unsafe_allow_html=True)
    with col_p2:
        st.markdown("""
        <div class="model-card" style="border-color: #ec4899;">
            <span class="badge-lumina">POPULAR</span>
            <h3>Lumina VIP</h3>
            <h2>$29 <span style="font-size: 1rem;">/ شهر</span></h2>
            <p>Seedance 2.5 4K فيديو</p>
            <p>توليد فيديوهات 60s غير محدودة</p>
        </div>
        """, unsafe_allow_html=True)
    with col_p3:
        st.markdown("""
        <div class="model-card">
            <h3>Enterprise API</h3>
            <h2>Custom</h2>
            <p>ربط API مباشر مع السيرفر</p>
            <p>دعم فني وتوليد فوري</p>
        </div>
        """, unsafe_allow_html=True)
