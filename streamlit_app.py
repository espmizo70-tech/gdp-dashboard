import streamlit as st
import config
import ai_engine
import requests
import time

# إعدادات الصفحة
st.set_page_config(
    page_title="Lumina AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# إدارة حالة اللغة والجلوس
if 'lang' not in st.session_state:
    st.session_state.lang = 'ar'

if 'gallery_images' not in st.session_state:
    st.session_state.gallery_images = [
        {"title": "Cyberpunk City", "url": "https://image.pollinations.ai/prompt/cyberpunk%20futuristic%20city%20neon%20lights?width=600&height=400"},
        {"title": "Arabian Knight", "url": "https://image.pollinations.ai/prompt/ancient%20arabian%20warrior%20cinematic%20lighting?width=600&height=400"},
        {"title": "Space Explorer", "url": "https://image.pollinations.ai/prompt/astronaut%20discovering%20alien%20planet?width=600&height=400"}
    ]

# اختيار اللغة من القائمة الجانبية
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brain.png", width=70)
    st.title("🌐 Settings / الإعدادات")
    selected_lang = st.selectbox(
        "اللغة / Language",
        options=["العربية", "English"],
        index=0 if st.session_state.lang == 'ar' else 1
    )
    st.session_state.lang = 'ar' if selected_lang == "العربية" else 'en'

t = config.TRANSLATIONS[st.session_state.lang]
is_rtl = (st.session_state.lang == 'ar')

# تصميم الواجهة الأنيق
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Cairo', sans-serif !important;
        direction: {"rtl" if is_rtl else "ltr"};
        text-align: {"right" if is_rtl else "left"};
        background-color: #090d16 !important;
        color: #f1f5f9 !important;
    }}
    
    .main-header {{
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .main-title {{
        font-size: 32px; font-weight: 900;
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px; background: #0f172a; padding: 8px; border-radius: 14px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px; color: #94a3b8 !important; font-weight: 700 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #0072ff 0%, #00c6ff 100%) !important;
        color: #fff !important;
    }}
</style>
""", unsafe_allow_html=True)

# الهيدر الرئيسي
st.markdown(f"""
<div class="main-header">
    <div class="main-title">{t["title"]}</div>
    <div style="color: #94a3b8; font-size: 15px;">{t["subtitle"]}</div>
</div>
""", unsafe_allow_html=True)

# التبويبات الرئيسية
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_chat"], 
    t["tab_studio"], 
    t["tab_images"], 
    t["tab_gallery"]
])

# 1️⃣ تبويب شات الذكاء الاصطناعي (ChatGPT)
with tab1:
    st.subheader(t["tab_chat"])
    user_prompt = st.text_area(t["prompt_label"], height=100, placeholder="مثال: اكتب لي سيناريو فيديو قصير عن أهمية الذكاء الاصطناعي...")
    if st.button(t["generate_btn"], key="chat_btn"):
        if user_prompt.strip():
            with st.spinner("جاري التفكير والتوليد..." if is_rtl else "Thinking..."):
                ai_response = ai_engine.generate_ai_text(user_prompt, st.session_state.lang)
                st.markdown("### 🤖 النتيجة:")
                st.info(ai_response)
        else:
            st.warning("يرجى كتابة نص أولاً!" if is_rtl else "Please enter text first!")

# 2️⃣ تبويب استوديو الفيديوهات
with tab2:
    st.subheader(t["tab_studio"])
    col1, col2 = st.columns(2)
    with col1:
        aspect = st.selectbox(t["aspect_ratio"], ["9:16 (TikTok/Reels)", "16:9 (YouTube)", "1:1 (Instagram)"])
        voice = st.selectbox(t["voice_label"], ["شاكر - وثائقي", "سلمى - حماسي", "حامد - إخباري"])
    with col2:
        proj_name = st.text_input("اسم المشروع:", "فيديو_جديد")
        num_scenes = st.slider("عدد المشاهد:", 1, 5, 2)
    
    st.markdown("---")
    if st.button(t["render_btn"], key="vid_btn"):
        st.success("جاري تجهيز السيرفر لبدء رندر الفيديو..." if is_rtl else "Preparing server for video render...")

# 3️⃣ تبويب توليد الصور بالـ AI
with tab3:
    st.subheader(t["tab_images"])
    img_prompt = st.text_input(t["image_prompt"], placeholder="A futuristic arabic castle in desert, cinematic lighting, 8k resolution")
    
    if st.button(t["generate_img_btn"], key="img_btn"):
        if img_prompt.strip():
            with st.spinner("جاري رسم الصورة بالذكاء الاصطناعي..." if is_rtl else "Generating AI Image..."):
                generated_url = ai_engine.generate_ai_image_url(img_prompt)
                st.image(generated_url, caption=img_prompt, use_column_width=True)
                
                # إضافتها تلقائياً إلى معرض أعمال الزوار
                st.session_state.gallery_images.insert(0, {"title": img_prompt[:30], "url": generated_url})
                st.success("تمت إضافة الصورة بنجاح للمعرض العام!" if is_rtl else "Added to public showcase gallery!")
        else:
            st.warning("يرجى كتابة وصف للصورة!" if is_rtl else "Please enter an image description!")

# 4️⃣ تبويب معرض أعمال الزوار (Public Showcase)
with tab4:
    st.subheader(t["gallery_title"])
    cols = st.columns(3)
    for index, item in enumerate(st.session_state.gallery_images):
        with cols[index % 3]:
            st.image(item["url"], use_column_width=True)
            st.caption(f"🎨 {item['title']}")
