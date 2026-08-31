import streamlit as st
import os
import requests
import io
import textwrap
import asyncio
import json
import urllib.parse
import numpy as np
import csv
from datetime import datetime

# 🛠️ حل مشكلة Pillow/ANTIALIAS تلقائياً
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import (
    ImageClip, CompositeVideoClip, AudioFileClip, 
    concatenate_videoclips
)
import arabic_reshaper
from bidi.algorithm import get_display

# فحص المكتبات
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

# 1. تهيئة الصفحة والواجهة
st.set_page_config(
    page_title="Lumina & DaVinci AI | Enterprise SaaS Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم SaaS إحترافي للغاية باللون الأسود الملكي والتوهج الذهبي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Orbitron:wght@700;900&display=swap');
    
    * { font-family: 'Cairo', sans-serif; }
    
    .stApp {
        background: #020408;
        color: #f8fafc;
    }
    
    /* Top Header Bar */
    .app-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(25px);
        border: 1px solid rgba(212, 175, 55, 0.35);
        border-radius: 20px;
        padding: 16px 28px;
        margin-bottom: 25px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.9);
    }
    .app-brand {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.1rem;
        font-weight: 900;
        background: linear-gradient(90deg, #f39c12, #d4af37, #00f2fe, #a855f7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .badge-user {
        background: rgba(212, 175, 55, 0.15);
        border: 1px solid #d4af37;
        color: #f39c12;
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.88rem;
        font-weight: 700;
    }

    /* Auth Login Card */
    .auth-card {
        max-width: 520px;
        margin: 60px auto;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.85) 100%);
        border: 2px solid rgba(212, 175, 55, 0.4);
        border-radius: 28px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95), 0 0 40px rgba(212, 175, 55, 0.2);
    }
    .auth-title {
        font-size: 2.2rem;
        font-weight: 900;
        background: linear-gradient(90deg, #ffffff, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* Primary SaaS Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #f39c12, #00c6ff, #a855f7);
        color: #000000;
        font-size: 1.3rem;
        font-weight: 900;
        padding: 1rem;
        border-radius: 18px;
        border: none;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.35);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 18px 45px rgba(0, 198, 255, 0.5);
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# دالة تسليم وحفظ بيانات البريد الإلكتروني في ملف Leads
LEADS_FILE = "registered_leads.csv"

def save_lead(name, email):
    file_exists = os.path.isfile(LEADS_FILE)
    with open(LEADS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Email"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email])

# تهيئة جلسة المستخدم (Session State)
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None
if "user_credits" not in st.session_state:
    st.session_state["user_credits"] = 5

# ---------------------------------------------------------
# 🔑 بوابة تسجيل الدخول بالبريد الإلكتروني (Email Gate)
# ---------------------------------------------------------
if not st.session_state["user_email"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
        <div class="auth-title">⚡ مرحبا بك في استوديو LUMINA AI</div>
        <p style="color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;">
            منصة الذكاء الاصطناعي الأولى لإنتاج القصص والفيديوهات السينمائية بالأصوات البشرية. يرجى إدخال بريدك الإلكتروني للبدء مجاناً.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        input_name = st.text_input("👤 الاسم الكامل / Name:", placeholder="مثال: أحمد علي")
        input_email = st.text_input("📧 البريد الإلكتروني / Gmail:", placeholder="example@gmail.com")
        
        if st.button("🔓 الدخول وفتح الاستوديو مجاناً (5 Credits)"):
            if not input_email.strip() or "@" not in input_email or "." not in input_email:
                st.error("⚠️ يرجى إدخال بريد إلكتروني صحيح (Gmail/Email) للتفعيل!")
            else:
                save_lead(input_name, input_email)
                st.session_state["user_email"] = input_email
                st.session_state["user_name"] = input_name if input_name else "المستخدم"
                st.success("تم تسجيل الدخول بنجاح! جاري تحويلك للوحة التحكم...")
                st.rerun()
    st.stop()  # حظر بقية الكود حتى يسجل الدخول

# ---------------------------------------------------------
# 🌟 واجهة التطبيق الرئيسية بعد تسجيل الدخول
# ---------------------------------------------------------

# الشريط العلوي مع معلومات المستخدم ورصيده
st.markdown(f"""
<div class="app-header">
    <div class="app-brand">⚡ LUMINA & DAVINCI <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 400;">ULTRA STUDIO</span></div>
    <div>
        <span class="badge-user">👤 {st.session_state['user_name']} ({st.session_state['user_email']})</span>
        <span class="badge-user" style="margin-right: 8px; color: #00f2fe; border-color: #00f2fe;">💎 الرصيد: {st.session_state['user_credits']} فيديوهات</span>
    </div>
</div>
""", unsafe_allow_html=True)

# زر تسجيل الخروج في Sidebar
if st.sidebar.button("🚪 تسجيل الخروج / تغيير الإيميل"):
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.title("🎛️ إعدادات الصوت والذكاء الاصطناعي")
openai_key = st.sidebar.text_input("🔑 مفتاح OpenAI API (اختر اختياري):", type="password")

st.sidebar.markdown("---")
st.sidebar.subheader("🎙️ اختر صوت الراوي البشري")

VOICE_OPTIONS = {
    "🇸🇦 حمدان - صوت رجالي سعودي فخم": "ar-SA-HamedNeural",
    "🇸🇦 زارية - صوت نسائي سعودي ناعم": "ar-SA-ZariyahNeural",
    "🇪🇬 شاكر - صوت وثائقي مصري متمرس": "ar-EG-ShakirNeural",
    "🇪🇬 سلمى - صوت نسائي مصري احترافي": "ar-EG-SalmaNeural",
    "🇦🇪 حمدان - صوت إماراتي سينمائي": "ar-AE-HamdanNeural",
    "🇸🇾 أماني - صوت شامي/سوري دافئ": "ar-SY-AmanyNeural",
    "🇺🇸 Christopher - US Cinematic Voice": "en-US-ChristopherNeural",
    "🇬🇧 Sonia - UK Professional Voice": "en-GB-SoniaNeural"
}

selected_voice_label = st.sidebar.selectbox("اختر الراوي الصوتي:", list(VOICE_OPTIONS.keys()))
selected_voice_id = VOICE_OPTIONS[selected_voice_label]

speech_rate = st.sidebar.select_slider("⚡ سرعة نطق الصوت:", options=["-20%", "0%", "+15%", "+30%"], value="0%")

st.sidebar.markdown("---")
platform_choice = st.sidebar.selectbox(
    "📐 أبعاد الفيديو المنصة Target:",
    [
        "🎵 TikTok / Reels / Shorts (9:16)",
        "🔴 YouTube HD / Cinema (16:9)",
        "📸 Instagram Feed (1:1)"
    ]
)

if "9:16" in platform_choice: w, h = 1080, 1920
elif "16:9" in platform_choice: w, h = 1920, 1080
else: w, h = 1080, 1080

# دالة التوليد الصوتي المتطور
async def generate_neural_audio_advanced(text, voice, rate_str, output_path):
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    await communicate.save(output_path)

def create_advanced_voice(text, voice_id, rate_str, output_path):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(generate_neural_audio_advanced(text, voice_id, rate_str, output_path))
        return True
    except Exception:
        from gtts import gTTS
        tts = gTTS(text=text, lang='ar')
        tts.save(output_path)
        return True

# دالة كتابة السكريبت
def build_ultra_script(topic, niche, api_key):
    if HAS_OPENAI and api_key:
        try:
            client = openai.OpenAI(api_key=api_key)
            prompt = f"""
            اكتب قصة سينمائية قصيرة ومثيرة جداً في مجال '{niche}' حول الموضوع: '{topic}'.
            القصة تتكون من 4 إلى 5 أسطر فقط.
            السطر الأول يجب أن يكون Hook قاسي ومثير.
            اكتب النصوص مباشرة سطر بسطر بدون أرقام أو رموز.
            """
            res = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=350
            )
            return res.choices[0].message.content.strip()
        except Exception:
            pass
            
    templates = {
        "👻 قصص رعب وغموض": f"في ليلة مظلمة، فتحت الباب القديم للمكان المهجور حول {topic}.\nأصوات همس غريبة كانت تصدر من خلف الجدران المغلقة.\nخطوات خفية تقترب بسرعة نحو المكان الذي أقف فيه.\nاكتشفت الحقيقة المرعبة التي حاول الجميع إخفاءها!",
        "🏛️ وثائقيات تاريخية": f"قبل آلاف السنين، أقيمت واحدة من أعظم الحضارات في تاريخ {topic}.\nأسرار وهندسة معمارية حيرت أدمغة علماء العصر الحديث.\nحروب ومعاهدات غيرت مجرى التاريخ البشري للأبد.\nتبقى هذه الأسطورة شاهدة على عظمة الماضي.",
        "💡 تحفيز وتطوير الذات": f"النجاح ليس مصادفة، بل هو رحلة تبدأ بقرار شجاع حول {topic}.\nكل حلم كبير بدأ بفكرة صغيرة وإصرار لا يتزحزح.\nالتحديات هي الصخرة التي تصقل قدراتك الحقيقية.\nاستمر في السعي ولا تتوقف حتى تصل إلى القمة!",
        "💰 مال وأعمال (Money Radar)": f"كيف بنى أثرياء العالم ثرواتهم الضخمة في مجال {topic}؟\nسر صغير يغفله تسعة وتسعون بالمائة من الناس.\nالاستثمار الذكي واغتنام الفرص هما مفتاح الثراء.\nابدأ الآن في بناء امبراطوريتك المالية الخاصة!"
    }
    return templates.get(niche, f"قصة سينمائية مشوقة ومثيرة حول {topic}.\nأحداث مفاجئة تتسارع بمرور الوقت.\nاكتشف السر العجيب المخبأ بين المشاهد.\nتجربة فريدة تجعلك تتطلع للمزيد!")

# دالة توليد صور AI بأنماط متعددة (Pollinations Engine)
def generate_styled_ai_image(prompt_text, style_name, width, height, seed):
    styles_dict = {
        "🎬 Cinematic Realism": "cinematic photorealistic, 8k resolution, highly detailed, dramatic lighting",
        "🔮 Cyberpunk & Sci-Fi": "cyberpunk style, neon lights, futuristic, 8k digital art",
        "🎨 Pixar / 3D Render": "3d pixar style, cute animated character, vibrant colors, unreal engine 5 render",
        "📜 Historical Painting": "oil painting masterpiece, classical historical art style, rich detail"
    }
    style_prompt = styles_dict.get(style_name, "cinematic photorealistic")
    full_prompt = urllib.parse.quote(f"{style_prompt}, {prompt_text}")
    
    ai_url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={width}&height={height}&seed={seed}&nologo=true"
    try:
        res = requests.get(ai_url, timeout=7)
        if res.status_code == 200:
            img = Image.open(io.BytesIO(res.content)).convert('RGB')
            return ImageEnhance.Color(img).enhance(1.2)
    except Exception:
        pass
        
    # Fallback
    try:
        res = requests.get(f"https://picsum.photos/{width}/{height}?random={seed + 500}", timeout=4)
        if res.status_code == 200:
            return Image.open(io.BytesIO(res.content)).convert('RGB')
    except Exception:
        pass

    img = Image.new('RGB', (width, height), color=(8, 12, 25))
    return img

# دالة طباعة النصوص السينمائية مع دعم الألوان المتعددة
def render_custom_subtitles(text, text_color_rgb, width=1080, height=1920):
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    lines = textwrap.wrap(text, width=22 if width < height else 44)
    wrapped = "\n".join(lines)
    
    reshaped = arabic_reshaper.reshape(wrapped)
    display_text = get_display(reshaped)

    font_size = int(height * 0.038)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()

    cx, cy = width // 2, int(height * 0.79)
    bbox = draw.multiline_textbbox((cx, cy), display_text, font=font, anchor="mm", align="center")
    pad_x, pad_y = int(width * 0.04), int(height * 0.02)
    
    # مربع النص الشفاف
    draw.rounded_rectangle(
        [bbox[0]-pad_x, bbox[1]-pad_y, bbox[2]+pad_x, bbox[3]+pad_y],
        radius=16,
        fill=(5, 8, 18, 230),
        outline=text_color_rgb,
        width=2
    )
    
    draw.multiline_text((cx, cy), display_text, font=font, fill=text_color_rgb + (255,), anchor="mm", align="center")
    return np.array(img)

# محرر خيارات الفيديو
col1, col2 = st.columns([2, 1])

with col1:
    user_topic = st.text_input("💡 أدخل فكرة الفيديو أو القصة السينمائية:", "رحلة أول رائد فضاء يستكشف ثقباً أسود")
    selected_niche = st.selectbox(
        "📚 تصنيف القصة (Niche):",
        ["🏛️ وثائقيات تاريخية", "👻 قصص رعب وغموض", "💡 تحفيز وتطوير الذات", "💰 مال وأعمال (Money Radar)"]
    )

with col2:
    visual_style = st.selectbox(
        "🎨 نمط الصور الذكية (AI Style):",
        ["🎬 Cinematic Realism", "🔮 Cyberpunk & Sci-Fi", "🎨 Pixar / 3D Render", "📜 Historical Painting"]
    )
    camera_style = st.selectbox("🎥 حركة الكاميرا:", ["Smooth Zoom In", "Zoom Out", "ثابت"])

st.markdown("---")

if st.button("🚀 توليد وتصدير الفيديو السينمائي الفائق"):
    if st.session_state["user_credits"] <= 0:
        st.error("⚠️ نفد رصيدك المجاني من الفيديوهات! تواصل مع الإدارة للحصول على المزيد.")
    elif not user_topic.strip():
        st.error("يرجى كتابة موضوع القصة أولاً!")
    else:
        status_box = st.empty()
        pbar = st.progress(0)
        
        try:
            status_box.markdown("**🧠 Phase 1: صياغة السكريبت والقصة بواسطة ChatGPT الذكي...**")
            script = build_ultra_script(user_topic, selected_niche, openai_key)
            lines = [l.strip() for l in script.split("\n") if l.strip()][:5]
            
            sub_clips = []
            audio_clips = []
            temp_files = []
            total = len(lines)
            
            for i, line in enumerate(lines):
                status_box.markdown(f"**🎨 Phase 2: إنشاء صورة AI سينمائية + الصوت البشري للمشهد ({i+1}/{total})...**")
                
                # الصوت البشري
                aud_file = f"voice_pro_{i}.mp3"
                create_advanced_voice(line, selected_voice_id, speech_rate, aud_file)
                temp_files.append(aud_file)
                
                aclip = AudioFileClip(aud_file)
                dur = aclip.duration
                audio_clips.append(aclip)

                # صورة AI بحسب الاستايل المحدد
                bg_img = generate_styled_ai_image(f"{user_topic}, {line}", visual_style, w, h, i * 77)
                bg_clip = ImageClip(np.array(bg_img)).set_duration(dur)
                
                if camera_style == "Smooth Zoom In":
                    bg_clip = bg_clip.resize(lambda t: 1 + 0.04 * (t / dur))
                elif camera_style == "Zoom Out":
                    bg_clip = bg_clip.resize(lambda t: 1.1 - 0.04 * (t / dur))

                # كتابة النص المنسق
                sub_np = render_custom_subtitles(line, (212, 175, 55), width=w, height=h)
                sub_clip = ImageClip(sub_np).set_duration(dur)

                # الدمج
                scene = CompositeVideoClip([bg_clip, sub_clip]).set_audio(aclip)
                sub_clips.append(scene)
                
                pbar.progress(int(((i + 1) / total) * 85))

            status_box.markdown("**⚡ Phase 3: تجميع مقاطع المشاهد والتصدير النهائي...**")
            final_v = concatenate_videoclips(sub_clips)
            
            out_file = "lumina_ultra_v5.mp4"
            final_v.write_videofile(out_file, fps=24, codec='libx264', audio_codec='aac')
            
            # خصم نقطة من رصيد المستخدم
            st.session_state["user_credits"] -= 1
            
            pbar.progress(100)
            status_box.empty()
            
            for c in audio_clips: c.close()
            for f in temp_files:
                if os.path.exists(f): os.remove(f)

            st.balloons()
            st.success("🎉 تم توليد الفيديو السينمائي بنجاح!")
            st.video(out_file)

        except Exception as e:
            st.error(f"حدث خطأ أثناء معالجة الفيديو: {str(e)}")
