import streamlit as st
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip

st.set_page_config(page_title="منصة صناعة الفيديوهات V5 Pro", page_icon="🎬", layout="wide")

st.title("🎬 منصة صناعة الفيديوهات الاحترافية V5 Pro")
st.write("قم بتخصيص السكريبت والألوان لإنشاء مقاطع Shorts جاهزة بدون مشاكل رندر.")

# دالة إنشاء صورة النص الشفافة بديل ImageMagick
def create_text_image(text, size=(900, 500), font_size=50, text_color="yellow"):
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # تحويل اسم اللون لتركيب RGB
    color_rgb = (255, 255, 0, 255) if text_color == "yellow" else (255, 255, 255, 255)
    
    # رسم النص في المنتصف
    draw.multiline_text(
        (size[0] // 2, size[1] // 2),
        text,
        fill=color_rgb,
        anchor="mm",
        align="center"
    )
    return np.array(img)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ إعدادات التصميم")
    bg_option = st.selectbox("لون الخلفية:", ["كحلي داكن", "أسود كلاسيكي"])
    bg_color = (15, 23, 42) if bg_option == "كحلي داكن" else (0, 0, 0)
    
    text_color_choice = st.selectbox("لون النص:", ["yellow", "white"])

with col2:
    st.subheader("📝 السكريبت")
    default_text = "في أعماق الغابة السحرية، كان هناك سر محبوس.\nرحلة تبحث عن الإجابات المنتظرة.\nاكتشف الحقيقة قبل فوات الأوان."
    user_script = st.text_area("أدخل جمل السكريبت:", value=default_text, height=180)

if st.button("🚀 إنشاء الفيديو الاحترافي الآن", use_container_width=True):
    lines = [line.strip() for line in user_script.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى إدخال السكريبت أولاً!")
    else:
        with st.spinner("جاري معالجة الصوت ورندر الفيديو..."):
            try:
                full_text = "\n".join(lines)
                audio_file = "voice_temp.mp3"
                output_video = "final_short.mp4"
                
                # 1. توليد الصوت
                tts = gTTS(text=" ".join(lines), lang='ar')
                tts.save(audio_file)
                
                # 2. احتساب التوقيت
                audio_clip = AudioFileClip(audio_file)
                video_duration = audio_clip.duration
                
                # 3. خلفية الفيديو (1080x1920)
                bg_clip = ColorClip(size=(1080, 1920), color=bg_color, duration=video_duration)
                
                # 4. تراكب النص باستخدام PIL (تجاوز ImageMagick)
                text_np = create_text_image(full_text, text_color=text_color_choice)
                txt_clip = ImageClip(text_np).set_position('center').set_duration(video_duration)
                
                # 5. التصدير النهائي
                final_clip = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
                final_clip.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac')
                
                audio_clip.close()
                if os.path.exists(audio_file):
                    os.remove(audio_file)

                st.success("🎬 تم رندر الفيديو بنجاح!")
                st.video(output_video)

            except Exception as e:
                st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
