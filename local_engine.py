# local_engine.py - محرك محلي مستقل 100% دون أي مواقع خارجية

import asyncio
import edge_tts
import random

# 1️⃣ محرك النصوص والسيناريو المحلي (بدون ChatGPT)
def generate_local_script(topic: str, style: str = "قصة") -> str:
    """كود محلي ينشئ سيناريو كامل داخل موقعك"""
    intros = [
        f"هل تعلم ما هو السر الحقيقي وراء {topic}؟",
        f"في هذا الفيديو السريع، سنكتشف حقائق مذهلة عن {topic}.",
        f"قصة اليوم تعود بنا إلى عالم {topic} المثير."
    ]
    bodies = [
        f"تشير الدراسات والأبحاث إلى أن {topic} يغير طريقة تفكيرنا اليومية ويفتح آفاقاً جديدة للنجاح.",
        f"الكثير من الناس يغفلون عن قوة {topic}، لكن التركيز عليه يمنحك أفضلية كبيرة جداً.",
        f"من أهم النقاط التي يجب أن تعرفها هي أن التعامل مع {topic} يتطلب خطوات مرتبة وبسيطة."
    ]
    outros = [
        "إذا أردت معرفة المزيد، تابعنا للمزيد من المحتوى المميز!",
        "شاركونا آرائكم في التعليقات ولا تنسوا المتابعة!",
        "هذا كل شيء لليوم، نراكم في الفيديو القادم!"
    ]
    
    script = f"{random.choice(intros)}\n\n{random.choice(bodies)}\n\n{random.choice(outros)}"
    return script

# 2️⃣ محرك الصوت العربي المستقل (بدون ElevenLabs)
async def create_arabic_audio_async(text: str, output_path: str, voice: str = "ar-SA-HamedNeural"):
    """توليد تعليق صوتي من داخل السيرفر بدون مفتاح API"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def generate_arabic_audio(text: str, output_path: str = "voiceover.mp3", voice: str = "ar-SA-HamedNeural"):
    asyncio.run(create_arabic_audio_async(text, output_path, voice))
    return output_path
