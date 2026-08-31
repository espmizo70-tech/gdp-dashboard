# ai_engine.py - محركات الذكاء الاصطناعي مع الترجـمة التلقائية للصور

import urllib.parse
import requests

def generate_ai_text(prompt: str, lang: str = "ar") -> str:
    """توليد نصوص وأفكار بالذكاء الاصطناعي مجاناً"""
    system_instruction = "أنت مساعد ذكاء اصطناعي احترافي لصنع السيناريو والمحتوى." if lang == "ar" else "You are a professional AI content assistant."
    full_prompt = f"{system_instruction}\n\n{prompt}"
    
    encoded_prompt = urllib.parse.quote(full_prompt)
    url = f"https://text.pollinations.ai/{encoded_prompt}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text
        return "حدث خطأ أثناء الاتصال بالسيرفر." if lang == "ar" else "Error connecting to server."
    except Exception as e:
        return f"خطأ: {str(e)}"

def generate_ai_image_url(prompt: str, width: int = 1024, height: int = 1024) -> str:
    """ترجمة الوصف العربي إلى إنجليزي تلقائياً لتوليد الصورة الصحيحة 100%"""
    english_prompt = prompt
    
    # ترجمة النص إلى الإنجليزية في الخلفية ليفهمه نموذج الصور
    try:
        trans_query = f"Translate this image description into concise English for AI generator, return ONLY English text: {prompt}"
        trans_url = f"https://text.pollinations.ai/{urllib.parse.quote(trans_query)}"
        res = requests.get(trans_url, timeout=6)
        if res.status_code == 200 and res.text.strip():
            english_prompt = res.text.strip()
    except Exception:
        pass  # في حال تعثر الترجمة يستخدم النص الأصلي

    encoded_prompt = urllib.parse.quote(english_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true"
    return image_url
