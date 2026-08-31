import streamlit as st
import config
import ai_engine

# إعدادات الصفحة
st.set_page_config(
    page_title="LUMINA AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'

if 'gallery_images' not in st.session_state:
    st.session_state.gallery_images = [
        {"title": "سيارة مستقبليّة", "url": "https://image.pollinations.ai/prompt/futuristic%20concept%20car%20neon%20lights%208k?width=600&height=400"},
        {"title": "مدينة ذكية", "url": "https://image.pollinations.ai/prompt/futuristic%20smart%20city%20sunset?width=600&height=400"}
    ]

# القائمة الجانبية
with st.sidebar:
    st.title("⚙️ الإعدادات")
    selected_lang = st.selectbox("اختر اللغة / Language", ["العربية", "English"])
    st.session_state.lang = 'ar' if selected_lang == "العربية" else 'en'

t = config.TRANSLATIONS[st.session_state.lang]

# تحسين التصميم للشاشات الصغيرة
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    * {
        font-family: 'Cairo', sans-serif !important;
    }
    
    /* إخفاء القوائم العلوية المزعجة */
    #MainMenu, footer, header { visibility: hidden; }
    
    .app-header {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .app-title {
        color: #00f2fe;
        font-size: 22px;
        font-weight: 900;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000 !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
        border: none !important;
        width: 100%;
        padding: 12px !important;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# الهيدر الرئيسي
st.markdown(f"""
<div class="app-header">
    <div class="app-title">⚡ {t["title"]}</div>
    <div style="color: #94a3b8; font-size: 12px;">{t["subtitle"]}</div>
</div>
""", unsafe_allow_html=True)

# التبويبات
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_chat"], 
    t["tab_studio"], 
    t["tab_images"], 
    t["tab_gallery"]
])

# 1️⃣ شات الذكاء الاصطناعي
with tab1:
    st.subheader(t["tab_chat"])
    user_prompt = st.text_area(t["prompt_label"], height=100, placeholder="اكتب سؤالك هنا...")
    if st.button(t["generate_btn"], key="chat_btn"):
        if user_prompt.strip():
            with st.spinner("جاري التفكير..."):
                res = ai_engine.generate_ai_text(user_prompt, st.session_state.lang)
                st.info(res)

# 2️⃣ استوديو الفيديوهات
with tab2:
    st.subheader(t["tab_studio"])
    st.selectbox(t["aspect_ratio"], ["9:16 (TikTok/Reels)", "16:9 (YouTube)"])
    st.selectbox(t["voice_label"], ["شاكر - وثائقي", "سلمى - حماسي"])
    st.button(t["render_btn"], key="vid_btn")

# 3️⃣ توليد الصور بالذكاء الاصطناعي (محدث ومترجم)
with tab3:
    st.subheader(t["tab_images"])
    img_prompt = st.text_input(t["image_prompt"], placeholder="مثال: اريد سيارة خيالية سريعة")
    
    if st.button(t["generate_img_btn"], key="img_btn"):
        if img_prompt.strip():
            with st.spinner("جاري ترجمة الوصف ورسم الصورة بالضبط..."):
                img_url = ai_engine.generate_ai_image_url(img_prompt)
                st.image(img_url, caption=f"🎨 النتيجة لـ: {img_prompt}", use_container_width=True)
                st.session_state.gallery_images.insert(0, {"title": img_prompt, "url": img_url})
                st.success("تم التوليد بنجاح وصورة السيارة جاهزة!")
        else:
            st.warning("يرجى كتابة وصف للصورة!")

# 4️⃣ معرض الأعمال
with tab4:
    st.subheader(t["gallery_title"])
    for item in st.session_state.gallery_images:
        st.image(item["url"], caption=item["title"], use_container_width=True)
