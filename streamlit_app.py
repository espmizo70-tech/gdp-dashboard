import streamlit as st
import asyncio
import os
import requests
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip

st.title("🎬 مولد الفيديوهات القصيرة التلقائي")

topic = st.text_input("موضوع الفيديو:", "حقائق غريبة عن المحيطات")
button = st.button("إنشاء الفيديو الآن")

async def generate_voice(text):
    tts = edge_tts.Communicate(text, "ar-SA-HamedNeural")
    await tts.save("voice.mp3")

def fetch_image(prompt):
    url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}?width=1080&height=1920&nologo=true"
    res = requests.get(url)
    with open("bg.jpg", "wb") as f:
        f.write(res.content)

if button:
    with st.spinner("جاري إنشاء الفيديو..."):
        asyncio.run(generate_voice(topic))
        fetch_image(f"{topic}, vertical 8k")
        audio = AudioFileClip("voice.mp3")
        clip = ImageClip("bg.jpg").set_duration(audio.duration).set_audio(audio)
        clip.write_videofile("output.mp4", fps=24, codec="libx264", audio_codec="aac")
        st.success("تم إنشاء الفيديو بنجاح!")
        st.video("output.mp4")
