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

# تجربة استيراد مكتبة OpenAI
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# 1. إعداد الصفحة وتصاميم Lumina AI العالمية
st.set_page_config(page_title="Lumina AI Studio Pro - BytePlus", page_icon="⚡", layout="wide")

# CSS سينمائي فاخر يحاكي واجهة Lumina AI / BytePlus
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background: #050811;
        color: #f1f5f9;
    }
    
    /* Navbar Top Bar */
    .lumina-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.9);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(56, 189, 248, 0.15);
        border-radius: 22px;
        padding: 16px 32px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.6);
    }
    .lumina-logo {
        font-size: 1.9rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00c6ff, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge-status {
        background: linear-gradient(90deg, #ec4899, #8b5cf6);
        color: white;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 800;
        box-shadow: 0 0 20px rgba(236, 72, 153, 0.4);
    }
    
    /* Hero Card */
    .hero-lumina {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.85) 0%, rgba(15, 23, 42, 0.98) 100%);
        border: 1px solid rgba(168, 85, 247, 0.25);
        border-radius: 28px;
        padding: 35px 28px;
        text-align: right;
        margin-bottom: 30px;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.75);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .hero-desc {
        color: #94a3b8;
        font-size: 1.15rem;
        line-height: 1.7;
    }

    /* Primary Action Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #00c6ff, #0072ff, #a855f7, #ec4899);
        color: white;
        font-size: 1.35rem;
        font-weight: 900;
        padding: 1.1rem;
        border-radius: 20px;
        border: none;
        box-shadow: 0 12px 35px rgba(0, 114, 255, 0.45);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 20px 45px rgba(236, 72, 153, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# الشريط العلوي
st.markdown("""
<div class="lumina-header">
    <div class="lumina-logo">⚡ Lumina AI Studio <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 400;">by BytePlus</span></div>
    <div>
        <span class="badge-status">🤖 ChatGPT & Seedance 2.5 Integrated</span>
    </div>
</div>
""", unsafe_allow_html=True)

# البانر الرئيسي
st.markdown("""
<div class="hero-lumina">
    <div class="badge-status">🔥 ULTIMATE MULTI-PLATFORM GENERATOR</div>
    <div class="hero-title">منصة توليد الفيديوهات والقصص AI المتكاملة</div>
    <div class="hero-desc">أنشئ قصصاً وفيديوهات احترافية 60 ثانية لجميع المنصات (TikTok, YouTube, Instagram, Snapchat, Facebook, LinkedIn) بكتابة سينمائية فائقة الوضوح وتوليد تلقائي بواسطة ChatGPT.</div>
</div>
""", unsafe_allow_html=True)

# الشريط الجانبي لإعدادات مفتاح API
st.sidebar.title("⚙️ إعدادات الذكاء الاصطناعي")
openai_api_key = st.sidebar.text_input("مفتاح OpenAI API Key (اختياري لكتابة ChatGPT):", type="password")

if openai_api_key:
    st.sidebar.success("تم تفعيل مفتاح ChatGPT بنجاح! 🟢")
else:
    st.sidebar.info("سيتم استخدام النماذج الذكية التلقائية في حال عدم ادخال المفتاح. ℹ️")

# دالة توليد الخلفية السينمائية المضمونة
def get_lumina_background(width, height, seed):
    try:
        url = f"https://picsum.photos/{width}/{height}?random={seed + 120}"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content)).convert('RGB')
    except:
        pass
    
    # خلفية سينمائية احتياطية عالية الجودة
    img = Image.new('RGB', (width, height), color=(8, 12, 25))
    draw = ImageDraw.Draw(img)
    for y in range(height):
        r = int(8 + (y / height) * 45)
        g = int(12 + (y / height) * 30)
        b = int(25 + (y / height) * 80)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
    return img

# دالة رسم النصوص السينمائية الواضحة فوق الصور (Text-On-Image Layer)
def render_lumina_text(text, lang='ar', width=1080, height=1920, font_color="yellow"):
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

    font_size = int(height * 0.042)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    cx = width // 2
    cy = int(height * 0.78) # موضعة الكلام في الثلث السفلي السينمائي
    
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    pad_x = int(width * 0.05)
    pad_y = int(height * 0.02)
    
    # 1. طبقة حماية سوداء شفافة خلف النص
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=18,
        fill=(0, 0, 0, 225),
        outline=(56, 189, 248, 120),
        width=2
    )

    color_rgb = (255, 235, 59, 255) if font_color == "yellow" else (255, 255, 255, 255)
    
    # 2. رسم الخط العريض الناصع
    draw.multiline_text((cx, cy), display_text, font=font, fill=color_rgb, anchor="mm", align="center")
    
    return np.array(img)

# دالة كتابة السكريبت بواسطة ChatGPT
def generate_chatgpt_script(topic, api_key):
    if HAS_OPENAI and api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            prompt = f"اكتب سكريبت قصة سينمائية مشوقة مدتها 60 ثانية حول موضوع: '{topic}'. مقسمة إلى 5 أسطر فقط، كل سطر يمثل مشهداً صغيراً بكلمات قوية ومباشرة بدون مقدمات أو أرقام."
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"تعذر الاتصال بـ ChatGPT API: {str(e)} - تم تفعيل المنشئ المحلي تلقائياً.")
    
    # منشئ احتياطي في حال عدم إدخال API Key
    return f"في عالم غريب ومثير، تبدأ رحلة {topic}.\nكل خطوة تقربنا من كشف السر المخبأ بين الظلال.\nأحداث متسارعة لم يكن يتوقعها أحد.\nاكتشف الحقيقة قبل فوات الأوان.\nهل أنت مستعد لهذه التجربة الفريدة؟"

# تبويبات الموقع
tab_gpt, tab_manual, tab_platforms, tab_models = st.tabs([
    "🤖 ChatGPT Auto-Script & Video Generator",
    "✍️ Manual Script Editor (60s)",
    "🌐 Platform & Dimensions Hub",
    "⚡ Lumina AI Model Suite"
])

# التبويب 1: توليد السكريبت بواسطة ChatGPT تلقائياً
with tab_gpt:
    st.subheader("🤖 توليد القصة والفيديو تلقائياً بواسطة ChatGPT")
    topic_input = st.text_input("أدخل موضوع القصة أو القناة (مثال: رحلة الفضاء، أسرار الذكاء الاصطناعي، حكايات تاريخية):", "أسرار المحيطات الغامضة")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        plat_gpt = st.selectbox(
            "اختر المنصة والمقاس التلقائي:",
            [
                "🎵 TikTok / Shorts / Reels (9:16)",
                "🔴 YouTube HD Video (16:9)",
                "📸 Instagram Post (1:1)",
                "👻 Snapchat Spotlight (9:16)",
                "📘 Facebook Reels (9:16)",
                "💼 LinkedIn Video (16:9)"
            ],
            key="plat_gpt"
        )
    with col_g2:
        voice_gpt = st.selectbox(
            "اختر الصوت واللغة:",
            [
                "🇸🇦 العربية - لهجة سعودية / خليجية",
                "🇪🇬 العربية - لهجة مصرية",
                "🌐 العربية - الفصحى القياسية",
                "🇺🇸 English - US Male/Female",
                "🇬🇧 English - UK British",
                "🇫🇷 French - Français",
                "🇪🇸 Spanish - Español"
            ],
            key="voice_gpt"
        )

# التبويب 2: تحرير السكريبت يدوياً
with tab_manual:
    st.subheader("✍️ تحرير نصوص السكريبت والمشاهد يدوياً")
    manual_script = st.text_area(
        "أدخل نصوص المشاهد (كل سطر يصنع مشهداً وصوراً متزامنة):",
        value="في عام 2050، فتحت البشرية أبواب المحيط الرقمي.\nسفن تنطلق نحو مجرات لم يطأها إنسان من قبل.\nأسرار كونية تنتظر من يفك شفرتها.\nرحلة لا عودة فيها نحو المستقبل.\nهل أنت مستعد لاكتشاف الحقيقة؟",
        height=160
    )

# التبويب 3: المنصات والأبعاد
with tab_platforms:
    st.subheader("📐 الأبعاد المتاحة وخصائص المنصات")
    st.markdown("""
    * **🎵 TikTok & Reels (9:16):** 1080x1920 (أفضل مقاس للفيديوهات العمودية القصيرة)
    * **🔴 YouTube Longform (16:9):** 1920x1080 (أفضل مقاس للشاشات الكبيرة والمحتوى السينمائي)
    * **📸 Instagram Feed (1:1):** 1080x1080 (مقاس مربع متوافق مع كافة التغذيات)
    * **📸 Instagram Story (4:5):** 1080x1350 (بورتريه ملائم للإعلانات)
    """)

# التبويب 4: خطط ونماذج Lumina
with tab_models:
    st.subheader("⚡ محركات الذكاء الاصطناعي المدمجة في Lumina AI")
    st.markdown("""
    - **Seedance 2.5:** محرك توليد الفيديو السينمائي عالي الجودة.
    - **Seedream 5.0 Pro:** محرك توليد الصور والخلفيات الذكية.
    - **OmniHuman 1.5:** محرك الشخصيات والمتحدثين الرقميين.
    - **GPT-4o Mini:** محرك صياغة السكريبتات والتحليل النصي.
    """)

st.markdown("---")

# إعدادات الأبعاد والصوت للتوليد
plat_choice = plat_gpt if 'plat_gpt' in locals() else "🎵 TikTok / Shorts / Reels (9:16)"
voice_choice = voice_gpt if 'voice_gpt' in locals() else "🇸🇦 العربية - لهجة سعودية / خليجية"

if "9:16" in plat_choice: width, height = 1080, 1920
elif "16:9" in plat_choice: width, height = 1920, 1080
elif "1:1" in plat_choice: width, height = 1080, 1080
else: width, height = 1080, 1350

voice_map = {
    "🇸🇦 العربية - لهجة سعودية / خليجية": ('ar', 'com.sa'),
    "🇪🇬 العربية - لهجة مصرية": ('ar', 'com.eg'),
    "🌐 العربية - الفصحى القياسية": ('ar', 'com'),
    "🇺🇸 English - US Male/Female": ('en', 'com'),
    "🇬🇧 English - UK British": ('en', 'co.uk'),
    "🇫🇷 French - Français": ('fr', 'fr'),
    "🇪🇸 Spanish - Español": ('es', 'es')
}
lang_code, tld_val = voice_map.get(voice_choice, ('ar', 'com'))

# زر الإنتاج الرئيسي
if st.button("🚀 إنشاء قصة وفيديو Lumina AI (60s) الآن"):
    status_box = st.empty()
    progress_bar = st.progress(0)
    
    # 1. توليد أو تجهيز النص
    status_box.markdown("**🤖 Step 1: جاري صياغة السكريبت بواسطة ChatGPT...**")
    if topic_input and len(topic_input.strip()) > 0:
        script_text = generate_chatgpt_script(topic_input, openai_api_key)
    else:
        script_text = manual_script
        
    lines = [l.strip() for l in script_text.split("\n") if l.strip()]
    
    if not lines:
        st.error("يرجى إدخال موضوع أو سكريبت أولاً!")
    else:
        try:
            sub_clips = []
            audio_clips = []
            temp_files = []
            total_lines = len(lines)
            
            for i, line in enumerate(lines):
                status_box.markdown(f"**🎨 Step 2: معالجة المشهد ({i+1}/{total_lines}) مع تركيب الصوت والنص على الصورة...**")
                
                # إنشاء الصوت
                audio_file = f"lumina_v12_{i}.mp3"
                tts = gTTS(text=line, lang=lang_code, tld=tld_val)
                tts.save(audio_file)
                temp_files.append(audio_file)
                
                a_clip = AudioFileClip(audio_file)
                line_dur = a_clip.duration
                audio_clips.append(a_clip)

                # جلب الصورة السينمائية
                bg_img = get_lumina_background(width, height, i)
                bg_clip = ImageClip(np.array(bg_img)).set_duration(line_dur)

                # رسم النص الواضح جداً فوق الصورة
                txt_np = render_lumina_text(line, lang=lang_code, width=width, height=height, font_color="yellow")
                txt_clip = ImageClip(txt_np).set_duration(line_dur)

                # دمج المشهد
                scene = CompositeVideoClip([bg_clip, txt_clip]).set_audio(a_clip)
                sub_clips.append(scene)
                
                progress_bar.progress(int(((i + 1) / total_lines) * 85))

            status_box.markdown("**⚡ Step 3: جاري الرندر النهائي وتصدير قصة الـ 60 ثانية...**")
            final_video = concatenate_videoclips(sub_clips)
            output_file = "lumina_v12_final.mp4"
            final_video.write_videofile(output_file, fps=24, codec='libx264', audio_codec='aac')

            progress_bar.progress(100)
            status_box.empty()
            
            # التنظيف
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("✨ تم توليد الفيديو السينمائي بنجاح!")
            st.video(output_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
