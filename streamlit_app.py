import streamlit as st
import requests
import json

# 1. إعدادات الصفحة الهيكلية
st.set_page_config(
    page_title="Lumina AI - Video Creator Studio V12",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. تصميم الواجهة بالثيم الداكن الاحترافي (Dark Theme CSS)
st.markdown("""
<style>
    /* خلفية التطبيق */
    .stApp {
        background-color: #0b0f19;
        color: #f0f4f8;
    }
    
    /* تخصيص القائمة الجانبية */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    
    /* تحسين شكل التبويبات Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: #111827;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #1f2937;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #9ca3af;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important;
        color: #ffffff !important;
    }
    
    /* تصميم البطاقات المخصصة */
    .feature-card {
        background: #1f2937;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #374151;
        margin-bottom: 15px;
    }

    /* الأزرار الرئيسية */
    .stButton > button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        padding: 12px 24px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. الشريط الجانبي (Sidebar Navigation & Global Settings)
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/video-playlist.png", width=60)
    st.title("Lumina Studio V12")
    st.caption("المنصة الاحترافية لتوليد الفيديوهات بالذكاء الاصطناعي")
    st.markdown("---")
    
    st.subheader("⚙️ إعدادات المشروع العامة")
    project_title = st.text_input("اسم المشروع", value="فيديو_جديد_01")
    
    # اختيار الجودة والسرعة
    output_quality = st.selectbox(
        "جودة الفيديو (Output Resolution)",
        options=["1080p (Full HD)", "4K (Ultra HD)", "720p (Fast Render)"],
        index=0
    )
    
    fps_choice = st.radio("معدل إطارات السرعة (FPS)", options=[30, 60], horizontal=True)
    
    st.markdown("---")
    st.info("💡 يتم معالجة الفيديوهات عبر خادم FastAPI المسرّع ببطاقات الرسم البياني GPU.")

# ---------------------------------------------------------
# 4. الواجهة الرئيسية للتبويبات (Main Tabs)
# ---------------------------------------------------------
st.title("🎬 محرر الفيديوهات الذكي")
st.write("قم بضبط الخصائص، رفع المشاهد، وتوليد فيديو عالي الدقة بمقاسات متعددة.")

tab1, tab2, tab3, tab4 = st.tabs([
    "📐 1. الأبعاد والتصميم", 
    "🎞️ 2. المشاهد والمحتوى", 
    "🎙️ 3. الصوت والموسيقى", 
    "🚀 4. المعاينة والرندر"
])

# ---------------------------------------------------------
# التبويب الأول: الأبعاد والتصميم (Aspect Ratio & Text Styling)
# ---------------------------------------------------------
with tab1:
    st.subheader("1️⃣ تحديد المقاس واستايل النصوص")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📐 مقاس الفيديو (Aspect Ratio)")
        aspect_ratio = st.selectbox(
            "اختر المنصة المستهدفة:",
            options=[
                "9:16 (TikTok / Reels / Shorts - عمودي)",
                "16:9 (YouTube / TV - أفقي)",
                "1:1 (Instagram Post - مربع)",
                "4:5 (Facebook Feed - عمودي قصير)"
            ]
        )
        
        st.markdown("### 🎨 موضع وطريقة عرض النص")
        text_position = st.selectbox("موقع الكلمات على الشاشة", ["أسفل الشاشة (Bottom)", "منتصف الشاشة (Center)", "أعلى الشاشة (Top)"])
        animation_style = st.selectbox("حركة ظهور الكلمات", ["كلمة بكلمة (Word-by-Word Highlight)", "ظهور تدريجي (Fade In)", "آلة كاتبة (Typewriter)", "ثابت (Static)"])

    with col2:
        st.markdown("### 🔤 تخصيص الخط والألوان")
        font_family = st.selectbox("نوع الخط العربي", ["Cairo-Bold", "Tajawal-Black", "Almarai-Bold", "Amiri-Regular"])
        font_size = st.slider("حجم الخط", min_value=24, max_value=80, value=48)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            text_color = st.color_picker("لون النص", "#FFFFFF")
        with c2:
            highlight_color = st.color_picker("لون التمييز", "#FFD700")
        with c3:
            stroke_color = st.color_picker("حد الكلمات", "#000000")

# ---------------------------------------------------------
# التبويب الثاني: المشاهد والمحتوى (Scenes Management)
# ---------------------------------------------------------
with tab2:
    st.subheader("2️⃣ إضافة وتنظيم المشاهد")
    
    num_scenes = st.number_input("عدد مشاهد الفيديو:", min_value=1, max_value=10, value=3, step=1)
    
    scenes_data = []
    
    for i in range(int(num_scenes)):
        st.markdown(f"---")
        st.markdown(f"#### 🎬 المشهد رقم {i+1}")
        col_img, col_txt = st.columns([1, 2])
        
        with col_img:
            media_type = st.radio(f"نوع الملف (مشهد {i+1})", ["صورة", "فيديو قصيرة"], key=f"media_type_{i}", horizontal=True)
            uploaded_file = st.file_uploader(f"ارفع {media_type} للمشهد {i+1}", type=["jpg", "png", "mp4"], key=f"file_{i}")
            
        with col_txt:
            scene_text = st.text_area(f"الكلام الخاص بالمشهد {i+1}:", value=f"هذا نص تجريبي ينطق في المشهد رقم {i+1}", key=f"text_{i}")
            scene_duration = st.number_input(f"مدة المشهد بالثواني ({i+1}):", min_value=1.0, max_value=30.0, value=5.0, key=f"dur_{i}")
            
        scenes_data.append({
            "scene_index": i + 1,
            "text": scene_text,
            "duration": scene_duration,
            "file": uploaded_file
        })

# ---------------------------------------------------------
# التبويب الثالث: الصوت والموسيقى (Voiceovers & Music)
# ---------------------------------------------------------
with tab3:
    st.subheader("3️⃣ التحكم في الراوي الصوتي والموسيقى")
    
    col_voice, col_music = st.columns(2)
    
    with col_voice:
        st.markdown("### 🎙️ الصوت الاصطناعي (AI Voice)")
        voice_gender = st.selectbox("الجنس والنبرة:", ["ذكر - حماسي وثائقي", "أنثى - هادئ وإخباري", "ذكر - ودود وسريع"])
        voice_speed = st.slider("سرعة قراءة النص:", min_value=0.75, max_value=1.5, value=1.0, step=0.05)
        pitch_level = st.slider("درجة حدة الصوت (Pitch):", min_value=-5, max_value=5, value=0)

    with col_music:
        st.markdown("### 🎵 الموسيقى الخلفية")
        bg_music = st.file_uploader("ارفع ملف موسيقى خلفية (MP3/WAV)", type=["mp3", "wav"])
        music_volume = st.slider("مستوى صوت الموسيقى الخلفية:", min_value=0.0, max_value=0.5, value=0.15, help="يتم خفض صوت الموسيقى تلقائياً عند نطق المذيع (Ducking)")

# ---------------------------------------------------------
# التبويب الرابع: المعاينة وإرسال أمر الرندر (Preview & Render)
# ---------------------------------------------------------
with tab4:
    st.subheader("4️⃣ ملخص الطلب وبدء استخراج الفيديو")
    
    st.markdown("<div class='feature-card'>", unsafe_allow_html=True)
    st.markdown("#### 📋 مراجعة الإعدادات المطلوبة:")
    st.write(f"- **عنوان المشروع:** {project_title}")
    st.write(f"- **المقاس المختار:** {aspect_ratio}")
    st.write(f"- **عدد المشاهد:** {num_scenes} مشاهد")
    st.write(f"- **جودة الإخراج:** {output_quality} @ {fps_choice}fps")
    st.write(f"- **نوع الخط والموقع:** {font_family} ({text_position})")
    st.markdown("</div>", unsafe_allow_html=True)

    # زر إرسال الطلب إلى خادم FastAPI
    if st.button("🚀 بدء استخراج الفيديو الآن (Start Rendering)"):
        with st.spinner("جاري إرسال البيانات للـ Backend وبدء عملية المعالجة بالذكاء الاصطناعي..."):
            
            # 1. تجميع البيانات للـ JSON Payload
            payload = {
                "title": project_title,
                "aspect_ratio": aspect_ratio.split(" ")[0], # استخراج 9:16 أو 16:9
                "quality": output_quality,
                "fps": fps_choice,
                "font_style": {
                    "font_family": font_family,
                    "font_size": font_size,
                    "primary_color": text_color,
                    "highlight_color": highlight_color,
                    "stroke_color": stroke_color,
                    "position": text_position,
                    "animation": animation_style
                },
                "audio_config": {
                    "voice": voice_gender,
                    "speed": voice_speed,
                    "music_volume": music_volume
                },
                "scenes_count": len(scenes_data)
            }
            
            # 2. محاكاة الاتصال برابط FastAPI Backend (مثال: http://localhost:8000/api/v1/generate-video)
            try:
                # ملاحظة: قم بتفعيل الرابط الحقيقي عند تشغيل سيرفر FastAPI
                # response = requests.post("http://localhost:8000/api/v1/generate-video", json=payload)
                
                st.success("✅ تم إرسال طلب الفيديو بنجاح إلى محرك المعالجة!")
                st.json(payload) # عرض هكيل البيانات لغرض الاختبار
                
                st.info("⌛ جاري تركيب المشاهد بواسطة MoviePy... يمكنك تتبع حالة التقدم من اللوحة.")
                st.progress(65)
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالخادم: {e}")
