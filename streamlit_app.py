import streamlit as st
import local_engine

st.set_page_config(page_title="Lumina Studio", page_icon="🎬", layout="wide")

# تصميم خاص وأنيق للموقع
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
    * { font-family: 'Cairo', sans-serif !important; }
    .main-box {
        background: #0f172a;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #1e293b;
        margin-bottom: 20px;
    }
    .title-text { color: #00f2fe; font-size: 26px; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-box">
    <div class="title-text">🎬 استوديو لومينا المستقل لصنع المحتوى</div>
    <div style="color: #94a3b8;">منصة خاصة 100% - تعمل داخلياً بدون الحاجة لاشتراكات أو مواقع خارجية</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 مولد النصوص المحلي", "🎙️ المعلق الصوتي الداخلي"])

# 1️⃣ توليد سيناريو محلي
with tab1:
    st.subheader("📝 كتابة سيناريو تلقائي من السيرفر")
    topic_input = st.text_input("موضوع الفيديو:", placeholder="مثال: الذكاء الاصطناعي، النجاح، صناعة الفيديو")
    
    if st.button("توليد النص محلياً 🚀"):
        if topic_input:
            script = local_engine.generate_local_script(topic_input)
            st.success("تم توليد النص بنجاح من داخل موقعك:")
            st.text_area("النص الناتج:", script, height=150)
        else:
            st.warning("يرجى كتابة موضوع أولاً!")

# 2️⃣ توليد صوت محلي
with tab2:
    st.subheader("🎙️ تحويل النص إلى صوت عربي واقعي")
    text_to_speak = st.text_area("أدخل النص المراد تحويله لصوت:", "مرحباً بكم في موقعنا المستقل لصنع الفيديوهات والصوتيات.")
    
    voice_option = st.selectbox("اختر المعلق الصوتي:", [
        "حامد - سعودي (ar-SA-HamedNeural)",
        "سلمى - مصري (ar-EG-SalmaNeural)",
        "شاكر - عماني (ar-OM-ShakirNeural)"
    ])
    
    # استخراج رمز الصوت
    voice_code = voice_option.split("(")[1].replace(")", "").strip()
    
    if st.button("إنشاء الملف الصوتي 🎧"):
        if text_to_speak:
            with st.spinner("جاري معالجة الصوت داخل السيرفر..."):
                audio_file = local_engine.generate_arabic_audio(text_to_speak, "output.mp3", voice_code)
                st.audio(audio_file, format="audio/mp3")
                st.success("تم إنشاء الصوت بنجاح بدون الاستعانة بأي موقع خارجي!")
