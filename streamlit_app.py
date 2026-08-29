import streamlit as st
import os
import numpy as np
from PIL import Image, ImageDraw
from gtts import gTTS
from moviepy.editor import ImageClip, CompositeVideoClip, ColorClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips
import arabic_reshaper
from bidi.algorithm import get_display

st.set_page_config(page_title="منصة صناعة الفيديوهات V6", page_icon="🎬", layout="wide")

st.title("🎬 منصة صناعة الفيديوهات V6 - مزامنة النصوص المباشرة")
st.write("عرض كل جملة تلقائياً بالتزامن مع توقيت نطقها في التعليق الصوتي.")

def create_text_image(text, size=(900, 500), text_color="yellow"):
    # تصحيح تباعد واتجاه الأحرف العربية
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    color_rgb = (255, 255, 0, 255) if text_color == "yellow" else (255, 255, 255, 255)
    
    draw.multiline_text(
        (size[0] // 2, size[1] // 2),
        bidi_text,
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
    text_color_choice = st.selectbox("لون النص المتراكب:", ["yellow", "white"])

with col2:
    st.subheader("📝 سكريبت الفيديو")
    default_text = "في أعماق الغابة السحرية، كان هناك سر محبوس.\nرحلة تبحث عن الإجابات المنتظرة.\nاكتشف الحقيقة قبل فوات الأوان."
    user_script = st.text_area("أدخل الجمل (كل جملة في سطر مستقل):", value=default_text, height=180)

if st.button("🚀 إنشاء الفيديو المتزامن الآن", use_container_width=True):
    lines = [line.strip() for line in user_script.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى إدخال نص السكريبت أولاً!")
    else:
        with st.spinner("جاري تقطيع الصوت ورندر المشاهد جملة بجملة..."):
            try:
                sub_clips = []
                audio_clips = []
                temp_files = []

                for i, line in enumerate(lines):
                    # 1. توليد صوت لكل جملة
                    audio_filename = f"temp_voice_{i}.mp3"
                    tts = gTTS(text=line, lang='ar')
                    tts.save(audio_filename)
                    temp_files.append(audio_filename)
                    
                    # 2. احتساب مدة نطق الجملة
                    audio_clip = AudioFileClip(audio_filename)
                    line_duration = audio_clip.duration
                    audio_clips.append(audio_clip)

                    # 3. إنشاء مشهد النص المستقل لهذه الجملة
                    bg_clip = ColorClip(size=(1080, 1920), color=bg_color, duration=line_duration)
                    text_np = create_text_image(line, text_color=text_color_choice)
                    txt_clip = ImageClip(text_np).set_position('center').set_duration(line_duration)
                    
                    combined_sub = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
                    sub_clips.append(combined_sub)

                # 4. دمج كافة المشاهد الصوتية والمرئية بالتسلسل
                final_video = concatenate_videoclips(sub_clips)
                output_path = "final_synced_short.mp4"
                final_video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')

                # تنظيف الملفات المؤقتة
                for clip in audio_clips:
                    clip.close()
                for file_path in temp_files:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                st.success("🎬 تم إنشاء الفيديو المتزامن بنجاح!")
                st.video(output_path)

            except Exception as e:
                st.error(f"حدث خطأ أثناء التوليد: {str(e)}")
