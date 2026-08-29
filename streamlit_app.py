import streamlit as st
import asyncio
import os
import requests
import edge_tts
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# استيراد دعم اللغة العربية المتقدم
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    HAS_ARABIC_SUPPORT = True
except ImportError:
    HAS_ARABIC_SUPPORT = False

st.set_page_config(page_title="AutoShorts Ultra Pro Studio", page_icon="🎬", layout="wide")

st.title("🎬 منصة صناعة الفيديوهات الاحترافية V4")
st.write("اصنع فيديوهات قصيرة بنمط سينمائي، مشاهد متحركة، نصوص مظهرة، وعلامة مائية مجاناً بالكامل!")

# 1. القائمة الجانبية - التحكم بالصوت والعلامة المائية
st.sidebar.header("⚙️ إعدادات الإنتاج")

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

voice_speed = st.sidebar.select_slider(
    "⚡ سرعة الحديث (TikTok Style):",
    options=["عادي (+0%)", "سريع (+10%)", "سريع جداً (+20%)"],
    value="سريع (+10%)"
)

speed_rates = {
    "عادي (+0%)": "+0%",
    "سريع (+10%)": "+10%",
    "سريع جداً (+20%)": "+20%"
}

style_prompt = st.sidebar.selectbox(
    "🎨 نمط وجو الصور:",
    ("cinematic, 8k vertical, highly detailed, photorealistic", 
     "3D Pixar style animation, bright colors, vertical format", 
     "dark moody documentary style, ultra realistic, cinematic lighting",
     "cyberpunk neon style, futuristic 8k vertical")
)

# 2. سكريبتات جاهزة سريعة
st.subheader("📝 كتابة سكريبت الفيديو:")

template_choice = st.selectbox(
    "💡 اختر نمط سكريبت جاهز (أو اكتب سكريبت خاص بك بالأسفل):",
    ("مخصص (اكتب سكريبتك الخاص)", "حقائق عن الأهرامات", "سر من أسرار الثراء", "معلومة عن الفضاء")
)

default_scripts = {
    "حقائق عن الأهرامات": "هل تعلم أن الأهرامات ليست فقط في مصر؟\nالسودان تحتوي على أكثر من 200 هرم أثري مذهل!\nوهي تتفوق عدداً على جميع أهرامات مصر مجتمعة.\nاشترك في القناة للمزيد من الحقائق يومياً!",
    "سر من أسرار الثراء": "أصحاب الملايين لا يعتمدون على مصدر دخل واحد فقط.\nالدراسات تؤكد أن المعدل هو 7 مصادر دخل مختلفة.\nالاستثمار والتجارة الإلكترونية هي مفتاح الحرية المالية.\nتابعنا لتعلم أسرار المال والنجاح!",
    "معلومة عن الفضاء": "هل تعلم أن اليوم الواحد على كوكب الزهرة أطول من سنته الكاملة؟\nيدور الزهرة حول نفسه ببطء شديد جداً.\nبينما يكمل دورته حول الشمس في وقت أقصر!\nسبحان الله، عالم الفضاء مليء بالغرائب."
}

if template_choice != "مخصص (اكتب سكريبتك الخاص)":
    initial_text = default_scripts[template_choice]
else:
    initial_text = "اكتب الجملة الأولى هنا\nاكتب الجملة الثانية هنا\nاكتب الجملة الثالثة هنا"

user_script = st.text_area("أدخل جمل السكريبت (كل جملة في سطر مستقل):", value=initial_text, height=140)

# دالة إعادة تشكيل النص العربي
def format_arabic_text(text):
    if HAS_ARABIC_SUPPORT:
        reshaped = arabic_reshaper.reshape(text)
        return get_display(reshaped)
    return text

# دالة رسم النصوص والعلامة المائية
def process_frame(img_path, subtitle_text, watermark_text, output_path):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    
    overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # مظلل أسفل الشاشة للترجمة
    banner_height = int(h * 0.22)
    draw.rectangle([0, h - banner_height, w, h], fill=(0, 0, 0, 160))
    
    # رسم العلامة المائية في الأعلى
    if watermark_text:
        wm = format_arabic_text(watermark_text)
        draw.text((int(w * 0.05), int(h * 0.05)), wm, fill=(255, 255, 255, 180))
        
    # رسم النص في أسفل المشهد
    formatted_sub = format_arabic_text(subtitle_text)
    sub_x = int(w * 0.08)
    sub_y = int(h - banner_height + (banner_height * 0.3))
    
    # إضافة حدود سوداء حول النص (Outline Effect)
    for dx, dy in [(-2,-2), (-2,2), (2,-2), (2,2), (0,-2), (0,2), (-2,0), (2,0)]:
        draw.text((sub_x + dx, sub_y + dy), formatted_sub, fill=(0, 0, 0, 255))
        
    # النص الرئيسي باللون الأصفر الفاقع
    draw.text((sub_x, sub_y), formatted_sub, fill=(255, 220, 0, 255))
    
    final_img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    final_img.save(output_path)

# دالة إنشاء التعليق الصوتي مع التحكم بالسرعة
async def generate_voice(text, voice_code, rate, output_audio):
    tts = edge_tts.Communicate(text, voice_code, rate=rate)
    await tts.save(output_audio)

# دالة جلب الصورة
def fetch_image(prompt, output_img):
    clean_prompt = requests.utils.quote(f"{prompt}, {style_prompt}")
    url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1920&nologo=true"
    res = requests.get(url)
    with open(output_img, "wb") as f:
        f.write(res.content)

# تطبيق تأثير الزوم المبتكر (Ken Burns Effect)
def create_zoom_clip(img_path, duration):
    img_clip = ImageClip(img_path).set_duration(duration)
    # تأثير تكبير ناعم جداً من 100% إلى 108%
    return img_clip.resize(lambda t: 1 + 0.08 * (t / duration))

# 3. زر التنفيذ التلقائي
if st.button("🚀 إنشاء الفيديو السينمائي الآن"):
    sentences = [s.strip() for s in user_script.split("\n") if s.strip()]
    if not sentences:
        st.error("الرجاء كتابة سيناريو يحتوي على نص!")
    else:
        with st.spinner("⚡ جاري إنتاج المشاهد الاحترافية وتطبيق المؤثرات الصوتية والبصرية..."):
            progress_bar = st.progress(0)
            clips = []
            selected_voice = voices_map[voice_option]
            selected_rate = speed_rates[voice_speed]
            
            for i, sentence in enumerate(sentences):
                st.write(f"🎬 معالجة المشهد {i+1} من {len(sentences)}: `{sentence[:35]}...`")
                
                audio_file = f"voice_{i}.mp3"
                raw_img = f"bg_{i}.jpg"
                final_img = f"processed_bg_{i}.jpg"
                
                # إنشاء الصوت والصورة وتطبيق الشعار والترجمة
                asyncio.run(generate_voice(sentence, selected_voice, selected_rate, audio_file))
                fetch_image(sentence, raw_img)
                process_frame(raw_img, sentence, channel_watermark, final_img)
                
                # إنشاء مقطع الصورة مع الزوم والصوت
                audio_clip = AudioFileClip(audio_file)
                clip = create_zoom_clip(final_img, audio_clip.duration).set_audio(audio_clip)
                clips.append(clip)
                
                progress_bar.progress((i + 1) / len(sentences))
            
            # دمج الفيديو
            st.write("🎞️ جاري تجميع المشاهد في فيديو نهائي عالي الجودة...")
            final_video = concatenate_videoclips(clips, method="compose")
            final_video.write_videofile("ultra_autoshort.mp4", fps=24, codec="libx264", audio_codec="aac")
            
            st.success("🎉 تم إنشاء الفيديو بنجاح بأعلى دقة واحترافية!")
            st.video("ultra_autoshort.mp4")
