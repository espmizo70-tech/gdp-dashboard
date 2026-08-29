import streamlit as st
import os
from gtts import gTTS
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, AudioFileClip

st.set_page_config(page_title="منصة صناعة الفيديوهات V5 Pro", page_icon="🎬", layout="wide")

st.title("🎬 منصة صناعة الفيديوهات الاحترافية V5 Pro")
st.write("قم بتخصيص السكريبت، الألوان، وأصوات التعليق الصوتي لإنشاء مقاطع Shorts جاهزة للنشر.")

# تقسيم الشاشة إلى عمودين للتحكم والتعديل
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("⚙️ إعدادات الفيديو والتصميم")
    
    # اختيار اللون الخلفي
    bg_color_option = st.selectbox(
        "لون الخلفية:",
        ["كحلي داكن (Dark Navy)", "أسود كلاسيكي (Black)", "عنابي سينمائي (Dark Crimson)"]
    )
    color_map = {
        "كحلي داكن (Dark Navy)": (15, 23, 42),
        "أسود كلاسيكي (Black)": (0, 0, 0),
        "عنابي سينمائي (Dark Crimson)": (45, 10, 20)
    }

    # تخصيص النص
    text_color = st.color_picker("لون النص المتراكب:", "#FFFF00")
    font_size = st.slider("حجم الخط:", min_value=30, max_value=90, value=55)
    
    # خيارات الصوت
    accent = st.selectbox("لهجة التعليق الصوتي (gTTS):", ["العربية الفصحى (عام)", "لهجة إقليمية (السعودية)"])
    tld_val = 'com.sa' if "السعودية" in accent else 'com'

with col2:
    st.subheader("📝 السكريبت والترجمة")
    
    default_text = "في أعماق الغابة السحرية، كان هناك سر محبوس.\nرحلة تبحث عن الإجابات المنتظرة.\nاكتشف الحقيقة قبل فوات الأوان."
    user_script = st.text_area("أدخل جمل السكريبت (كل جملة في سطر مستقل):", value=default_text, height=180)

st.markdown("---")

# زر التوليد والرندر
if st.button("🚀 إنشاء الفيديو الاحترافي الآن", use_container_width=True):
    lines = [line.strip() for line in user_script.split("\n") if line.strip()]
    
    if not lines:
        st.error("يرجى إدخال نص السكريبت أولاً!")
    else:
        with st.spinner("جاري معالجة الصوت، محاذاة النص، ورندر الفيديو..."):
            try:
                full_text = " ".join(lines)
                audio_file = "voice_temp.mp3"
                output_video = "final_short.mp4"
                
                # 1. توليد الصوت
                tts = gTTS(text=full_text, lang='ar', tld=tld_val)
                tts.save(audio_file)
                
                # 2. احتساب التوقيت
                audio_clip = AudioFileClip(audio_file)
                video_duration = audio_clip.duration
                
                # 3. إنشاء الخلفية
                bg_color = color_map[bg_color_option]
                bg_clip = ColorClip(size=(1080, 1920), color=bg_color, duration=video_duration)
                
                # 4. تراكب النص
                txt_clip = TextClip(
                    full_text,
                    fontsize=font_size,
                    color=text_color,
                    font='Arial',
                    method='caption',
                    size=(900, None)
                ).set_position('center').set_duration(video_duration)
                
                # 5. الدمج والتصدير
                final_clip = CompositeVideoClip([bg_clip, txt_clip]).set_audio(audio_clip)
                final_clip.write_videofile(output_video, fps=24, codec='libx264', audio_codec='aac')
                
                # تنظيف الصوت
                audio_clip.close()
                if os.path.exists(audio_file):
                    os.remove(audio_file)

                st.success("🎬 تم رندر الفيديو بنجاح!")
                st.video(output_video)

            except Exception as e:
                st.error(f"حدث خطأ أثناء الإنشاء: {str(e)}")
