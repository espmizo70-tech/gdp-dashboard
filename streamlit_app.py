import streamlit as st
import requests
import time

st.set_page_config(page_title="Lumina Studio V12", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0f19; color: #f0f4f8; }
    section[data-testid="stSidebar"] { background-color: #111827; }
    .stButton > button {
        background: linear-gradient(135deg, #00c6ff 0%, #0072ff 100%);
        color: white; font-weight: bold; border-radius: 8px; border: none; padding: 12px;
    }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚡ Lumina Studio V12")
    st.markdown("---")
    project_title = st.text_input("اسم المشروع", "فيديو_احترافي_01")
    quality = st.selectbox("جودة الرندر", ["1080p (Full HD)", "4K (Ultra HD)", "720p (Fast)"])
    fps = st.radio("معدل الإطارات (FPS)", [30, 60], horizontal=True)

st.title("🎬 محرر الفيديوهات الذكي")

tab1, tab2, tab3, tab4 = st.tabs(["📐 المقاسات والتصميم", "🎞️ المشاهد والنصوص", "🎙️ الأصوات", "🚀 الرندر"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📐 مقاس الفيديو")
        aspect_ratio = st.selectbox("اختر المقاس:", ["9:16 (TikTok/Reels)", "16:9 (YouTube)", "1:1 (Instagram)", "4:5 (Facebook)"])
        text_position = st.selectbox("موقع الكلمات", ["أسفل الشاشة", "منتصف الشاشة", "أعلى الشاشة"])
        animation = st.selectbox("طريقة عرض الكلمات", ["كلمة بكلمة", "ظهور تدريجي", "آلة كاتبة"])
    with col2:
        st.subheader("🔤 الخطوط والألوان")
        font_family = st.selectbox("نوع الخط العربي", ["Cairo-Bold", "Tajawal-Black", "Almarai-Bold", "Amiri"])
        font_size = st.slider("حجم الخط", 24, 80, 48)
        c1, c2, c3 = st.columns(3)
        with c1: primary_color = st.color_picker("لون النص", "#FFFFFF")
        with c2: highlight_color = st.color_picker("لون التمييز", "#FFD700")
        with c3: stroke_color = st.color_picker("حدود الكلمات", "#000000")

with tab2:
    st.subheader("🎞️ المشاهد")
    num_scenes = st.number_input("عدد المشاهد:", 1, 10, 3)
    scenes_list = []
    for i in range(int(num_scenes)):
        sc_txt = st.text_area(f"الكلام للمشهد {i+1}", f"هذا كليب المشهد {i+1}", key=f"t_{i}")
        sc_dur = st.number_input(f"المدة بالثواني للمشهد {i+1}", 1.0, 30.0, 5.0, key=f"d_{i}")
        scenes_list.append({"scene_index": i+1, "text": sc_txt, "duration": sc_dur})

with tab3:
    st.subheader("🎙️ الصوت والموسيقى")
    voice = st.selectbox("نبرة الصوت:", ["ذكر - وثائقي", "أنثى - إخباري", "ذكر - ودود"])
    speed = st.slider("سرعة النطق:", 0.75, 1.5, 1.0)
    music_vol = st.slider("صوت الموسيقى الخلفية:", 0.0, 0.5, 0.15)

with tab4:
    st.subheader("🚀 استخراج الفيديو")
    if st.button("🚀 بدء استخراج الفيديو"):
        payload = {
            "title": project_title,
            "aspect_ratio": aspect_ratio.split(" ")[0],
            "quality": quality.split(" ")[0],
            "fps": fps,
            "scenes": scenes_list,
            "font_config": {
                "font_family": font_family, "font_size": font_size,
                "primary_color": primary_color, "highlight_color": highlight_color,
                "stroke_color": stroke_color, "position": text_position, "animation": animation
            },
            "audio_config": {"voice_type": voice, "speed": speed, "music_volume": music_vol}
        }
        try:
            res = requests.post("http://localhost:8000/api/v1/generate", json=payload)
            if res.status_code == 200:
                task_id = res.json()["task_id"]
                st.success(f"تم بدء المهمة برقم: `{task_id}`")
                p_bar = st.progress(0)
                status_lbl = st.empty()
                while True:
                    time.sleep(2)
                    st_res = requests.get(f"http://localhost:8000/api/v1/status/{task_id}").json()
                    status_lbl.info(st_res.get("message", ""))
                    p_bar.progress(st_res.get("progress", 0))
                    if st_res.get("status") == "completed":
                        st.balloons()
                        st.success("🎉 اكتمل رندر الفيديو بنجاح!")
                        st.video(st_res["video_url"])
                        break
                    elif st_res.get("status") == "failed":
                        st.error(f"خطأ: {st_res.get('error')}")
                        break
        except Exception as err:
            st.error(f"تأكد من تشغيل FastAPI أولاً! التفاصيل: {err}")
