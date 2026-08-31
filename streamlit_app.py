import streamlit as st

st.title("🎙️ استوديو اختيار الأصوات والخطوط المتحركة")

# 1. قسم اختيار الأصوات مع الاستماع التجريبي
st.subheader("1. اختر الصوت المناسب")

col1, col2 = st.columns([3, 1])

with col1:
    voice_option = st.selectbox(
        "اختر المعلق الصوتي:",
        ["عمر - صوت عربي احترافي", "سارة - صوت عربي حماسي", "Alex - English Natural"]
    )

with col2:
    st.write("معاينة الصوت:")
    # زر الاستماع قبل الاختيار
    if voice_option == "عمر - صوت عربي احترافي":
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3") # رابط صوت تجريبي
    elif voice_option == "سارة - صوت عربي حماسي":
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3")

# 2. قسم حركات الكتابة على الفيديو (Subtitles)
st.subheader("2. طريقة ظهور النصوص على الفيديو")

animation_style = st.radio(
    "اختر حركة النصوص:",
    [
        "✨ ظهور كلمة بكلمة (Word-by-Word Pop)", 
        "⌨️ آلة كاتبة (Typewriter)", 
        "💬 نص ثابت بأسفل الشاشة (Static Subtitle)"
    ]
)

# 3. اختيار اللغة
language = st.selectbox("لغة الفيديو والنصوص:", ["العربية", "English"])

if st.button("تأكيد الاختيارات وتوليد الفيديو 🚀"):
    st.success(f"تم اختيار الصوت: {voice_option} مع تأثير: {animation_style}")
