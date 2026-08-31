import streamlit as st
import config
import ai_engine

# إعداد الصفحة
st.set_page_config(
    page_title="Lumina AI Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# إدارة حالة اللغة والجلوس
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'

if 'gallery_images' not in st.session_state:
    st.session_state.gallery_images = [
        {"title": "مدينة المستقبل", "url": "https://image.pollinations.ai/prompt/cyberpunk%20futuristic%20city%20neon%20lights?width=600&height=400"},
        {"title": "فارس عربي", "url": "https://image.pollinations.ai/prompt/ancient%20arabian%20warrior%20cinematic%20lighting?width=600&height=400"},
        {"title": "رائد فضاء", "url": "https://image.pollinations.ai/prompt/astronaut%20discovering%20alien%20planet?width=600&height=400"}
    ]

# قائمة الإعدادات واللغة
with st.sidebar:
    st.title("⚙️ الإعدادات / Settings")
    selected_lang = st.selectbox("اختر اللغة / Select Language", ["العربية", "English"])
    st.session_state.lang = 'ar' if selected_lang == "العربية" else 'en'

t = config.TRANSLATIONS[st.session_state.lang]

# تحسين التصميم ومنع تداخل النصوص في الهواتف
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    html, body, div, span, h1, h2, h3, p {
        font-family: 'Cairo', sans-serif !important;
    }
    
    /* تصميم الهيدر الاحترافي */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }
    .hero-title {
        color: #00f2fe;
        font-size: 24px;
        font-weight: 900;
        margin: 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 13px;
        margin-top: 5px;
    }

    /* تحسين زر التوليد */
    .stButton > button {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# واجهة الرأس
st.markdown(f"""
<div class="hero-card">
    <div class="hero-title">⚡ {t["title"]}</div>
    <div class="hero-sub">{t["subtitle"]}</div>
</div>
""", unsafe_allow_html=True)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_chat"], 
    t["tab_studio"], 
    t["tab_images"], 
    t["tab_gallery"]
])

# 1️⃣ الشات الذكي (ChatGPT)
with tab1:
    st.subheader(t["tab_chat"])
    user_prompt = st.text_area(t["prompt_label"], height=100, placeholder="اكتب سؤالك أو اطلب كوداً وسيناريو...")
    if st.button(t["generate_btn"], key="chat_btn"):
        if user_prompt.strip():
            with st.spinner("جاري التوليد..."):
                res = ai_engine.generate_ai_text(user_prompt, st.session_state.lang)
                st.info(res)
        else:
            st.warning("يرجى إدخال نص أولاً!")

# 2️⃣ استوديو الفيديوهات
with tab2:
    st.subheader(t["tab_studio"])
    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(t["aspect_ratio"], ["9:16 (TikTok/Reels)", "16:9 (YouTube)"])
    with col2:
        st.selectbox(t["voice_label"], ["شاكر - وثائقي", "سلمى - حماسي"])
    st.button(t["render_btn"], key="vid_btn")

# 3️⃣ مولد الصور
with tab3:
    st.subheader(t["tab_images"])
    img_prompt = st.text_input(t["image_prompt"], placeholder="A futuristic lion warrior, cinematic, 8k")
    if st.button(t["generate_img_btn"], key="img_btn"):
        if img_prompt.strip():
            with st.spinner("جاري الرسم..."):
                img_url = ai_engine.generate_ai_image_url(img_prompt)
                st.image(img_url, caption=img_prompt, use_container_width=True)
                st.session_state.gallery_images.insert(0, {"title": img_prompt[:25], "url": img_url})
                st.success("تم التوليد وإضافة الصورة لمعرض الأعمال!")
        else:
            st.warning("يرجى إدخال وصف للصورة!")

# 4️⃣ معرض أعمال الزوار (تم إصلاح خطأ use_container_width هنا)
with tab4:
    st.subheader(t["gallery_title"])
    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.gallery_images):
        with cols[idx % 3]:
            if isinstance(item, dict) and "url" in item:
                st.image(item["url"], caption=item.get("title", ""), use_container_width=True)
