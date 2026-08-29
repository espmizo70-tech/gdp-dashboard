import streamlit as st
import asyncio
import os
import requests
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

st.set_page_config(page_title="AutoShorts Generator", page_icon="🎬")

st.title("🎬 مولد الفيديوهات القصيرة - النسخة المتقدمة")
st.write("قم بتخصيص الصوت والسيناريو لإنشاء فيديو احترافي مجاناً")

# 1. اختيار الصوت
voice_option = st.selectbox(
    "🎙️ اختر المعلق الصوتي:",
    ("حامد - سعودي (رجالي)", "سلمى - مصري (نسائي)", "ماجد - إماراتي (رجالي)", "منى - قطري (نسائي)")
)

# قاموس الأصوات المجانية
voices_map = {
    "حامد - سعودي (رجالي)": "ar-SA-HamedNeural",
    "سلمى - مصري (نسائي)": "ar-EG-SalmaNeural",
    "ماجد - إماراتي (رجالي)": "ar-AE-MajedNeural",
    "منى - قطري (نسائي)": "ar-QA-MonaNeural"
}

# 2. كتابة السكريبت النصي
script_text = st.text_area(
    "📝 أدخل نص الفيديو (السكريبت):", 
    "هل تعلم أن الأهرامات ليست فقط في مصر؟ السودان تحتوي على أهرامات أكثر من مصر بكثير، حيث تضم أكثر من 200 هرم أثري!"
)

button = st.button("🚀 إنشاء الفيديو الآن")

# وظيفة إنشاء الصوت
async def generate_voice(text, voice_code):
    tts = edge_tts.Communicate(text, voice_code)
    await tts.save("voice.mp3")

# وظيفة توليد الصورة
def fetch_image(prompt):
    clean_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true"
    res = requests.get(url)
    with open("bg.jpg", "wb") as f:
        f.write(res.content)

# تنفيذ العمليات
if button:
    with st.spinner("جاري إنشاء الفيديو وتطبيق الصوت المختارات..."):
        selected_voice = voices_map[voice_option]
        
        # أ) تحويل النص لصوت
        asyncio.run(generate_voice(script_text, selected_voice))
        
        # ب) جلب صورة تناسب النص
        fetch_image(f"{script_text[:40]}, vertical 8k cinematic")
        
        # ج) تجميع الفيديو
        audio = AudioFileClip("voice.mp3")
        clip = ImageClip("bg.jpg").set_duration(audio.duration).set_audio(audio)
        clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
        
        st.success("✨ تم إنشاء الفيديو بنجاح!")
        st.video("output.mp4")
