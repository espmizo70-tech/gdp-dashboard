import streamlit as st
import asyncio
import os
import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# استيراد متوافق مع كافة إصدارات MoviePy 1.x و 2.x
try:
    from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips, AudioArrayClip
except ImportError:
    try:
        from moviepy import ImageClip, AudioFileClip, CompositeAudioClip, concatenate_videoclips
        try:
            from moviepy import AudioArrayClip
        except ImportError:
            from moviepy.audio.AudioClip import AudioArrayClip
    except ImportError:
        from moviepy.video.VideoClip import ImageClip
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.audio.AudioClip import CompositeAudioClip, AudioArrayClip
        from moviepy.video.compositing.concatenate import concatenate_videoclips

# دوال توافقية بين MoviePy v1 و MoviePy v2 لمنع AttributeError
def set_duration(clip, d):
    if hasattr(clip, "with_duration"):
        return clip.with_duration(d)
    return clip.set_duration(d)

def set_audio(clip, a):
    if hasattr(clip, "with_audio"):
        return clip.with_audio(a)
    return clip.set_audio(a)

def apply_resize(clip, resize_func):
    if hasattr(clip, "resized"):
        try:
            return clip.resized(resize_func)
        except Exception:
            pass
    if hasattr(clip, "resize"):
        try:
            return clip.resize(resize_func)
        except Exception:
            pass
    return clip

# دعم اللغة العربية
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False

st.set_page_config(page_title="AutoShorts Ultimate Studio V5", page_icon="🔥", layout="wide")

st.title("🔥 استوديو الإنتاج الفائق AutoShorts V5")
st.write("صناعة فيديوهات احترافية كاملة: مشاهد متحركة، موسيقى خلفية، ترجمة ملونة، وعلامة مائية!")

# 1. الشريط الجانبي للإعدادات
st.sidebar.header("⚙️ إعدادات الإنتاج المتقدمة")

channel_watermark = st.sidebar.text_input("🏷️ اسم قناتك (Watermark):", "@MoneyRadar")

voice_option = st.sidebar.selectbox(
    "🎙️ اختر المعلق الصوتي:",
    ("حامد - سعودي (رجالي)", "سلمى - مصري (نسائي)", "ماجد - إماراتي (رجالي)", "منى - قطري (نسائي)")
)

voices_map = {
    "حامد - سعودي (رجالي)": "ar-SA-HamedNeural",
    "سلمى - مصري (نسائي)": "ar-EG-SalmaNeural",
    "ماجد - إماراتي (رجالي)": "ar-AE-MajedNeural",
    "منى - قطري (نسائي)": "ar-QA-MonaNeural"
}

text_color_choice = st.sidebar.selectbox(
    "🎨 لون الترجمة الرئيسي:",
    ("أصفر يوتيوب (Yellow)", "أخضر تيك توك (Neon Green)", "أبيض ساطع (White)")
)

color_map = {
    "أصفر يوتيوب (Yellow)": (255, 220, 0, 255),
    "أخضر تيك توك (Neon Green)": (57, 255, 20, 255),
    "أبيض ساطع (White)": (255, 255, 255, 255)
}

bgm_option = st.sidebar.checkbox("🎵 إضافة موسيقى خلفية حماسية", value=True)

style_prompt = st.sidebar.selectbox(
    "🎨 نمط وجو الصور:",
    ("cinematic, 8k vertical, highly detailed, photorealistic", 
     "3D Pixar style animation, bright colors, vertical format", 
     "dark moody documentary style, ultra realistic",
     "cyberpunk neon style, futuristic 8k vertical")
)

# 2. كتابة السكريبت
st.subheader("📝 سيناريو الفيديو:")

user_script = st.text_area(
    "أدخل جمل السكريبت (كل جملة في سطر مستقل):", 
    value="هل تعلم أن الأهرامات ليست فقط في مصر؟\nالسودان تحتوي على أكثر من 200 هرم أثري مذهل!\nوهي تتفوق عدداً على جميع أهرامات مصر مجتمعة.\nتابعنا للمزيد من المعرفة والمعلومات الشيقة يومياً!",
    height=140
)

# دالة تنسيق النص العربي
def format_arabic_text(text):
    if HAS_ARABIC_SUPPORT:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text

# دالة معالجة الصور وإضافة الترجمة والعلامة المائية
def process_frame(img_path, subtitle_text, watermark_text, output_path):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # مظلل أسفل الشاشة
    banner_height = int(h * 0.22)
    draw.rectangle([0, h - banner_height, w, h], fill=(0, 0, 0, 160))
    
    # رسم العلامة المائية
    if watermark_text:
        wm = format_arabic_text(watermark_text)
        draw.text((int(w * 0.05), int(h * 0.04)), wm, fill=(255, 255, 255, 180))
        
    # رسم الترجمة
    formatted_sub = format_arabic_text(subtitle_text)
    sub_x = int(w * 0.08)
    sub_y = int(h - banner_height + (banner_height * 0.3))
    
    # حدود سوداء للترجمة (Outline)
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (0,-2), (0,2), (-2,0), (2,0)]:
        draw.text((sub_x + dx, sub_y + dy), formatted_sub, fill=(0, 0, 0, 255))
        
    # لون النص
    draw.text((sub_x, sub_y), formatted_sub, fill=color_map[text_color_choice])
    
    final_img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    final_img.save(output_path)

async def generate_voice(text, voice_code, output_audio):
    tts = edge_tts.Communicate(text, voice_code, rate="+10%")
    await tts.save(output_audio)

def fetch_image(prompt, output_img):
    clean_prompt = requests.utils.quote(f"{prompt}, {style_prompt}")
    url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true"
    res = requests.get(url)
    with open(output_img, "wb") as f:
        f.write(res.content)

# إنتاج نغمة خلفية خفيفة تلقائياً
def make_simple_bgm(duration):
    fps = 44100
    t = np.linspace(0, duration, int(fps * duration), False)
    note = 0.03 * np.sin(2 * np.pi * 220 * t) * np.exp(-t % 1)
    audio_array = np.vstack((note, note)).T
    return AudioArrayClip(audio_array, fps=fps)

# 3. زر البدء
if st.button("🚀 إنتاج الفيديو النهائي"):
    sentences = [s.strip() for s in user_script.split("\n") if s.strip()]
    if not sentences:
        st.error("الرجاء كتابة سيناريو يحتوي على نص!")
    else:
        with st.spinner("⚡ جاري إنشاء المشاهد، الصوت، والمؤثرات..."):
            progress_bar = st.progress(0)
            clips = []
            selected_voice = voices_map[voice_option]
            
            for i, sentence in enumerate(sentences):
                st.write(f"🎬 معالجة المشهد {i+1}: `{sentence[:30]}...`")
                
                audio_file = f"voice_{i}.mp3"
                raw_img = f"bg_{i}.jpg"
                final_img = f"processed_bg_{i}.jpg"
                
                asyncio.run(generate_voice(sentence, selected_voice, audio_file))
                fetch_image(sentence, raw_img)
                process_frame(raw_img, sentence, channel_watermark, final_img)
                
                audio_clip = AudioFileClip(audio_file)
                
                # استخدام دوال التوافق
                img_clip = ImageClip(final_img)
                img_clip = set_duration(img_clip, audio_clip.duration)
                img_clip = set_audio(img_clip, audio_clip)
                img_clip = apply_resize(img_clip, lambda t: 1 + 0.07 * (t / audio_clip.duration))
                
                clips.append(img_clip)
                progress_bar.progress((i + 1) / len(sentences))
            
            st.write("🎞️ جاري رندر وتجميع الفيديو مع الموسيقى...")
            try:
                final_video = concatenate_videoclips(clips, method="compose")
            except Exception:
                final_video = concatenate_videoclips(clips)
            
            if bgm_option:
                try:
                    bgm_clip = make_simple_bgm(final_video.duration)
                    combined_audio = CompositeAudioClip([final_video.audio, bgm_clip])
                    final_video = set_audio(final_video, combined_audio)
                except Exception as e:
                    st.warning("تم تصدير الفيديو بالصوت الأصلي.")
                
            final_video.write_videofile("ultimate_autoshort.mp4", fps=24, codec="libx264", audio_codec="aac")
            
            st.success("🎉 تم إنتاج الفيديو السينمائي بنجاح!")
            st.video("ultimate_autoshort.mp4")
