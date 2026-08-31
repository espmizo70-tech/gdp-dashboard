# ai_engine.py - محركات الذكاء الاصطناعي المجانية

import urllib.parse
import requests

def generate_ai_text(prompt: str, lang: str = "ar") -> str:
    """توليد نصوص وأفكار سيناريو مجاناً بالذكاء الاصطناعي"""
    system_instruction = "أنت مساعد ذكاء اصطناعي احترافي لصنع سيناريو فيديوهات قصيرة." if lang == "ar" else "You are a professional AI scriptwriter for short videos."
    full_prompt = f"{system_instruction} {prompt}"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text
        return "حدث خطأ أثناء الاتصال بالسيرفر." if lang == "ar" else "Error connecting to server."
    except Exception as e:
        return f"خطأ: {str(e)}"

def generate_ai_image_url(prompt: str, width: int = 1084, height: int = 1084) -> str:
    """توليد صور فائقة الدقة فوراً وبشكل مجاني عبر روابط مباشرة"""
    encoded_prompt = urllib.parse.quote(prompt)
    # رابط مباشر يتولّد فوراً بالذكاء الاصطناعي (Pollinations AI)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    return image_url

