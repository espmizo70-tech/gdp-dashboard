from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uuid
import os
import time

app = FastAPI(title="Lumina AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = "rendered_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/videos", StaticFiles(directory=OUTPUT_DIR), name="videos")

class FontConfig(BaseModel):
    font_family: str
    font_size: int
    primary_color: str
    highlight_color: str
    stroke_color: str
    position: str
    animation: str

class AudioConfig(BaseModel):
    voice_type: str
    speed: float
    music_volume: float

class SceneItem(BaseModel):
    scene_index: int
    text: str
    duration: float

class VideoRenderRequest(BaseModel):
    title: str
    aspect_ratio: str
    quality: str
    fps: int
    scenes: List[SceneItem]
    font_config: FontConfig
    audio_config: AudioConfig

tasks_db = {}

def render_video_task(task_id: str, req: VideoRenderRequest):
    try:
        tasks_db[task_id] = {"status": "processing", "progress": 20, "message": f"تطبيق مقاس الشاشة {req.aspect_ratio}..."}
        time.sleep(3)
        tasks_db[task_id] = {"status": "processing", "progress": 60, "message": f"مزامنة النصوص بخط {req.font_config.font_family}..."}
        time.sleep(4)
        tasks_db[task_id] = {"status": "processing", "progress": 90, "message": f"استخراج الفيديو بجودة {req.quality}..."}
        time.sleep(3)

        file_name = f"{task_id}_{req.title}.mp4"
        file_path = os.path.join(OUTPUT_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(b"Rendered High-Quality Video File Content")

        video_url = f"http://localhost:8000/videos/{file_name}"
        tasks_db[task_id] = {
            "status": "completed",
            "progress": 100,
            "message": "تم استخراج الفيديو بنجاح!",
            "video_url": video_url
        }
    except Exception as e:
        tasks_db[task_id] = {"status": "failed", "error": str(e)}

@app.post("/api/v1/generate")
async def generate_video(req: VideoRenderRequest, bg_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())[:8]
    tasks_db[task_id] = {"status": "queued", "progress": 0, "message": "تم استلام الطلب..."}
    bg_tasks.add_task(render_video_task, task_id, req)
    return {"status": "success", "task_id": task_id}

@app.get("/api/v1/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")
    return tasks_db[task_id]
