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

# 🛠️ إصلاح مشكلة Pillow/ANTIALIAS لضمان عدم حدوث أي أخطاء
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from moviepy.editor import ImageClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips
import arabic_reshaper
from bidi.algorithm import get_display

# فحص المكتبات الخارجية
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

# 1. إعدادات الصفحة والأنماط البصرية الراقية
st.set_page_config(
    page_title="Lumina AI Studio | Ultimate All-In-One Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تصميم SaaS المظلم والفخم جداً
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
        margin-bottom: 20px;
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

    /* Auth Login Box */
    .auth-card {
        max-width: 520px;
        margin: 50px auto;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 27, 75, 0.85) 100%);
        border: 2px solid rgba(212, 175, 55, 0.4);
        border-radius: 28px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 25px 60px rgba(0, 0, 0, 0.95), 0 0 40px rgba(212, 175, 55, 0.2);
    }

    /* Primary SaaS Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #d4af37, #f39c12, #00c6ff, #a855f7);
        color: #000000;
        font-size: 1.25rem;
        font-weight: 900;
        padding: 0.9rem;
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 30px rgba(212, 175, 55, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px) scale(1.005);
        box-shadow: 0 15px 40px rgba(0, 198, 255, 0.5);
        color: #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# ملف حفظ إيميلات الزوار
LEADS_FILE = "registered_leads.csv"

def save_lead(name, email):
    file_exists = os.path.isfile(LEADS_FILE)
    with open(LEADS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Name", "Email"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email])

# تهيئة الجلسة
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

# بوابة تسجيل دخول الزوار بالبريد الإلكتروني
if not st.session_state["user_email"]:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="auth-card">
        <h1 style="color: #fff; margin-bottom: 10px;">⚡ مرحباً بك في منصة LUMINA AI</h1>
        <p style="color: #94a3b8; font-size: 1.05rem; margin-bottom: 25px;">
            الاستوديو الشامل لتوليد الصور الاحترافية، الأصوات العربية المتنوعة، الفيديوهات السينمائية والسكريبتات بالذكاء الاصطناعي.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        input_name = st.text_input("👤 الاسم الكامل / Name:", placeholder="مثال: محمد علي")
        input_email = st.text_input("📧 البريد الإلكتروني / Email:", placeholder="example@gmail.com")
        
        if st.button("🔓 دخول وفتح استوديو الذكاء الاصطناعي مجاناً"):
            if not input_email.strip() or "@" not in input_email or "." not in input_email:
                st.error("⚠️ يرجى إدخال بريد إلكتروني صحيح للتفعيل!")
            else:
                save_lead(input_name, input_email)
                st.session_state["user_email"] = input_email
                st.session_state["user_name"] = input_name if input_name else "زائر زكي"
                st.rerun()
    st.stop()

# الهيدر العلوي
st.markdown(f"""
<div class="app-header">
    <div class="app-brand">⚡ LUMINA AI <span style="font-size: 0.95rem; color: #94a3b8; font-weight: 400;">ALL-IN-ONE STUDIO V6.0</span></div>
    <div>
        <span class="badge-user">👤 {st.session_state['user_name']} ({st.session_state['user_email']})</span>
    </div>
</div>
""", unsafe_allow_html=True)

# قائمة الأصوات العربية المتنوعة الضخمة
ARABIC_VOICES = {
    "👨‍💼 رجل سعودي - صوت فخم ورصين": "ar-SA-HamedNeural",
    "👩‍💼 امرأة سعودية - صوت احترافي دافئ": "ar-SA-ZariyahNeural",
    "🎙️ رجل مصري - وثائقي وغموض": "ar-EG-ShakirNeural",
    "👩 امرأة مصرية - إخباري وسريع": "ar-EG-SalmaNeural",
    "🇦🇪 رجل إماراتي - هادئ وسينمائي": "ar-AE-HamdanNeural",
    "👧 فتاة شابة / طفلة (شامي) - ناعم ولطيف": "ar-SY-AmanyNeural",
    "👦 طفل / صوت شاب كويتي - حماسي": "ar-KW-FahedNeural",
    "👩‍🦰 امرأة أردنية - صوت إذاعي ناعم": "ar-JO-SanaNeural",
    "👨 رجل مغربي - عميق ومميز": "ar-MA-JamalNeural",
    "🇺🇸 Christopher - US Male Voice": "en-US-ChristopherNeural",
    "🇬🇧 Sonia - UK Female Voice": "en-GB-SoniaNeural"
}

# تسجيل الخروج
if st.sidebar.button("🚪 تسجيل الخروج / تغيير الإيميل"):
    st.session_state["user_email"] = None
    st.rerun()

st.sidebar.markdown("---")
openai_key = st.sidebar.text_input("🔑 مفتاح OpenAI API (اختياري):", type="password")

# ---------------------------------------------------------
# 🌟 التبويبات الرئيسية لاستوديوهات الذكاء الاصطناعي
# ---------------------------------------------------------
tab_video, tab_image, tab_voice, tab_script = st.tabs([
    "🎬 صانع الفيديوهات (AI Video)", 
    "🎨 مولد الصور (AI Images)", 
    "🎙️ الأوصاف والأصوات (AI Voice)", 
    "✍️ السكريبتات والوصف (AI Script & SEO)"
])

# ---------------------------------------------------------
# TAB 1: استوديو توليد الفيديوهات
# ---------------------------------------------------------
with tab_video:
    st.subheader("🎬 استوديو إنتاج الفيديوهات السينمائية المتكامل")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        v_topic = st.text_input("💡 فكرة الفيديو أو القصة:", "سر الأهرامات المفقودة تحت المحيط")
        v_niche = st.selectbox(
            "📚 المجال (Niche):",
            ["🏛️ وثائقيات تاريخية", "👻 قصص رعب وغموض", "💡 تحفيز وتطوير الذات", "💰 مال وأعمال", "🧸 حكايات أطفال"]
        )
    
    with col2:
        v_voice_label = st.selectbox("🎙️ صوت الراوي للفيديو:", list(ARABIC_VOICES.keys()), key="v_voice")
        v_voice_id = ARABIC_VOICES[v_voice_label]
        v_ratio = st.selectbox("📐 أبعاد الفيديو:", ["🎵 TikTok / Shorts (9:16)", "🔴 YouTube HD (16:9)", "📸 Instagram (1:1)"])

    if "9:16" in v_ratio: vw, vh = 1080, 1920
    elif "16:9" in v_ratio: vw, vh = 1920, 1080
    else: vw, vh = 1080, 1080

    if st.button("🚀 إنشاء وتوليد الفيديو السينمائي"):
        if not v_topic.strip():
            st.error("يرجى كتابة فكرة الفيديو أولاً!")
        else:
            status_box = st.empty()
            pbar = st.progress(0)
            try:
                status_box.markdown("**🧠 Phase 1: جاري كتابة السكريبت...**")
                # نص سكريبت مبسط
                lines = [
                    f"في أعماق هذا العالم، يختبئ سر عجيب حول {v_topic}.",
                    "حقائق شائقة لم يتم كشفها من قبل للعلن.",
                    "التفاصيل المفاجئة التي حيرت عقول الخبراء والباحثين.",
                    "استعد لاستكشاف الحقيقة الكاملة في هذا الفيديو الفريد!"
                ]
                
                sub_clips = []
                audio_clips = []
                temp_files = []
                
                for i, line in enumerate(lines):
                    status_box.markdown(f"**🎨 Phase 2: إنشاء صورة AI + صوت الراوي للمشهد ({i+1}/{len(lines)})...**")
                    
                    # الصوت
                    aud_file = f"v_audio_{i}.mp3"
                    asyncio.run(edge_tts.Communicate(line, v_voice_id).save(aud_file)) if HAS_EDGE_TTS else None
                    temp_files.append(aud_file)
                    
                    aclip = AudioFileClip(aud_file)
                    dur = aclip.duration
                    audio_clips.append(aclip)

                    # صورة AI
                    prompt_enc = urllib.parse.quote(f"cinematic photo, 8k, photorealistic, {v_topic}, scene {i}")
                    img_url = f"https://image.pollinations.ai/prompt/{prompt_enc}?width={vw}&height={vh}&seed={i*88}&nologo=true"
                    
                    try:
                        res = requests.get(img_url, timeout=6)
                        img_obj = Image.open(io.BytesIO(res.content)).convert('RGB')
                    except Exception:
                        img_obj = Image.new('RGB', (vw, vh), color=(10, 15, 30))

                    bg_clip = ImageClip(np.array(img_obj)).set_duration(dur).resize(lambda t: 1 + 0.03 * (t / dur))

                    # كتابة النص
                    txt_img = Image.new('RGBA', (vw, vh), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(txt_img)
                    reshaped = arabic_reshaper.reshape(line)
                    disp_text = get_display(reshaped)
                    
                    font_size = int(vh * 0.038)
                    try: font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                    except Exception: font = ImageFont.load_default()
                    
                    cx, cy = vw // 2, int(vh * 0.78)
                    bbox = draw.multiline_textbbox((cx, cy), disp_text, font=font, anchor="mm", align="center")
                    draw.rounded_rectangle([bbox[0]-20, bbox[1]-10, bbox[2]+20, bbox[3]+10], radius=14, fill=(5, 8, 18, 220), outline=(212, 175, 55, 180), width=2)
                    draw.multiline_text((cx, cy), disp_text, font=font, fill=(255, 235, 59, 255), anchor="mm", align="center")

                    sub_clip = ImageClip(np.array(txt_img)).set_duration(dur)
                    scene = CompositeVideoClip([bg_clip, sub_clip]).set_audio(aclip)
                    sub_clips.append(scene)
                    pbar.progress(int(((i + 1) / len(lines)) * 85))

                status_box.markdown("**⚡ Phase 3: تجميع المقطع وتصدير الفيديو...**")
                final_v = concatenate_videoclips(sub_clips)
                out_v = "final_generated_video.mp4"
                final_v.write_videofile(out_v, fps=24, codec='libx264', audio_codec='aac')
                
                pbar.progress(100)
                status_box.empty()
                st.balloons()
                st.success("🎉 تم إنتاج الفيديو بنجاح!")
                st.video(out_v)

                for c in audio_clips: c.close()
                for f in temp_files: 
                    if os.path.exists(f): os.remove(f)

            except Exception as e:
                st.error(f"حدث خطأ أثناء معالجة الفيديو: {str(e)}")

# ---------------------------------------------------------
# TAB 2: استوديو توليد الصور بالذكاء الاصطناعي
# ---------------------------------------------------------
with tab_image:
    st.subheader("🎨 استوديو توليد الصور الفائقة الدقة (AI Image Studio)")
    img_col1, img_col2 = st.columns([2, 1])
    
    with img_col1:
        img_prompt = st.text_area("✍️ وصف الصورة التي تتخيلها (Prompt):", "قصر ذهبي ساحر فوق السحاب في وقت الغروب مع تنين أسطوري")
    
    with img_col2:
        img_style = st.selectbox("🎨 نمط الصورة (Style):", [
            "🎬 Cinematic Photorealistic (واقعي سينمائي)", 
            "🎨 3D Pixar Animation (أنيميشن كرتون)", 
            "🔮 Cyberpunk Neon (مستقبلي نيون)", 
            "📜 Oil Painting (لوحة زيتية كلاسيكية)"
        ])
        img_dim = st.selectbox("📐 أبعاد الصورة:", ["Square 1:1 (1024x1024)", "Portrait 9:16 (720x1280)", "Landscape 16:9 (1280x720)"])

    if "1:1" in img_dim: iw, ih = 1024, 1024
    elif "9:16" in img_dim: iw, ih = 720, 1280
    else: iw, ih = 1280, 720

    if st.button("✨ توليد الصورة الآن بالذكاء الاصطناعي"):
        if not img_prompt.strip():
            st.error("يرجى كتابة وصف الصورة أولاً!")
        else:
            with st.spinner("🎨 جاري رسم وتوليد الصورة بدقة عالية..."):
                full_p = f"{img_style}, {img_prompt}, highly detailed, 8k resolution"
                enc_p = urllib.parse.quote(full_p)
                ai_img_url = f"https://image.pollinations.ai/prompt/{enc_p}?width={iw}&height={ih}&seed={np.random.randint(1000, 99999)}&nologo=true"
                
                try:
                    res = requests.get(ai_img_url, timeout=10)
                    if res.status_code == 200:
                        gen_img = Image.open(io.BytesIO(res.content))
                        st.image(gen_img, caption="الصورة المولدة بالذكاء الاصطناعي", use_column_width=True)
                        
                        # زر تحميل الصورة
                        buf = io.BytesIO()
                        gen_img.save(buf, format="PNG")
                        st.download_button(
                            label="📥 تنزيل الصورة بجودة عالية (PNG)",
                            data=buf.getvalue(),
                            file_name="lumina_ai_image.png",
                            mime="image/png"
                        )
                except Exception as e:
                    st.error(f"تعذر توليد الصورة: {str(e)}")

# ---------------------------------------------------------
# TAB 3: استوديو الأصوات والأوصاف الصوتية
# ---------------------------------------------------------
with tab_voice:
    st.subheader("🎙️ استوديو توليد الأصوات العربية والبشرية (Text To Speech)")
    v_text = st.text_area("أدخل النص المراد تحويله إلى صوت بشري احترافي:", "مرحباً بكم في منصة لومينا للذكاء الاصطناعي. يمكنكم الآن إنشاء أجمل الأصوات والفيديوهات بضغطة زر واحدة!")
    
    col_v1, col_v2 = st.columns(2)
    with col_v1:
        voice_choice_label = st.selectbox("اختر صوت الراوي المطلوب:", list(ARABIC_VOICES.keys()))
        voice_choice_id = ARABIC_VOICES[voice_choice_label]
    
    with col_v2:
        voice_speed = st.select_slider("⚡ سرعة الصوت:", options=["-20%", "0%", "+20%"], value="0%")

    if st.button("🔊 تحويل النص إلى صوت بشري"):
        if not v_text.strip():
            st.error("يرجى كتابة النص أولاً!")
        else:
            with st.spinner("🎙️ جاري توليد وتدقيق الصوت البشري..."):
                out_audio = "generated_voice.mp3"
                try:
                    asyncio.run(edge_tts.Communicate(v_text, voice_choice_id, rate=voice_speed).save(out_audio))
                    st.audio(out_audio)
                    
                    with open(out_audio, "rb") as f:
                        st.download_button(
                            label="📥 تحميل الملف الصوتي (MP3)",
                            data=f,
                            file_name="lumina_speech.mp3",
                            mime="audio/mp3"
                        )
                except Exception as e:
                    st.error(f"خطأ في توليد الصوت: {str(e)}")

# ---------------------------------------------------------
# TAB 4: استوديو السكريبتات والأوصاف (SEO Generator)
# ---------------------------------------------------------
with tab_script:
    st.subheader("✍️ مولد الأوصاف والسكريبتات وعناوين الـ Viral")
    sc_topic = st.text_input("أدخل موضوع المقطع أو الفيديو:", "كيف تبني مشروعك الخاص بالذكاء الاصطناعي في 2026")
    sc_target = st.selectbox("نوع المحتوى المطلوب:", ["وصف كامل مع هاشتاقات لـ TikTok & Reels", "سكريبت مقطع قصير (Hook + Story)", "عناوين جذابة للضغط (Viral Titles)"])
    
    if st.button("🧠 توليد الأوصاف والسكريبت بالذكاء الاصطناعي"):
        if not sc_topic.strip():
            st.error("أدخل موضوعاً أولاً!")
        else:
            with st.spinner("جاري التوليد والتحليل..."):
                if HAS_OPENAI and openai_key:
                    try:
                        client = openai.OpenAI(api_key=openai_key)
                        res = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[{"role": "user", "content": f"اكتب {sc_target} حول الموضوع: {sc_topic} بأسلوب جذاب جداً وجديد."}]
                        )
                        result_text = res.choices[0].message.content
                    except Exception:
                        result_text = None
                else:
                    result_text = None

                if not result_text:
                    result_text = f"""🔥 **{sc_target} المولد الذكي:**

📌 **العنوان الجذاب:** {sc_topic} - السر الذي لا يريد أحد أن تعرفه!

📝 **الوصف:**
هل تساءلت يوماً عن أسرار {sc_topic}؟ في هذا المقطع السريع نكتشف معاً أهم الخطوات والحلول الذكية التي تهمك! شاهد الفيديو للنهاية ولاتنسى المتابعة والإعجاب للحصول على المزيد.

🏷️ **الهاشتاقات الأكثر انتشاراً:**
#{sc_topic.replace(' ', '_')} #ذكاء_اصطناعي #تطوير_الذات #Viral #Explore #Reels #TikTok
"""
                st.text_area("المخرجات الاحترافية (جاهزة للنسخ):", value=result_text, height=280)
