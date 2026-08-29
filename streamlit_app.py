import streamlit as st
import asyncio
import os
import requests
import edge_tts
from PIL import Image, ImageDraw
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

st.set_page_config(page_title="AutoShorts Pro Studio", page_icon="🎬", layout="wide")

st.title("🚀 مولد الفيديوهات الاحترافي - مشاهد متعددة")
st.write("اصنع فيديو قصير بنمط Reels / TikTok بمشاهد وصور متغيرة مع كل جملة مجاناً!")

# 1. القائمة الجانبية للإعدادات
st.sidebar.header("⚙️ إعدادات الصوت والأسلوب")
voice_option = st.sidebar.selectbox(
    "🎙️ اختر صوت المعلق:",
    ("حامد - سعودي (رجالي)", "سلمى - مصري (نسائي)", "ماجد - إماراتي (رجالي)", "منى - قطري (نسائي)")
)

voices_map = {
    "حامد - سعودي (رجالي)": "ar-SA-HamedNeural",
    "سلمى - مصري (نسائي)": "ar-EG-SalmaNeural",
    "ماجد - إماراتي (رجالي)": "ar-AE-MajedNeural",
    "منى - قطري (نسائي)": "ar-QA-MonaNeural"
}

style_prompt = st.sidebar.selectbox(
    "🎨 نمط الصور والفن:",
    ("cinematic, 8k vertical, realistic", "3D cartoon animation style, Pixar style", "dark moody documentary style", "cyberpunk neon style")
)

# 2. كتابة السكريبت
st.subheader("📝 اكتب سيناريو الفيديو (كل جملة في سطر مستقل):")
user_script = st.text_area(
    "أدخل جمل السكريبت:",
    value="هل تعلم أن الأهرامات ليست فقط في مصر؟\nالسودان تحتوي على أكثر من 200 هرم أثري مذهل!\nوهي تتفوق عدداً على جميع أهرامات مصر مجتمعة.\nتابعنا للمزيد من المعرفة والمعلومات الشيقة يومياً!",
    height=150
)

# دالة تحسين الصورة وإضافة مظلل للترجمة
def process_image(img_path, output_path):
    img = Image.open(img_path).convert("RGB")
    width, height = img.size
    
    # إضافة شريط ناعم شفاف في الأسفل لزيادة الاحترافية
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    banner_height = int(height * 0.22)
    overlay_draw.rectangle([0, height - banner_height, width, height], fill=(0, 0, 0, 140))
    
    final_img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    final_img.save(output_path)

# دالة توليد الصوت
async def generate_voice(text, voice_code, output_audio):
    tts = edge_tts.Communicate(text, voice_code)
    await tts.save(output_audio)

# دالة جلب الصورة
def fetch_image(prompt, output_img):
    clean_prompt = requests.utils.quote(f"{prompt}, {style_prompt}")
    url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true"
    res = requests.get(url)
    with open(output_img, "wb") as f:
        f.write(res.content)

# زر البدء والتجميع
if st.button("🚀 إنشاء الفيديو متعدد المشاهد الآن"):
    sentences = [s.strip() for s in user_script.split("\n") if s.strip()]
    if not sentences:
        st.error("الرجاء كتابة نص واحد على الأقل!")
    else:
        with st.spinner("جاري تصميم المشاهد، توليد الأصوات، وتجميع الفيديو النهائي..."):
            progress_bar = st.progress(0)
            clips = []
            selected_voice = voices_map[voice_option]
            
            for i, sentence in enumerate(sentences):
                st.write(f"⏳ جاري إنشاء المشهد {i+1} من {len(sentences)}: `{sentence[:30]}...`")
                
                audio_file = f"voice_{i}.mp3"
                raw_img = f"bg_{i}.jpg"
                final_img = f"processed_bg_{i}.jpg"
                
                # إنشاء الصوت والصورة لكل مشهد
                asyncio.run(generate_voice(sentence, selected_voice, audio_file))
                fetch_image(sentence, raw_img)
                process_image(raw_img, final_img)
                
                # إنشاء المقطع البصري والصوتي للمشهد
                audio_clip = AudioFileClip(audio_file)
                img_clip = ImageClip(final_img).set_duration(audio_clip.duration).set_audio(audio_clip)
                clips.append(img_clip)
                
                progress_bar.progress((i + 1) / len(sentences))
            
            # دمج جميع المشاهد في فيديو واحد
            st.write("🎬 جاري رندر وتصدير الفيديو النهائي...")
            final_video = concatenate_videoclips(clips, method="compose")
            final_video.write_videofile("final_autoshorts.mp4", fps=24, codec="libx264", audio_codec="aac")
            
            st.success("🎉 تم إنشاء الفيديو متعدد المشاهد بنجاح!")
            st.video("final_autoshorts.mp4")
