# في التبويب الرابع داخل app.py
if st.button("🚀 بدء استخراج الفيديو الآن (Start Rendering)"):
    # 1. تجهيز البيانات
    payload = {
        "title": project_title,
        "aspect_ratio": aspect_ratio.split(" ")[0],
        "quality": output_quality,
        "fps": fps_choice,
        "font_style": {
            "font_family": font_family,
            "font_size": font_size,
            "primary_color": text_color,
            "highlight_color": highlight_color,
            "stroke_color": stroke_color,
            "position": text_position,
            "animation": animation_style
        },
        "audio_config": {
            "voice": voice_gender,
            "speed": voice_speed,
            "music_volume": music_volume
        },
        "scenes_count": len(scenes_data)
    }

    try:
        # 2. إرسال الطلب إلى FastAPI
        response = requests.post("http://localhost:8000/api/v1/generate-video", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            task_id = data["task_id"]
            st.success(f"تم إرسال المهمة بنجاح! رقم المهمة: `{task_id}`")
            
            # 3. شريط تتبع التقدم التفاعلي (Polling Status)
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            while True:
                time.sleep(2) # فحص الحالة كل ثانيتين
                status_res = requests.get(f"http://localhost:8000/api/v1/task-status/{task_id}")
                status_data = status_res.json()
                
                status_text.info(f"الحالة: {status_data.get('message', '')}")
                progress_bar.progress(status_data.get('progress', 0))
                
                if status_data.get("status") == "completed":
                    st.success("🎉 اكتمل رندر الفيديو بنجاح!")
                    st.video(status_data["video_url"])
                    st.download_button("📥 تحميل الفيديو النهائي", data=requests.get(status_data["video_url"]).content, file_name=f"{project_title}.mp4")
                    break
                elif status_data.get("status") == "failed":
                    st.error(f"حدث خطأ أثناء المعالجة: {status_data.get('error')}")
                    break
        else:
            st.error("فشل الاتصال بسيرفر FastAPI.")

    except Exception as e:
        st.error(f"تأكد من تشغيل سيرفر FastAPI أولاً! التفاصيل: {e}")
