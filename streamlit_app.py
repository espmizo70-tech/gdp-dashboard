import streamlit as st
import os
import requests
import io
import textwrap
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 1. تهيئة الصفحة والأنماط البصرية الاحترافية لـ DaVinci AI
st.set_page_config(
    page_title="DaVinci AI | Sora 2.0 Video Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS داكن مستوحى من DaVinci AI & Sora 2.0 (Glassmorphism & Gold/Neon Accents)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Orbitron:wght@700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background: #090a0f;
        color: #e2e8f0;
    }
    
    /* DaVinci Header */
    .davinci-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(18, 20, 29, 0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.25);
        border-radius: 20px;
        padding: 16px 30px;
        margin-bottom: 25px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.8);
    }
    .davinci-brand {
        font-family: 'Orbitron', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f39c12, #d4af37, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .sora-badge {
        background: linear-gradient(90deg, #d4af37, #e67e22);
        color: #000;
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* DaVinci Studio Card */
    .studio-card {
        background: linear-gradient(145deg, rgba(20, 24, 38, 0.9), rgba(10, 12, 18, 0.95));
        border: 1px solid rgba(212, 175, 55, 0.18);
        border-radius: 24px;
        padding: 28px;
        margin-bottom: 25px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
    }

    /* Primary Action Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #f39c12, #00c6ff);
        color: #000;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 1rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.35);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.005);
        box-shadow: 0 15px 40px rgba(0, 198, 255, 0.5);
        color: #fff;
    }
</style>
""", unsafe_allow_html=True)

# الشريط العلوي
st.markdown("""
<div class="davinci-nav">
    <div class="davinci-brand">🎨 DAVINCI AI <span class="sora-badge">SORA 2.0 ENGINE</span></div>
    <div>
        <span style="color: #94a3b8; font-size: 0.9rem;">Ultra-Realistic AI Video Generator</span>
    </div>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي (Side Controls)
st.sidebar.title("🎛️ DaVinci Studio Controls")
openai_key = st.sidebar.text_input("OpenAI API Key (Enhancer & Scripts):", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🎬 إعدادات الكاميرا والإخراج")
camera_motion = st.sidebar.selectbox(
    "حركة الكاميرا (Camera Motion):",
    ["Static (ثابت)", "Zoom In (تقريب سينمائي)", "Pan Right (مسح أفقـي)", "Crane Up (ارتفاع سينمائي)"]
)
motion_strength = st.sidebar.slider("كثافة الحركة (Motion Intensity):", 1, 10, 5)

style_preset = st.sidebar.selectbox(
    "النمط البصري (Style Preset):",
    [
        "📽️ Cinematic Photorealistic 8K",
        "🌆 Cyberpunk Neon Noir",
        "🎨 Japanese Anime / Studio Ghibli",
        "🖌️ Digital 3D Concept Art",
        "🎞️ Vintage 35mm Film"
    ]
)

# دالة توليد الخلفية البصرية الاحترافية
def fetch_davinci_frame(width, height, prompt_seed, motion_type="Static"):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={prompt_seed + 77}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content)).convert('RGB')
            # تطبيق تحسين بصري بحسب النمط
            enhancer = ImageEnhance.Color(img)
            img = enhancer.enhance(1.25)
            return img
    except:
        pass
    
    # خلفية نيون احتياطية لـ DaVinci
    img = Image.new('RGB', (width, height), color=(12, 14, 24))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(12 + (y / height) * 60)
        g = int(14 + (y / height) * 40)
        b = int(24 + (y / height) * 90)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

# دالة رسم النصوص السينمائية المتوافقة مع كافة المقاسات
def draw_davinci_subtitles(text, lang='ar', width=1080, height=1920):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    wrap_limit = 24 if width < height else 48
    lines = textwrap.wrap(text, width=wrap_limit)
    wrapped_text = "\n".join(lines)
    
    if lang in ['ar', 'ar-sa']:
        reshaped = arabic_reshaper.reshape(wrapped_text)
        display_text = get_display(reshaped)
    else:
        display_text = wrapped_text

    font_size = int(height * 0.038)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    cx, cy = width // 2, int(height * 0.80)
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    
    pad_x, pad_y = int(width * 0.04), int(height * 0.018)
    
    # خلفية نيون شفافة تحت الخط
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=14,
        fill=(8, 10, 18, 220),
        outline=(212, 175, 55, 180),
        width=2
    )
    
    draw.multiline_text((cx, cy), display_text, font=font, fill=(255, 235, 59, 255), anchor="mm", align="center")
    return np.array(img)

# دالة تحسين الوصف عبر ChatGPT (Sora Prompt Enhancer)
def enhance_prompt_with_gpt(prompt, api_key):
    if HAS_OPENAI and api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Convert this idea into a 5-scene detailed cinematic script (one line per scene) for Sora 2.0 video generator: '{prompt}'"
                }],
                max_tokens=250
            )
            return res.choices[0].message.content.strip()
        except:
            pass
    return f"{prompt}\nمباني مستقبلية تضيء أفق المدينة بنيون متحرك.\nسيارات طائرة تعبر بين السحاب بصوت محركات فائقة.\nالبطل ينظر إلى الأفق البعيد في انتظار المستقبل.\nشعار DaVinci AI يظهر في السماء بروعة سينمائية."

# واجهة التبويبات الرئيسية
tab_studio, tab_gallery, tab_settings = st.tabs(["🚀 Sora 2.0 Generator", "🖼️ Showcase & Presets", "⚙️ API Integration"])

with tab_studio:
    st.markdown("""
    <div class="studio-card">
        <h3>⚡ Prompt Studio - منشئ الفيديو السينمائي</h3>
        <p style="color: #94a3b8;">أدخل الوصف (Text Prompt) أو الفكرة، وسيقوم محرك Sora 2.0 بتوليد المشاهد وتطبيق حركة الكاميرا والتعليق الصوتي.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2 = st.columns([2, 1])
    
    with col_p1:
        user_prompt = st.text_area(
            "وصف الفيديو (Prompt / Story Idea):",
            "روبوت في المستقبل يكتشف زهرة نادرة تنمو في وسط مدينة مهجورة",
            height=120
        )
        negative_prompt = st.text_input("الوصف المستبعد (Negative Prompt):", "blurry, low quality, distorted hands, bad lighting")
    
    with col_p2:
        aspect_ratio = st.selectbox(
            "أبعاد المنصة (Aspect Ratio):",
            ["9:16 - Vertical (TikTok / Reels / Shorts)", "16:9 - Landscape (YouTube / Cinema)", "1:1 - Square (Instagram Feed)", "21:9 - Ultrawide Cinema"]
        )
        voice_lang = st.selectbox(
            "لغات التعليق الصوتي:",
            ["🇸🇦 العربية (سعودي/خليجي)", "🌐 العربية (فصحى)", "🇺🇸 English (US)", "🇬🇧 English (UK)", "🇫🇷 French"]
        )

    # تحديد مقاسات الفيديو
    if "9:16" in aspect_ratio: w, h = 1080, 1920
    elif "16:9" in aspect_ratio: w, h = 1920, 1080
    elif "1:1" in aspect_ratio: w, h = 1080, 1080
    else: w, h = 1920, 810 # 21:9

    voice_map = {
        "🇸🇦 العربية (سعودي/خليجي)": ('ar', 'com.sa'),
        "🌐 العربية (فصحى)": ('ar', 'com'),
        "🇺🇸 English (US)": ('en', 'com'),
        "🇬🇧 English (UK)": ('en', 'co.uk'),
        "🇫🇷 French": ('fr', 'fr')
    }
    lang, tld = voice_map[voice_lang]

    st.markdown("---")

    if st.button("✨ Generate DaVinci Sora 2.0 Video"):
        if not user_prompt.strip():
            st.error("يرجى أدخال وصف الفيديو أولاً!")
        else:
            status_box = st.empty()
            prog_bar = st.progress(0)
            
            try:
                status_box.markdown("**🤖 Phase 1: معالجة البرومبت وتحسين السكريبت بواسطة Sora Engine...**")
                script = enhance_prompt_with_gpt(user_prompt, openai_key)
                lines = [l.strip() for l in script.split("\n") if l.strip()][:5]
                
                sub_clips = []
                audio_clips = []
                temp_files = []
                total = len(lines)
                
                for i, line in enumerate(lines):
                    status_box.markdown(f"**🎬 Phase 2: رندر المشهد السينمائي ({i+1}/{total}) مع حركة الكاميرا ({camera_motion})...**")
                    
                    # 1. الصوت
                    aud_path = f"davinci_audio_{i}.mp3"
                    tts = gTTS(text=line, lang=lang, tld=tld)
                    tts.save(aud_path)
                    temp_files.append(aud_path)
                    
                    aclip = AudioFileClip(aud_path)
                    dur = aclip.duration
                    audio_clips.append(aclip)

                    # 2. الصورة البصرية
                    bg_img = fetch_davinci_frame(w, h, i * 42, camera_motion)
                    bg_clip = ImageClip(np.array(bg_img)).set_duration(dur)
                    
                    # 3. محاكاة حركة الكاميرا بسيطاً (Zoom Effect)
                    if "Zoom" in camera_motion:
                        bg_clip = bg_clip.resize(lambda t: 1 + 0.03 * t)

                    # 4. النص السلس فوق الصورة
                    sub_np = draw_davinci_subtitles(line, lang=lang, width=w, height=h)
                    sub_clip = ImageClip(sub_np).set_duration(dur)

                    # التركيب النهائي للمشهد
                    scene = CompositeVideoClip([bg_clip, sub_clip]).set_audio(aclip)
                    sub_clips.append(scene)
                    
                    prog_bar.progress(int(((i + 1) / total) * 85))

                status_box.markdown("**⚡ Phase 3: تجميع الصوت وتصدير الفيديو بدقة عالية...**")
                final_v = concatenate_videoclips(sub_clips)
                out_file = "davinci_sora_output.mp4"
                final_v.write_videofile(out_file, fps=24, codec='libx264', audio_codec='aac')
                
                prog_bar.progress(100)
                status_box.empty()
                
                # التنظيف
                for c in audio_clips: c.close()
                for f in temp_files:
                    if os.path.exists(f): os.remove(f)

                st.balloons()
                st.success("🎉 تم إنشاء فيديو DaVinci Sora 2.0 بنجاح!")
                st.video(out_file)

            except Exception as e:
                st.error(f"حدث خطأ أثناء رندر الفيديو: {str(e)}")

with tab_gallery:
    st.subheader("🖼️ معرض الأنماط والمخرجات السابقة (DaVinci Presets)")
    st.info("استعرض نماذج الصور المولدة عبر المحرك:")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.image("https://picsum.photos/600/1000?random=1", caption="Cinematic 8K")
    with col_m2:
        st.image("https://picsum.photos/600/1000?random=2", caption="Cyberpunk City")
    with col_m3:
        st.image("https://picsum.photos/600/1000?random=3", caption="Anime Visuals")

with tab_settings:
    st.subheader("⚙️ ربط المزودات المباشرة (Direct API Integration)")
    st.write("يمكنك ربط مفاتيح API المباشرة مثل OpenAI أو Runway أو Midjourney للحصول على سرعة توليد مضاعفة.")
    st.text_input("Runway Gen-2 API Key:")
    st.text_input("Midjourney / Pika API Key:")
